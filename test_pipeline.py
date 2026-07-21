from dotenv import load_dotenv
load_dotenv()

import time
import os
from app.detectors.port_scan import PortScanDetector
from app.detectors.arp_spoof import ARPSpoofDetector
from app.detectors.cleartext_creds import CleartextCredDetector
from app.threat_intel.abuseipdb import AbuseIPDB
from app.siem.alert_engine import AlertEngine

# Initialize all components
psd  = PortScanDetector(threshold=15, window=60)
arp  = ARPSpoofDetector()
cred = CleartextCredDetector()
intel = AbuseIPDB(api_key=os.getenv("ABUSEIPDB_API_KEY", ""))
siem = AlertEngine(export_path="alerts/alerts.json")

print("=" * 55)
print("NetGuardViz — Full Pipeline Test")
print("=" * 55)

# ─────────────────────────────────────────────
# SCENARIO 1: Port Scan Attack
# ─────────────────────────────────────────────
print("\n[SCENARIO 1] Simulating port scan from 10.0.0.5...")
attacker_ip = "10.0.0.5"
for port in range(1, 22):
    result = psd.analyze(attacker_ip, port, time.time())
    if result:
        ingested = siem.ingest(result)
        print(f"   🚨 ALERT: {ingested['type']}")
        print(f"      Severity  : {ingested['severity']}")
        print(f"      Source IP : {ingested['src_ip']}")
        print(f"      Alert ID  : {ingested['id'][:8]}...")
        break

# ─────────────────────────────────────────────
# SCENARIO 2: ARP Spoofing Attack
# ─────────────────────────────────────────────
print("\n[SCENARIO 2] Simulating ARP spoofing from 10.0.0.5...")

# First packet — legitimate MAC learned
arp.analyze("192.168.1.1", "aa:bb:cc:dd:ee:ff")

# Second packet — different MAC for same IP = spoof
result = arp.analyze("192.168.1.1", "11:22:33:44:55:66")
if result:
    result["src_ip"] = attacker_ip  # tag the attacker
    ingested = siem.ingest(result)
    print(f"   🚨 ALERT: {ingested['type']}")
    print(f"      Severity  : {ingested['severity']}")
    print(f"      Alert ID  : {ingested['id'][:8]}...")

# ─────────────────────────────────────────────
# SCENARIO 3: Cleartext Credentials
# ─────────────────────────────────────────────
print("\n[SCENARIO 3] Simulating cleartext HTTP auth...")
fake_payload = "GET /admin HTTP/1.1\r\nAuthorization: Basic dXNlcjpwYXNzd29yZA==\r\n"
results = cred.analyze(fake_payload, attacker_ip, 80)
for result in results:
    ingested = siem.ingest(result)
    print(f"   🚨 ALERT: {ingested['type']}")
    print(f"      Severity  : {ingested['severity']}")
    print(f"      Detail    : {ingested['detail']}")
    print(f"      Alert ID  : {ingested['id'][:8]}...")

# ─────────────────────────────────────────────
# SCENARIO 4: Threat Intelligence Check
# ─────────────────────────────────────────────
print("\n[SCENARIO 4] Checking known malicious IP against AbuseIPDB...")
malicious_ip = "185.220.101.1"
result = intel.check_ip(malicious_ip)
if not result.get("clean"):
    ingested = siem.ingest(result)
    print(f"   🚨 ALERT: {ingested['type']}")
    print(f"      Severity     : {ingested['severity']}")
    print(f"      Abuse Score  : {result['abuse_score']}/100")
    print(f"      Total Reports: {result['total_reports']}")
    print(f"      Country      : {result['country']}")
else:
    print(f"   ✅ IP came back clean (score: {result.get('score')})")

# ─────────────────────────────────────────────
# SCENARIO 5: Correlation — Same IP, Multiple Attacks
# ─────────────────────────────────────────────
print("\n[SCENARIO 5] Running correlation engine...")
threats = siem.correlate()
if threats:
    for ip, data in threats.items():
        print(f"   ⚠️  ELEVATED THREAT: {ip}")
        print(f"      Attack types : {data['reasons']}")
        print(f"      Total alerts : {data['alert_count']}")
else:
    print("   No correlated threats found")

# ─────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("Pipeline Summary")
print("=" * 55)
print(f"   LOW      : {siem.stats['LOW']}")
print(f"   MEDIUM   : {siem.stats['MEDIUM']}")
print(f"   HIGH     : {siem.stats['HIGH']}")
print(f"   CRITICAL : {siem.stats['CRITICAL']}")
print(f"   TOTAL    : {sum(siem.stats.values())} alerts generated")
print(f"\n   JSON export → alerts/alerts.json")
print("\n✅ Full pipeline test complete")
print("=" * 55)