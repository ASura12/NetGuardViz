from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Shared Base Fields
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(BaseModel):
    username: str = Field(..., min_length = 5 ,max_length = 50)
    email : EmailStr
    password: str = Field(..., min_length=8, max_length=72)

# Safe Public Response
class UserPublic(BaseModel):
    id : str
    username : str
    email: EmailStr
    is_active: bool
    created_at: datetime



# Database Representation (Internal Use)
class UserInDB(UserBase):
    id: Optional[str] = None
    hashed_password: str
    role: str = "user"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)



def user_serializer(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "is_active": user["is_active"],
        "created_at": user["created_at"]
    }

class Userlogin(BaseModel):
    email: EmailStr
    password: str

