from fastapi import APIRouter, HTTPException
from app.models.schemas import UserLogin
from app.auth.hashing import verify_password
from app.core.database import users_collection
from app.core.security import JWTService
from app.core.logger import logger

router = APIRouter()
jwt_service = JWTService()

@router.post("/login")
async def login(user: UserLogin):

    logger.info(f"Login attempt for email: {user.email}")

    # 1️⃣ Find user by email
    db_user = users_collection.find_one({"email": user.email})

    if not db_user:
        logger.warning(f"Login failed - user not found: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 2️⃣ Verify password
    if not verify_password(user.password, db_user["hashed_password"]):
        logger.warning(f"Login failed - wrong password: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 3️⃣ Generate JWT
    token = jwt_service.encode(db_user["email"], db_user.get("role", "user"))

    # 4️⃣ Log success
    logger.info(f"User logged in successfully: {user.email}")

    # 5️⃣ Return token
    return {
        "access_token": token,
        "token_type": "bearer"
    }