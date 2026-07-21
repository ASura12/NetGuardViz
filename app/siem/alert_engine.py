# siem/alert_engine.py
import json
import uuid
from datetime import datetime
from enum import Enum

class Severity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class AlertEngine:
    def __init__(self, export_path="alerts/alerts.json"):
        self.alerts = []
        self.export_path = export_path
        self.stats = {s.name: 0 for s in Severity}

    def ingest(self, raw_alert: dict):
        """Normalize and store an alert from any detector."""
        alert = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "severity": raw_alert.get("severity", "LOW"),
            "type": raw_alert.get("alert"),
            "src_ip": raw_alert.get("src_ip") or raw_alert.get("ip"),
            "detail": raw_alert.get("detail", ""),
            "raw": raw_alert
        }
        self.alerts.append(alert)
        self.stats[alert["severity"]] += 1
        self._export()
        return alert

    def _export(self):
        with open(self.export_path, "w") as f:
            json.dump({
                "generated_at": datetime.utcnow().isoformat(),
                "summary": self.stats,
                "alerts": self.alerts
            }, f, indent=2)

    def correlate(self):
        """
        Simple correlation: same src_ip triggering multiple
        alert types = elevated threat score.
        """
        ip_alerts = {}
        for a in self.alerts:
            ip = a.get("src_ip")
            if ip:
                ip_alerts.setdefault(ip, []).append(a["type"])
        
        threats = {}
        for ip, types in ip_alerts.items():
            if len(set(types)) >= 2:  # Multiple different alert types
                threats[ip] = {
                    "threat_level": "ELEVATED",
                    "reasons": list(set(types)),
                    "alert_count": len(types)
                }
        return threats