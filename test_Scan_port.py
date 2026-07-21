from app.detectors.port_scan import PortScanDetector
import time

detector = PortScanDetector(threshold=15, window=60)

print("Simulating port scan from 192.168.1.100...\n")

# Simulate one IP hitting 20 different ports rapidly
for port in range(1, 21):
    result = detector.analyze(
        src_ip="192.168.1.100",
        dst_port=port,
        timestamp=time.time()
    )
    if result:
        print(f"🚨 ALERT TRIGGERED:")
        print(f"   Source IP  : {result['src_ip']}")
        print(f"   Ports hit  : {result['ports_hit']}")
        print(f"   Severity   : {result['severity']}")
        print(f"   Alert type : {result['alert']}")
        break  # Alert fired, stop loop

print("\nSimulating normal traffic from 192.168.1.200...")
# Normal user — only hits 3 ports, should NOT trigger alert
for port in [80, 443, 22]:
    result = detector.analyze(
        src_ip="192.168.1.200",
        dst_port=port,
        timestamp=time.time()
    )
    if result:
        print("Alert triggered — unexpected!")
    else:
        print(f"   Port {port} — no alert (normal)")