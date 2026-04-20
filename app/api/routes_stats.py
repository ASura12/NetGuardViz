from fastapi import APIRouter, Depends
from app.core.database import logs_collection, alerts_collection
from app.models.stats_model import StatsModel
from app.auth.dependency import get_current_user

router = APIRouter(prefix="/api/stats", tags=["Stats"])

@router.get("/", response_model=StatsModel)
async def get_stats(current_user=Depends(get_current_user)):
    total_logs = logs_collection.count_documents({
        "owner_email": current_user["email"],
        "is_deleted": {"$ne": True}
    })
    total_alerts = alerts_collection.count_documents({"owner_email": current_user["email"]})

    suspicious_percentage = (
        (total_alerts / total_logs) * 100 if total_logs > 0 else 0.0
    )

    return StatsModel(
        total_logs=total_logs,
        total_alerts=total_alerts,
        suspicious_percentage=round(suspicious_percentage, 2)
    )

