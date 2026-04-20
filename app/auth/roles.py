from fastapi import Depends, HTTPException, status
from app.auth.dependency import get_current_user


def require_role(required_role: str):

    async def role_checker(current_user = Depends(get_current_user)):

        user_role = current_user["role"]

        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden"
            )

        return current_user

    return role_checker