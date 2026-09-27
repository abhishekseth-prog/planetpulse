from datetime import datetime
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="User full name")
    email: str = Field(..., max_length=254, description="User email address")
    password: str = Field(..., min_length=10, max_length=128, description="Password (at least 10 chars)")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        name = v.strip()
        if len(name) < 2:
            raise ValueError("Name must contain at least 2 characters")
        return name

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        normalized = v.strip().lower()
        if len(normalized) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", normalized):
            raise ValueError("Enter a valid email address")
        return normalized


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=254, description="User email address")
    password: str = Field(..., min_length=1, max_length=128, description="Password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        normalized = v.strip().lower()
        if len(normalized) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", normalized):
            raise ValueError("Enter a valid email address")
        return normalized


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
