from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from app.models.user import UserRole


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.DOCTOR


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    username: str
    password: str
