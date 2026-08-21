from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    full_name: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="User full name",
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="User password",
    )


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str