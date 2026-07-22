import uuid
from datetime import datetime
from enum import Enum
from app.core.database import alerts_collection

class Severity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class AlertEngine:
    def __init__(self):
        pass  # no file path needed anymore

    def ingest(self, raw_alert: dict):
        alert = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "severity": raw_alert.get("severity", "LOW"),
            "type": raw_alert.get("alert"),
            "src_ip": raw_alert.get("src_ip") or raw_alert.get("ip"),
            "detail": raw_alert.get("detail", ""),
            "raw": raw_alert
        }
        alerts_collection.insert_one(alert.copy())  # .copy() avoids Mongo injecting _id into your local dict
        return alert

    def get_summary(self):
        stats = {s.name: 0 for s in Severity}
        alerts = list(alerts_collection.find({}, {"_id": 0}).sort("timestamp", -1))
        for a in alerts:
            sev = a.get("severity", "LOW")
            if sev in stats:
                stats[sev] += 1
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "summary": stats,
            "alerts": alerts
        }

    def correlate(self):
        alerts = list(alerts_collection.find({}, {"_id": 0}))
        ip_alerts = {}
        for a in alerts:
            ip = a.get("src_ip")
            if ip:
                ip_alerts.setdefault(ip, []).append(a["type"])

        threats = {}
        for ip, types in ip_alerts.items():
            if len(set(types)) >= 2:
                threats[ip] = {
                    "threat_level": "ELEVATED",
                    "reasons": list(set(types)),
                    "alert_count": len(types)
                }
        return threats