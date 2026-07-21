from fastapi import APIRouter, Depends
from app.threat_intel.abuseipdb import AbuseIPDB
from app.auth.dependency import get_current_user  # your existing auth
import os
from dotenv import load_dotenv
load_dotenv()


router = APIRouter()


api_key = os.getenv("ABUSEIPDB_API_KEY")
if not api_key:
    raise ValueError("ABUSEIPDB_API_KEY is missing from .env file")

intel = AbuseIPDB(api_key=api_key)

@router.get("/check/{ip}")
async def check_ip_reputation(ip: str, user=Depends(get_current_user)):
    """Check a single IP against AbuseIPDB threat intel."""
    return intel.check_ip(ip)

@router.get("/summary")
async def threat_summary(user=Depends(get_current_user)):
    """Return SIEM alert summary with severity breakdown."""
    import json, os
    path = "alerts/alerts.json"
    if not os.path.exists(path):
        return {"message": "No alerts yet", "summary": {}}
    with open(path) as f:
        return json.load(f)