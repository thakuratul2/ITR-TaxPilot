"""Pydantic schemas for user authentication and authorization."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Payload for user signup/registration."""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password with minimum 6 characters")
    full_name: str | None = Field(default=None, max_length=255)


class UserLoginRequest(BaseModel):
    """Payload for user sign-in."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    """Public user profile response."""
    id: str
    email: str
    full_name: str | None = None
    is_active: bool = True
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class AuthTokenResponse(BaseModel):
    """JWT response wrapper with user profile."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
