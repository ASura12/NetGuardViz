from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.models.schemas import UserCreate, UserPublic
from app.auth.hashing import hash_password
from app.core.database import users_collection
from app.core.config import ADMIN_EMAILS
from app.models.schemas import user_serializer

router = APIRouter()

@router.post("/signup", response_model=UserPublic)
async def signup(user: UserCreate):

    # 1️⃣ Check if email already exists
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2️⃣ Hash password
    hashed_pwd = hash_password(user.password)

    # 3️⃣ Create user dictionary
    is_admin_email = user.email.lower() in ADMIN_EMAILS
    new_user = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_pwd,
        "role": "admin" if is_admin_email else "user",
        "is_active": True,
        "created_at": datetime.utcnow()
    }

    # 4️⃣ Insert into MongoDB
    result = users_collection.insert_one(new_user)

    # 5️⃣ Fetch inserted user
    created_user = users_collection.find_one({"_id": result.inserted_id})

    if created_user is None:
        raise HTTPException(status_code=500, detail="Failed to fetch created user")

    return user_serializer(created_user)