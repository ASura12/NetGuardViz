from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import JWTService
from app.core.database import users_collection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

jwt_service = JWTService()
async def get_current_user(token: str = Depends(oauth2_scheme)):

    # 1️⃣ Decode JWT token

    payload =jwt_service.decode(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # 2️⃣ Extract user identity from token
    email = payload.get("sub")

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # 3️⃣ Fetch user from database
    user = users_collection.find_one({"email": email})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )

    # 4️⃣ Return normalized authenticated user info from DB
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "role": user.get("role", "user"),
        "is_active": user.get("is_active", True)
    }

