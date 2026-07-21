from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.hashing import verify_password
from app.core.database import users_collection
from app.core.security import JWTService
from app.core.logger import logger

router = APIRouter()
jwt_service = JWTService()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):

    logger.info(f"Login attempt for email: {form_data.username}")

    # Find user by email
    db_user = users_collection.find_one({"email": form_data.username})

    if not db_user:
        logger.warning(f"Login failed - user not found: {form_data.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not verify_password(form_data.password, db_user["hashed_password"]):
        logger.warning(f"Login failed - wrong password: {form_data.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate JWT
    token = jwt_service.encode(
        db_user["email"],
        db_user.get("role", "user")
    )

    logger.info(f"User logged in successfully: {form_data.username}")

    return {
        "access_token": token,
        "token_type": "bearer"
    }