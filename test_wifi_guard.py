"""
Tests for the Wi-Fi detector. No MongoDB, network or Wi-Fi hardware needed.

  python test_wifi_guard.py        # plain script
  pytest test_wifi_guard.py        # or via pytest
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from scapy.all import rdpcap, wrpcap  # type: ignore
import make_sample_pcap as gen
from app.detectors.wifi_guard import WiFiGuard


def run(pkts, **kw):
    guard = WiFiGuard(**kw)
    alerts = []
    for p in pkts:
        alerts += guard.analyze(p)
    return guard, alerts


def names(alerts):
    return [a["alert"] for a in alerts]


def test_attack_scenario_raises_expected_alerts():
    guard, alerts = run(gen.build_packets(attack=True))
    got = names(alerts)
    assert got.count("DEAUTH_FLOOD") == 1, got           # one alert, not one per frame
    assert "EVIL_TWIN_SUSPECTED" in got, got
    assert "WEAK_WIFI_SECURITY" in got, got              # the open clone
    assert "WPA_HANDSHAKE_CAPTURED" in got, got

    flood = next(a for a in alerts if a["alert"] == "DEAUTH_FLOOD")
    assert flood["severity"] == "HIGH"
    assert flood["target_mac"] == gen.CLIENT and flood["bssid"] == gen.AP1
    twin = next(a for a in alerts if a["alert"] == "EVIL_TWIN_SUSPECTED")
    assert twin["severity"] == "CRITICAL" and twin["bssid"] == gen.EVIL
    assert twin["legit_bssid"] == gen.AP1

    # Only the open clone is weak - the two WPA2 APs must not be flagged.
    weak = {a["bssid"] for a in alerts if a["alert"] == "WEAK_WIFI_SECURITY"}
    assert weak == {gen.EVIL}, weak


def test_benign_traffic_raises_no_serious_alerts():
    _, alerts = run(gen.build_packets(attack=False))
    assert not [a for a in alerts if a["severity"] in ("HIGH", "CRITICAL")], names(alerts)
    assert "WEAK_WIFI_SECURITY" not in names(alerts), names(alerts)
    assert "EVIL_TWIN_SUSPECTED" not in names(alerts), names(alerts)


def test_few_deauths_below_threshold_do_not_alert():
    _, alerts = run(gen.build_packets(attack=False, deauth_count=0)
                    + [gen.deauth(10.0 + i) for i in range(10)])
    assert "DEAUTH_FLOOD" not in names(alerts)


def test_deauth_threshold_is_configurable():
    pkts = [gen.deauth(i * 0.1) for i in range(10)]
    _, alerts = run(pkts, deauth_threshold=5)
    assert names(alerts) == ["DEAUTH_FLOOD"]


def test_alert_has_siem_compatible_fields():
    _, alerts = run(gen.build_packets(attack=True))
    for a in alerts:
        assert a["severity"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        assert a["alert"] and a["detail"] and a["source"] == "wifi"


def test_inventory_summary():
    guard, _ = run(gen.build_packets(attack=True))
    s = guard.summary()
    assert {ap["bssid"] for ap in s["access_points"]} == {gen.AP1, gen.AP2, gen.EVIL}
    campus = next(ap for ap in s["access_points"] if ap["bssid"] == gen.AP1)
    assert campus["clients"] == 1 and "WPA2/PSK" in campus["crypto"]


def test_pcap_roundtrip(tmp_path=None):
    path = os.path.join(tmp_path or "samples", "_roundtrip_test.pcap")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    wrpcap(path, gen.build_packets(attack=True))
    try:
        _, alerts = run(rdpcap(path))
        assert "DEAUTH_FLOOD" in names(alerts)
    finally:
        os.remove(path)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {name}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
