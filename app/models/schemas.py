from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


def individual_data(log):
    return {
        "id": str(log["_id"]),
        "content": log["content"],
        "filename": log.get("filename"),
        "status": log.get("status"),
        "suspicious": log.get("suspicious", False)
    }


def all_tasks(logs):
    return [individual_data(log) for log in logs]


class LogUpdateModel(BaseModel):
    status : Optional[str] = None
    suspicious : Optional[bool] = None
    notes : Optional[str] = None


class UserCreate(BaseModel):
    username: str = Field(..., min_length=5, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime


def user_serializer(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "role": user.get("role", "user"),
        "is_active": user.get("is_active", True),
        "created_at": user["created_at"],
    }


