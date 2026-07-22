from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.hashing import verify_password
from app.core.database import users_collection
from app.core.security import JWTService
from app.core.logger import logger
from app.threat_intel.abuseipdb import AbuseIPDB
from app.siem.alert_engine import AlertEngine
import os

router = APIRouter()
jwt_service = JWTService()
intel = AbuseIPDB(api_key=os.getenv("ABUSEIPDB_API_KEY", ""))
siem = AlertEngine(export_path="alerts/alerts.json")

@router.post("/login")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):

    logger.info(f"Login attempt for email: {form_data.username}")

    db_user = users_collection.find_one({"email": form_data.username})

    if not db_user:
        logger.warning(f"Login failed - user not found: {form_data.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, db_user["hashed_password"]):
        logger.warning(f"Login failed - wrong password: {form_data.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt_service.encode(
        db_user["email"],
        db_user.get("role", "user")
    )

    logger.info(f"User logged in successfully: {form_data.username}")

    # ── Automatic threat intel check on login IP ──
    try:
        client_ip = get_client_ip(request)
        # Skip check for local/private IPs (localhost, private testing)
        if not client_ip.startswith(("127.", "10.", "192.168.", "172.")):
            intel_result = intel.check_ip(client_ip)
            if not intel_result.get("clean"):
                intel_result["detail"] = f"Suspicious login from {client_ip}"
                siem.ingest(intel_result)
                logger.warning(f"Suspicious login IP flagged: {client_ip}")
    except Exception as e:
        logger.error(f"Threat intel check failed on login: {e}")

    return {
        "access_token": token,
        "token_type": "bearer"
    }

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"