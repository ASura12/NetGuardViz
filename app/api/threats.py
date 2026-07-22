from fastapi import APIRouter, Depends
from app.siem.alert_engine import AlertEngine
from app.threat_intel.abuseipdb import AbuseIPDB
from app.auth.dependency import get_current_user  # your existing auth
from pydantic import BaseModel
import os
from dotenv import load_dotenv
load_dotenv()


router = APIRouter()


api_key = os.getenv("ABUSEIPDB_API_KEY")
if not api_key:
    raise ValueError("ABUSEIPDB_API_KEY is missing from .env file")

intel = AbuseIPDB(api_key=api_key)


class SeedAlert(BaseModel):
    alert: str
    severity: str
    src_ip: str
    detail: str = ""

@router.post("/seed")
async def seed_alert(payload: SeedAlert, user=Depends(get_current_user)):
    """Manually add a sample alert — useful for demos/portfolio."""
    from app.siem.alert_engine import AlertEngine
    siem = AlertEngine()
    ingested = siem.ingest(payload.dict())
    return {"message": "Alert seeded", "alert": ingested}

@router.get("/check/{ip}")
async def check_ip_reputation(ip: str, user=Depends(get_current_user)):
    """Check a single IP against AbuseIPDB threat intel."""
    return intel.check_ip(ip)

@router.get("/summary")
async def threat_summary(user=Depends(get_current_user)):
    siem = AlertEngine()
    return siem.get_summary()