from collections import defaultdict
import time

class PortScanDetector:
    def __init__(self, threshold=15, window=60, cooldown=30):
        self.threshold = threshold
        self.window = window
        self.cooldown = cooldown  # seconds before re-alerting same IP
        self.tracker = defaultdict(list)
        self.last_alert = {}  # src_ip -> last alert timestamp

    def analyze(self, src_ip, dst_port, timestamp):
        self.tracker[src_ip].append((dst_port, timestamp))

        cutoff = timestamp - self.window
        self.tracker[src_ip] = [
            (p, t) for p, t in self.tracker[src_ip] if t > cutoff
        ]

        unique_ports = set(p for p, t in self.tracker[src_ip])

        if len(unique_ports) >= self.threshold:
            last = self.last_alert.get(src_ip, 0)
            if timestamp - last >= self.cooldown:
                self.last_alert[src_ip] = timestamp
                return {
                    "alert": "PORT_SCAN_DETECTED",
                    "severity": "HIGH",
                    "src_ip": src_ip,
                    "ports_hit": len(unique_ports),
                    "window_seconds": self.window,
                    "timestamp": timestamp
                }
        return None