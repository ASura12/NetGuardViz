# detectors/arp_spoof.py
class ARPSpoofDetector:
    def __init__(self):
        self.ip_mac_table = {}  # known IP→MAC mappings

    def analyze(self, ip, mac):
        if ip in self.ip_mac_table:
            if self.ip_mac_table[ip] != mac:
                return {
                    "alert": "ARP_SPOOF_DETECTED",
                    "severity": "CRITICAL",
                    "ip": ip,
                    "known_mac": self.ip_mac_table[ip],
                    "new_mac": mac,
                }
        self.ip_mac_table[ip] = mac
        return None