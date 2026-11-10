#!/usr/bin/env python3
"""
Writes a synthetic 802.11 capture to disk so the Wi-Fi detector can be tested
without monitor-mode hardware. Nothing is transmitted - frames are only written
to a pcap file.

  python scripts/make_sample_pcap.py                 # attack scenario -> samples/sample.pcap
  python scripts/make_sample_pcap.py --benign        # normal traffic only -> samples/benign.pcap

Attack scenario contains: normal beacons from two WPA2 APs, an open "evil twin"
that clones one SSID, a 4-frame EAPOL handshake, and a 120-frame deauth burst.
"""
import argparse
import os

from scapy.all import (  # type: ignore
    RadioTap, Dot11, Dot11Beacon, Dot11Elt, Dot11Deauth, LLC, SNAP, EAPOL, Raw, wrpcap,
)

AP1, AP2, EVIL = "aa:bb:cc:00:00:01", "aa:bb:cc:00:00:02", "de:ad:be:ef:00:01"
CLIENT = "11:22:33:44:55:66"
BCAST = "ff:ff:ff:ff:ff:ff"


def beacon(bssid, ssid, chan, secure=True, t=0.0):
    cap = "ESS+privacy" if secure else "ESS"
    elts = (Dot11Elt(ID=0, info=ssid) / Dot11Elt(ID=1, info=b"\x82\x84\x8b\x96") /
            Dot11Elt(ID=3, info=bytes([chan])))
    if secure:  # minimal RSN information element -> WPA2-PSK (CCMP)
        rsn = (b"\x01\x00" b"\x00\x0f\xac\x04" b"\x01\x00" b"\x00\x0f\xac\x04"
               b"\x01\x00" b"\x00\x0f\xac\x02" b"\x00\x00")
        elts = elts / Dot11Elt(ID=48, info=rsn)
    p = (RadioTap() / Dot11(type=0, subtype=8, addr1=BCAST, addr2=bssid, addr3=bssid) /
         Dot11Beacon(cap=cap) / elts)
    p.time = t
    return p


def eapol_frame(to_ds, t):
    d = Dot11(type=2, subtype=0, FCfield=1 if to_ds else 2,  # 1 = to-DS, 2 = from-DS
              addr1=AP1 if to_ds else CLIENT, addr2=CLIENT if to_ds else AP1, addr3=AP1)
    p = (RadioTap() / d / LLC() / SNAP(OUI=0, code=0x888e) /
         EAPOL(version=2, type=3) / Raw(b"\x02" + b"\x00" * 94))
    p.time = t
    return p


def deauth(t, reason=7):
    p = (RadioTap() / Dot11(type=0, subtype=12, addr1=CLIENT, addr2=AP1, addr3=AP1) /
         Dot11Deauth(reason=reason))
    p.time = t
    return p


def build_packets(attack=True, deauth_count=120):
    pkts = []
    for i in range(10):
        pkts.append(beacon(AP1, "CampusWiFi", 6, True, i * 0.1))
        pkts.append(beacon(AP2, "LabNet", 11, True, i * 0.1 + 0.01))
    if attack:
        pkts.append(beacon(EVIL, "CampusWiFi", 6, False, 1.0))      # evil twin (open)
    for i in range(4):                                                # 4-way handshake
        pkts.append(eapol_frame(to_ds=(i % 2 == 1), t=2.0 + i * 0.05))
    if attack:
        for i in range(deauth_count):                                 # deauth flood
            pkts.append(deauth(3.0 + i * 0.017))
    else:
        for i in range(3):                                            # a few normal deauths
            pkts.append(deauth(3.0 + i * 20.0, reason=3))
    return [_as_captured(p) for p in pkts]


def _as_captured(p):
    """Serialise and re-dissect so the packet looks like one read from a real capture
    (information elements such as the RSN IE are only parsed after dissection)."""
    q = RadioTap(bytes(p))
    q.time = p.time
    return q


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--benign", action="store_true", help="write normal traffic only")
    ap.add_argument("--out", help="output path (default samples/sample.pcap or samples/benign.pcap)")
    args = ap.parse_args()

    out = args.out or os.path.join("samples", "benign.pcap" if args.benign else "sample.pcap")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    pkts = build_packets(attack=not args.benign)
    wrpcap(out, pkts)
    print(f"wrote {out} ({len(pkts)} frames)")


if __name__ == "__main__":
    main()
