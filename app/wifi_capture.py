"""
Wi-Fi capture agent for NetGuardViz (sibling of app/capture.py).

Runs locally - monitor mode needs raw access to a Wi-Fi adapter, so like
capture.py it cannot run on Render.

  # Live capture from a monitor-mode interface (Linux/macOS, needs root):
  sudo python -m app.wifi_capture --iface wlan0mon

  # Replay a capture file (no hardware or database needed with --dry-run):
  python -m app.wifi_capture --pcap samples/sample.pcap --dry-run

Only capture traffic on networks you own or are authorised to monitor.
"""
import argparse
import json
import time

from app.detectors.wifi_guard import WiFiGuard

ICONS = {"CRITICAL": "🔴", "HIGH": "🚨", "MEDIUM": "⚠️", "LOW": "ℹ️"}


def build_handler(guard, siem=None, counters=None):
    """Return a per-packet callback that feeds the detector and (optionally) the SIEM."""
    counters = counters if counters is not None else {"packets": 0, "alerts": 0}

    def handle(pkt):
        counters["packets"] += 1
        try:
            for alert in guard.analyze(pkt):
                counters["alerts"] += 1
                if siem is not None:
                    siem.ingest(alert)
                icon = ICONS.get(alert["severity"], "")
                print(f"{icon} ALERT: {alert['alert']} [{alert['severity']}] - {alert['detail']}")
        except Exception as e:  # don't crash the sniffer over one bad frame
            print(f"[!] Skipped a frame due to error: {e}")

    return handle, counters


def run_pcap(path, guard, siem=None):
    from scapy.all import PcapReader  # type: ignore
    handle, counters = build_handler(guard, siem)
    with PcapReader(path) as reader:
        for pkt in reader:
            handle(pkt)
    return counters


def run_live(iface, guard, siem=None, duration=None):
    from scapy.all import sniff  # type: ignore
    handle, counters = build_handler(guard, siem)
    print(f"[*] Sniffing 802.11 frames on {iface} (Ctrl+C to stop)...")
    try:
        sniff(iface=iface, prn=handle, store=False, timeout=duration)
    except KeyboardInterrupt:
        pass
    return counters


def main():
    ap = argparse.ArgumentParser(description="NetGuardViz Wi-Fi capture agent")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--iface", help="monitor-mode interface, e.g. wlan0mon")
    src.add_argument("--pcap", help="pcap/pcapng file to replay")
    ap.add_argument("--duration", type=int, help="stop live capture after N seconds")
    ap.add_argument("--window", type=float, default=5.0, help="sliding window in seconds")
    ap.add_argument("--deauth-threshold", type=int, default=30,
                    help="deauth/disassoc frames per window that count as a flood")
    ap.add_argument("--dry-run", action="store_true",
                    help="print alerts only; don't connect to MongoDB / the SIEM engine")
    ap.add_argument("--json", help="write an AP inventory + frame-count summary to this file")
    args = ap.parse_args()

    siem = None
    if not args.dry_run:
        # Imported lazily: this connects to MongoDB (needs .env), which --dry-run avoids.
        from dotenv import load_dotenv
        load_dotenv()
        from app.siem.alert_engine import AlertEngine
        siem = AlertEngine()

    guard = WiFiGuard(window=args.window, deauth_threshold=args.deauth_threshold)
    started = time.time()
    counters = (run_pcap(args.pcap, guard, siem) if args.pcap
                else run_live(args.iface, guard, siem, args.duration))

    elapsed = time.time() - started
    print(f"\n[SUMMARY] {counters['packets']} frames, {counters['alerts']} alerts "
          f"in {elapsed:.1f}s ({len(guard.aps)} access points seen)")
    if args.json:
        with open(args.json, "w") as f:
            json.dump(guard.summary(), f, indent=2)
        print(f"[SUMMARY] inventory written to {args.json}")


if __name__ == "__main__":
    main()
