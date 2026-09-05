"""Security utilities: password hashing, JWT generation, and token verification."""

import re
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()

# Default algorithm and secret key
JWT_SECRET_KEY = getattr(settings, "JWT_SECRET_KEY", "taxpilot-super-secret-production-key-change-in-env-123456789")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def generate_request_id() -> str:
    """Generate a unique random request ID."""
    return f"req_{uuid.uuid4().hex[:12]}"


def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded filename to prevent directory traversal and special character exploits."""
    clean_name = filename.replace("\\", "/").rstrip("/").split("/")[-1]
    clean_name = re.sub(r"[^\w\.\-\s]", "_", clean_name)
    return clean_name or f"upload_{uuid.uuid4().hex[:8]}.pdf"


def mask_pan(pan: str | None, style: str = "middle") -> str:
    """Mask 10-character PAN.
    - style='middle': ABCDE****F
    - style='prefix': XXXXX1234A or XXXXX1234X
    """
    if not pan or len(pan.strip()) < 5:
        return "XXXXX1234X"
    clean = pan.strip().upper()
    if len(clean) == 10:
        if style == "prefix":
            return f"XXXXX{clean[5:]}"
        return f"{clean[:5]}****{clean[-1]}"
    if style == "prefix":
        return f"XXXXX{clean[-4:]}"
    return f"{clean[:3]}****{clean[-1]}"


def mask_aadhaar(aadhaar: str | None) -> str:
    """Mask 12-digit Aadhaar number: XXXX-XXXX-1234."""
    if not aadhaar:
        return "XXXX-XXXX-XXXX"
    digits = re.sub(r"\D", "", str(aadhaar))
    if len(digits) == 12:
        return f"XXXX-XXXX-{digits[-4:]}"
    return "XXXX-XXXX-XXXX"


def mask_email(email: str | None) -> str:
    """Mask email address: j***n@example.com."""
    if not email or "@" not in email:
        return "u***r@domain.com"
    parts = email.strip().split("@")
    user, domain = parts[0], parts[1]
    if len(user) <= 2:
        masked_user = user[0] + "*"
    else:
        masked_user = f"{user[0]}{'*' * (len(user) - 2)}{user[-1]}"
    return f"{masked_user}@{domain}"


class TokenPayload(BaseModel):
    """Decoded JWT payload model."""
    sub: str
    email: str
    exp: int


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Generate bcrypt hash for a plaintext password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(
    subject: str,
    email: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: dict[str, Any] = {
        "sub": subject,
        "email": email,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(UTC).timestamp()),
    }

    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except (jwt.PyJWTError, Exception):
        return None
