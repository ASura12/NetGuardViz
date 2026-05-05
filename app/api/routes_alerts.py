from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.database import alerts_collection
from app.auth.dependency import get_current_user
from app.auth.roles import require_role



router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


def _serialize_bson(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, list):
        return [_serialize_bson(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize_bson(item) for key, item in value.items()}
    return value

@router.get("/")
async def get_alerts(
    current_user=Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    keyword: str | None = None
):

    query = {}
    # regular users see only their alerts; admins see all
    if current_user.get("role") != "admin":
        query["owner_email"] = current_user["email"]

    if keyword:
        query["detected_keywords"] = {"$regex": keyword, "$options": "i"}

    skip = (page - 1) * limit

    alerts = list(
        alerts_collection
        .find(query)
        .skip(skip)
        .limit(limit)
    )

    alerts = [_serialize_bson(alert) for alert in alerts]
    # expose a stable `id` string to the frontend and remove raw `_id`
    for a in alerts:
        if isinstance(a, dict) and a.get("_id") is not None:
            a["id"] = a.pop("_id")

    total = alerts_collection.count_documents(query)

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "data": alerts
    }

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str, current_user = Depends(require_role("admin"))):
    try:
        obj_id = ObjectId(alert_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid alert ID")

    # Admins are allowed to delete any alert. If you later allow non-admins here,
    # reintroduce an owner check. Currently this endpoint is protected by
    # `require_role("admin")` so only admins call it.
    result = alerts_collection.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {"message": "Alert deleted"}

