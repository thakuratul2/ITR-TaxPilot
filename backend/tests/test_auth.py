"""Tests for user registration, authentication, JWT tokens, and security utilities."""

from datetime import timedelta

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.db.base import Base
from app.db.session import get_db
from app.main import app


def test_password_hashing_and_verification():
    """Verify bcrypt hash generation and validation."""
    pwd = "SecureTaxPassword123!"
    hashed = get_password_hash(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_creation_and_decoding():
    """Verify JWT access token creation and payload decoding."""
    user_id = "user-12345-uuid"
    email = "taxpayer@taxpilot.in"
    token = create_access_token(subject=user_id, email=email, expires_delta=timedelta(hours=1))

    assert isinstance(token, str)
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["email"] == email


def test_jwt_decode_invalid_token():
    """Verify that malformed or forged tokens decode to None."""
    assert decode_access_token("invalid.token.payload") is None
    assert decode_access_token("") is None


@pytest_asyncio.fixture
async def test_db_session():
    """Create an isolated test engine and session with in-memory SQLite."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_auth_registration_and_login_flow(test_db_session: AsyncSession):
    """Test full registration, login, profile fetch, and logout lifecycle."""
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Register a new user
            test_email = "atul.singh@example.com"
            reg_payload = {
                "email": test_email,
                "password": "StrongPassword999!",
                "full_name": "Atul Pratap Singh",
            }
            res = await client.post("/api/v1/auth/register", json=reg_payload)
            assert res.status_code == 201
            data = res.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert data["user"]["email"] == test_email
            token = data["access_token"]

            # 2. Duplicate registration attempt
            dup_res = await client.post("/api/v1/auth/register", json=reg_payload)
            assert dup_res.status_code == 400

            # 3. Successful Login
            login_res = await client.post(
                "/api/v1/auth/login",
                json={"email": test_email, "password": "StrongPassword999!"},
            )
            assert login_res.status_code == 200
            login_data = login_res.json()
            assert "access_token" in login_data

            # 4. Failed Login (Wrong password)
            bad_login = await client.post(
                "/api/v1/auth/login",
                json={"email": test_email, "password": "WrongPassword!"},
            )
            assert bad_login.status_code == 401

            # 5. Access /me endpoint with token
            me_res = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert me_res.status_code == 200
            assert me_res.json()["email"] == test_email
            assert me_res.json()["full_name"] == "Atul Pratap Singh"

            # 6. Access /me endpoint with invalid/missing token
            unauth_res = await client.get("/api/v1/auth/me")
            assert unauth_res.status_code == 401
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_auth_logout_endpoint():
    """Verify logout endpoint returns 200 OK."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/v1/auth/logout")
        assert res.status_code == 200
        assert "Successfully logged out" in res.json()["message"]
