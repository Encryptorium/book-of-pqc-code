"""Tests for the fleet-readiness classifier."""

from tls_migration.fleet_assessment import classify


LIBRARY_MATRIX = {
    "openssl": (3, 5, 0),
    "go-crypto-tls": (1, 24, 0),
    "rustls": (0, 23, 22),
    "nss": (132, 0, 0),
}


def test_ready_when_version_exceeds_minimum():
    rows = classify([("app-server", "openssl", "3.5.6")], LIBRARY_MATRIX)
    assert len(rows) == 1
    assert rows[0].status == "ready"
    assert rows[0].version == (3, 5, 6)


def test_ready_at_exact_minimum():
    rows = classify([("app-server", "openssl", "3.5.0")], LIBRARY_MATRIX)
    assert rows[0].status == "ready"


def test_gated_when_version_below_minimum():
    rows = classify([("app-server", "openssl", "3.4.1")], LIBRARY_MATRIX)
    assert rows[0].status == "gated"
    assert "below minimum" in rows[0].reason


def test_blocked_when_library_unknown():
    rows = classify([("legacy-appliance", "wolfssl", "5.7.0")], LIBRARY_MATRIX)
    assert rows[0].status == "blocked"
    assert "wolfssl" in rows[0].reason


def test_mixed_inventory_classified_row_by_row():
    inventory = [
        ("edge-lb", "openssl", "3.5.2"),
        ("app-server", "openssl", "3.3.0"),
        ("backend-peer", "go-crypto-tls", "1.24.1"),
        ("sidecar", "envoy", "1.30.0"),
    ]
    rows = classify(inventory, LIBRARY_MATRIX)
    statuses = [r.status for r in rows]
    assert statuses == ["ready", "gated", "ready", "blocked"]


def test_minor_version_comparison_is_lexicographic():
    # 1.23.99 < 1.24.0 in tuple comparison
    rows = classify([("backend-peer", "go-crypto-tls", "1.23.99")], LIBRARY_MATRIX)
    assert rows[0].status == "gated"
