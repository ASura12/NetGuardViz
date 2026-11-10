# detectors/wifi_guard.py
"""
802.11 (Wi-Fi) anomaly detector for NetGuardViz.

Passive analysis only: it inspects frames that were already captured (live from a
monitor-mode interface, or replayed from a pcap) and never transmits anything.

Usage mirrors the other detectors: feed packets to `analyze(pkt)` and ingest any
alert dicts it returns into the SIEM engine.

Detections (all raised incrementally, so they also work in live capture):
  * DEAUTH_FLOOD            - many deauth/disassoc frames aimed at one target in a window
  * BEACON_FLOOD            - many distinct SSID/BSSID pairs advertised in a window
  * EVIL_TWIN_SUSPECTED     - same SSID advertised by another BSSID with different security
  * WEAK_WIFI_SECURITY      - open or WEP network observed
  * WPA_HANDSHAKE_CAPTURED  - full 4-way EAPOL exchange observed (informational)
"""
from collections import Counter, defaultdict, deque

from scapy.all import (  # type: ignore
    Dot11, Dot11Beacon, Dot11ProbeResp, Dot11Deauth, Dot11Disas, EAPOL,
)

BROADCAST = "ff:ff:ff:ff:ff:ff"
FRAME_TYPES = {0: "mgmt", 1: "ctrl", 2: "data"}
DEAUTH_REASONS = {
    1: "Unspecified", 2: "Previous auth no longer valid", 3: "Station leaving",
    4: "Inactivity", 6: "Class 2 frame from non-authenticated STA",
    7: "Class 3 frame from non-associated STA", 8: "Leaving BSS",
    15: "4-way handshake timeout",
}


class WiFiGuard:
    def __init__(self, window=5.0, deauth_threshold=30, beacon_threshold=20,
                 cooldown=10.0):
        self.window = window
        self.deauth_threshold = deauth_threshold
        self.beacon_threshold = beacon_threshold
        self.cooldown = cooldown  # seconds before re-alerting the same condition

        # inventory (used for reporting / dashboards)
        self.frame_counts = Counter()
        self.aps = {}                      # bssid -> {ssid, channel, crypto, beacons}
        self.clients = defaultdict(set)    # bssid -> set of client MACs
        self.first_ts = None
        self.last_ts = None

        # detector state
        self._deauth_win = defaultdict(deque)   # (kind, bssid, dst) -> timestamps
        self._beacon_win = deque()              # (ts, ssid, bssid)
        self._eapol = defaultdict(int)          # (bssid, client) -> frames seen
        self._last_alert = {}                   # dedupe key -> last alert ts
        self._weak_reported = set()             # bssids already flagged weak
        self._twin_reported = set()             # (ssid, bssid) already flagged

    # ------------------------------------------------------------------ public
    def analyze(self, pkt):
        """Inspect one packet. Returns a (possibly empty) list of alert dicts."""
        if not pkt.haslayer(Dot11):
            return []
        ts = float(pkt.time)
        if self.first_ts is None:
            self.first_ts = ts
        self.last_ts = ts

        d = pkt[Dot11]
        self.frame_counts[f"{FRAME_TYPES.get(d.type, d.type)}/{d.subtype}"] += 1

        if pkt.haslayer(Dot11Beacon) or pkt.haslayer(Dot11ProbeResp):
            return self._beacon(pkt, ts)
        if pkt.haslayer(Dot11Deauth) or pkt.haslayer(Dot11Disas):
            return self._deauth(pkt, ts)
        if d.type == 2:
            return self._data(pkt, d, ts)
        return []

    def summary(self):
        """JSON-serialisable snapshot of what has been observed so far."""
        return {
            "capture_seconds": round((self.last_ts or 0) - (self.first_ts or 0), 2),
            "frames": dict(sorted(self.frame_counts.items())),
            "access_points": [
                {"bssid": b, **info, "clients": len(self.clients.get(b, ()))}
                for b, info in self.aps.items()
            ],
        }

    # ----------------------------------------------------------------- helpers
    def _due(self, key, ts):
        """True (and records ts) if `key` has not alerted within the cooldown."""
        if ts - self._last_alert.get(key, float("-inf")) >= self.cooldown:
            self._last_alert[key] = ts
            return True
        return False

    @staticmethod
    def _alert(name, severity, detail, ts, **extra):
        return {"alert": name, "severity": severity, "detail": detail,
                "timestamp": ts, "source": "wifi", **extra}

    # ----------------------------------------------------------- beacons / APs
    def _beacon(self, pkt, ts):
        d = pkt[Dot11]
        bssid = (d.addr3 or "").lower()
        layer = pkt[Dot11Beacon] if pkt.haslayer(Dot11Beacon) else pkt[Dot11ProbeResp]
        try:
            stats = layer.network_stats()
        except Exception:
            return []  # malformed information elements - skip, don't crash the sniffer

        ssid = stats.get("ssid", "")
        channel = stats.get("channel")
        crypto = sorted(stats.get("crypto") or {"OPN"})
        alerts = []

        is_new = bssid not in self.aps
        prev = self.aps.get(bssid, {})
        self.aps[bssid] = {"ssid": ssid, "channel": channel, "crypto": crypto,
                           "beacons": prev.get("beacons", 0) + 1}

        if is_new and ssid:
            alerts += self._check_new_ap(bssid, ssid, channel, crypto, ts)
        alerts += self._check_beacon_flood(ssid, bssid, ts)
        return alerts

    def _check_new_ap(self, bssid, ssid, channel, crypto, ts):
        alerts = []
        # Weak security (once per BSSID)
        # Scapy labels an open network "OPN" in network_stats().
        is_weak = "OPN" in crypto or "Open" in crypto or "WEP" in crypto
        if is_weak and bssid not in self._weak_reported:
            self._weak_reported.add(bssid)
            alerts.append(self._alert(
                "WEAK_WIFI_SECURITY", "MEDIUM",
                f"Network '{ssid}' ({bssid}) uses {'/'.join(crypto)}",
                ts, bssid=bssid, src_mac=bssid, ssid=ssid))

        # Evil twin: same SSID already seen on another BSSID with different security
        for other_bssid, info in self.aps.items():
            if other_bssid == bssid or info["ssid"] != ssid:
                continue
            if info["crypto"] != crypto and (ssid, bssid) not in self._twin_reported:
                self._twin_reported.add((ssid, bssid))
                alerts.append(self._alert(
                    "EVIL_TWIN_SUSPECTED", "CRITICAL",
                    f"SSID '{ssid}' now also advertised by {bssid} "
                    f"({'/'.join(crypto)}, ch{channel}) but {other_bssid} uses "
                    f"{'/'.join(info['crypto'])}",
                    ts, bssid=bssid, src_mac=bssid, ssid=ssid,
                    legit_bssid=other_bssid))
                break
        return alerts

    def _check_beacon_flood(self, ssid, bssid, ts):
        self._beacon_win.append((ts, ssid, bssid))
        while self._beacon_win and ts - self._beacon_win[0][0] > self.window:
            self._beacon_win.popleft()
        distinct = {(s, b) for _, s, b in self._beacon_win}
        if len(distinct) >= self.beacon_threshold and self._due("beacon_flood", ts):
            return [self._alert(
                "BEACON_FLOOD", "HIGH",
                f"{len(distinct)} distinct SSID/BSSID pairs advertised in {self.window:g}s",
                ts, unique_networks=len(distinct), window_seconds=self.window)]
        return []

    # --------------------------------------------------------- deauth / disassoc
    def _deauth(self, pkt, ts):
        d = pkt[Dot11]
        if pkt.haslayer(Dot11Deauth):
            kind, layer = "deauth", pkt[Dot11Deauth]
        else:
            kind, layer = "disassoc", pkt[Dot11Disas]
        src = (d.addr2 or "").lower()
        dst = (d.addr1 or "").lower()
        bssid = (d.addr3 or "").lower()

        win = self._deauth_win[(kind, bssid, dst)]
        win.append(ts)
        while win and ts - win[0] > self.window:
            win.popleft()

        if len(win) >= self.deauth_threshold and self._due(("deauth", kind, bssid, dst), ts):
            target = "all clients (broadcast)" if dst == BROADCAST else dst
            reason = DEAUTH_REASONS.get(layer.reason, f"code {layer.reason}")
            return [self._alert(
                "DEAUTH_FLOOD", "HIGH",
                f"{len(win)} {kind} frames in {self.window:g}s targeting {target} "
                f"on BSSID {bssid} (reason: {reason})",
                ts, bssid=bssid, src_mac=src, target_mac=dst, frame_kind=kind,
                frame_count=len(win), window_seconds=self.window)]
        return []

    # ------------------------------------------------------------ data / EAPOL
    def _data(self, pkt, d, ts):
        ds = int(d.FCfield) & 0x3
        if ds == 1:        # to-DS:   addr1 = BSSID, addr2 = client
            bssid, client = d.addr1, d.addr2
        elif ds == 2:      # from-DS: addr2 = BSSID, addr1 = client
            bssid, client = d.addr2, d.addr1
        else:
            return []
        if not bssid or not client:
            return []
        bssid, client = bssid.lower(), client.lower()
        if client != BROADCAST:
            self.clients[bssid].add(client)

        if pkt.haslayer(EAPOL):
            key = (bssid, client)
            self._eapol[key] += 1
            if self._eapol[key] >= 4:
                self._eapol[key] = 0
                return [self._alert(
                    "WPA_HANDSHAKE_CAPTURED", "LOW",
                    f"Full 4-way EAPOL handshake observed between {client} and {bssid}",
                    ts, bssid=bssid, src_mac=client)]
        return []
