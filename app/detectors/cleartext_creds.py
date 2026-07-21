# detectors/cleartext_creds.py
import re

class CleartextCredDetector:
    HTTP_AUTH_PATTERN = re.compile(
        r'Authorization:\s*Basic\s+([A-Za-z0-9+/=]+)', re.IGNORECASE
    )
    FTP_PASS_PATTERN = re.compile(r'PASS\s+\S+', re.IGNORECASE)

    def analyze(self, payload: str, src_ip: str, dst_port: int):
        alerts = []
        
        if dst_port == 80 and self.HTTP_AUTH_PATTERN.search(payload):
            alerts.append({
                "alert": "CLEARTEXT_HTTP_AUTH",
                "severity": "HIGH",
                "src_ip": src_ip,
                "detail": "HTTP Basic Auth credentials in plaintext"
            })
        
        if dst_port == 21 and self.FTP_PASS_PATTERN.search(payload):
            alerts.append({
                "alert": "CLEARTEXT_FTP_PASSWORD",
                "severity": "HIGH",
                "src_ip": src_ip,
                "detail": "FTP password transmitted in cleartext"
            })
        
        return alerts