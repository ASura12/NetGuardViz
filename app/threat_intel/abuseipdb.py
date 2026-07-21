# threat_intel/abuseipdb.py
import requests
import functools

class AbuseIPDB:
    BASE_URL = "https://api.abuseipdb.com/api/v2/check"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Key": api_key,
            "Accept": "application/json"
        }

    @functools.lru_cache(maxsize=1000)  # Cache to avoid burning API quota
    def check_ip(self, ip: str) -> dict:
        params = {"ipAddress": ip, "maxAgeInDays": 90}
        response = requests.get(
            self.BASE_URL, headers=self.headers, params=params, timeout=5
        )
        data = response.json().get("data", {})
        
        score = data.get("abuseConfidenceScore", 0)
        if score > 25:
            return {
                "alert": "MALICIOUS_IP_CONNECTION",
                "severity": "CRITICAL" if score > 75 else "HIGH",
                "ip": ip,
                "abuse_score": score,
                "total_reports": data.get("totalReports", 0),
                "country": data.get("countryCode")
            }
        return {"ip": ip, "clean": True, "score": score}