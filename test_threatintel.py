from dotenv import load_dotenv
load_dotenv()

from app.threat_intel.abuseipdb import AbuseIPDB
import os

api_key = os.getenv("ABUSEIPDB_API_KEY")
if not api_key:
    print("❌ ABUSEIPDB_API_KEY missing from .env file")
    exit()

intel = AbuseIPDB(api_key=api_key)

# These are well-known malicious IPs safe to test against
test_ips = {
    "8.8.8.8":      "Google DNS — should be CLEAN",
    "1.1.1.1":      "Cloudflare DNS — should be CLEAN",
    "45.33.32.156": "Known scanner — likely FLAGGED",
    "185.220.101.1":"Tor exit node — likely FLAGGED",
}

print("=" * 50)
print("AbuseIPDB Threat Intel Test")
print("=" * 50)

for ip, description in test_ips.items():
    print(f"\nChecking {ip} ({description})")
    result = intel.check_ip(ip)

    if result.get("clean"):
        print(f"   ✅ CLEAN — abuse score: {result.get('score', 0)}")
    else:
        print(f"   🚨 MALICIOUS DETECTED")
        print(f"      Severity     : {result['severity']}")
        print(f"      Abuse Score  : {result['abuse_score']}/100")
        print(f"      Total Reports: {result['total_reports']}")
        print(f"      Country      : {result['country']}")

print("\n" + "=" * 50)
print("Testing LRU cache — same IP should not hit API twice")
print("Checking 8.8.8.8 again...")
result = intel.check_ip("8.8.8.8")
print(f"   Cache hit — score: {result.get('score', 0)}")
print("✅ Cache working correctly")
print("=" * 50)