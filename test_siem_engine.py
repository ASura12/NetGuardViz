from app.siem.alert_engine import AlertEngine

siem = AlertEngine(export_path="alerts/alerts.json")

print("Test 1 — Ingesting a PORT_SCAN alert...")
siem.ingest({
    "alert": "PORT_SCAN_DETECTED",
    "severity": "HIGH",
    "src_ip": "192.168.1.100",
    "ports_hit": 20,
    "detail": "20 ports hit in 60 seconds"
})

print("Test 2 — Ingesting an ARP_SPOOF alert from same IP...")
siem.ingest({
    "alert": "ARP_SPOOF_DETECTED",
    "severity": "CRITICAL",
    "src_ip": "192.168.1.100",
    "detail": "MAC address changed unexpectedly"
})

print("Test 3 — Ingesting a MALICIOUS_IP alert...")
siem.ingest({
    "alert": "MALICIOUS_IP_CONNECTION",
    "severity": "CRITICAL",
    "src_ip": "45.33.32.156",
    "detail": "IP found in AbuseIPDB with score 89"
})

print("\n--- Alert Summary ---")
print(f"LOW     : {siem.stats['LOW']}")
print(f"MEDIUM  : {siem.stats['MEDIUM']}")
print(f"HIGH    : {siem.stats['HIGH']}")
print(f"CRITICAL: {siem.stats['CRITICAL']}")

print("\n--- Correlation Results ---")
threats = siem.correlate()
for ip, data in threats.items():
    print(f"IP: {ip}")
    print(f"   Threat Level : {data['threat_level']}")
    print(f"   Reasons      : {data['reasons']}")
    print(f"   Alert Count  : {data['alert_count']}")

print("\n✅ alerts/alerts.json has been created — open it to verify")