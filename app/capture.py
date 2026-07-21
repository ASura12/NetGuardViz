from scapy.all import sniff, ARP, TCP, Raw  #type: ignore
from app.detectors.port_scan import PortScanDetector
from app.detectors.arp_spoof import ARPSpoofDetector
from app.detectors.cleartext_creds import CleartextCredDetector
from app.threat_intel.abuseipdb import AbuseIPDB
from app.siem.alert_engine import AlertEngine
import os, time

psd = PortScanDetector(threshold=15, window=60,cooldown=30)
arp_detector = ARPSpoofDetector()
cred = CleartextCredDetector()
intel = AbuseIPDB(api_key=os.getenv("ABUSEIPDB_API_KEY", ""))
siem = AlertEngine()

packet_count = 0
session_start = time.time()

def process_packet(pkt):
    global packet_count, session_start
    packet_count = 0
    session_start = time.time()
    try:
        timestamp = time.time()

        if pkt.haslayer(ARP) and pkt[ARP].op == 2:
            alert = arp_detector.analyze(pkt[ARP].psrc, pkt[ARP].hwsrc)
            if alert:
                siem.ingest(alert)
                print(f"🚨 ALERT: {alert['alert']} from {alert.get('ip') or alert.get('src_ip')}")

        if pkt.haslayer(TCP) and pkt.haslayer("IP"):
            src_ip = pkt["IP"].src
            dst_port = pkt[TCP].dport

            alert = psd.analyze(src_ip, dst_port, timestamp)
            if alert:
                siem.ingest(alert)
                print(f"🚨 ALERT: {alert['alert']} from {alert['src_ip']}")

            intel_result = intel.check_ip(src_ip)
            if not intel_result.get("clean"):
                siem.ingest(intel_result)
                print(f"🚨 ALERT: MALICIOUS_IP_CONNECTION from {src_ip}")

            if pkt.haslayer(Raw):
                payload = pkt[Raw].load.decode("utf-8", errors="ignore")
                for a in cred.analyze(payload, src_ip, dst_port):
                    siem.ingest(a)
                    print(f"🚨 ALERT: {a['alert']} from {src_ip}")

    except Exception as e:
        # Don't crash the whole sniffer over one bad packet
        print(f"[!] Skipped a packet due to error: {e}")

def start_capture(iface=None):
    print("[*] Starting packet capture on default interface...")
    try:
        sniff(iface=iface, prn=process_packet, store=False)
    except KeyboardInterrupt:
        elapsed = time.time() - session_start
        rate = (packet_count / elapsed) * 60
        print(f"\n[SUMMARY] Captured {packet_count} packets in {elapsed:.1f}s")
        print(f"[SUMMARY] Throughput: {rate:.0f} packets/min")

if __name__ == "__main__":
    start_capture()