from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.auth.roles import require_role
from app.core.database import users_collection

router = APIRouter(prefix="/auth", tags=["Admin"])


def _serialize_user(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user.get("username", ""),
        "email": user.get("email", ""),
        "role": user.get("role", "user"),
        "is_active": user.get("is_active", True),
    }


@router.get("/users")
async def list_users(admin_user=Depends(require_role("admin"))):
    users = list(users_collection.find({}, {"hashed_password": 0}))
    return {"data": [_serialize_user(user) for user in users]}


@router.patch("/users/{user_id}/role")
async def update_user_role(user_id: str, payload: dict, admin_user=Depends(require_role("admin"))):
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    role = payload.get("role")
    allowed_roles = {"user", "admin"}
    if role not in allowed_roles:
        raise HTTPException(status_code=400, detail="Invalid role")

    if str(admin_user.get("id")) == str(obj_id) and role != "admin":
        raise HTTPException(status_code=400, detail="You cannot remove your own admin role")

    result = users_collection.update_one({"_id": obj_id}, {"$set": {"role": role}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    updated = users_collection.find_one({"_id": obj_id}, {"hashed_password": 0})
    return {"message": "Role updated", "user": _serialize_user(updated)}


@router.patch("/users/{user_id}/status")
async def update_user_status(user_id: str, payload: dict, admin_user=Depends(require_role("admin"))):
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    is_active = payload.get("is_active")
    if not isinstance(is_active, bool):
        raise HTTPException(status_code=400, detail="is_active must be boolean")

    if str(admin_user.get("id")) == str(obj_id) and is_active is False:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account")

    result = users_collection.update_one({"_id": obj_id}, {"$set": {"is_active": is_active}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    updated = users_collection.find_one({"_id": obj_id}, {"hashed_password": 0})
    return {"message": "Status updated", "user": _serialize_user(updated)}