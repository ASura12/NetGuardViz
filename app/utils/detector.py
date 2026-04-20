from datetime import datetime
from app.core.database import alerts_collection
from app.utils.notification import send_alert_notification

SUSPICIOUS_KEYWORDS = ["denied", "unauthorized", "attack", "malware", "break"]

def detect_suspicious_keywords(filename: str, content: str):

    detected = [
        kw for kw in SUSPICIOUS_KEYWORDS
        if kw.lower() in content.lower()
    ]

    if detected:

        alert_doc = {
            "filename": filename,
            "detected_keywords": detected,
            "timestamp": datetime.utcnow()
        }

        alerts_collection.insert_one(alert_doc)

        # 🔔 Email ALert
        send_alert_notification(alert_doc)

        return alert_doc

    return None