"""Tests for the per-window NamedGroup adoption rollup."""

from pathlib import Path

import pytest

from tls_migration.named_group_rollup import (
    MONITORED,
    Record,
    read_csv,
    rollup,
)


def test_empty_records_returns_empty_windows():
    assert rollup([], 300) == []


def test_single_window_totals_and_percentage():
    records = [
        Record(timestamp=1000, codepoint="0x11EC"),
        Record(timestamp=1100, codepoint="0x001D"),
        Record(timestamp=1200, codepoint="0x11EC"),
    ]
    stats = rollup(records, window_seconds=300)
    assert len(stats) == 1
    w = stats[0]
    assert w.total == 3
    assert w.counts["0x11EC"] == 2
    assert w.counts["0x001D"] == 1
    # 2/3 = 66.6...%
    assert abs(w.percent("0x11EC") - (200.0 / 3)) < 1e-9


def test_window_boundary_is_half_open():
    records = [
        Record(timestamp=0, codepoint="0x11EC"),
        Record(timestamp=300, codepoint="0x001D"),  # exactly at next window's start
    ]
    stats = rollup(records, window_seconds=300)
    assert len(stats) == 2
    assert stats[0].counts["0x11EC"] == 1
    assert stats[0].counts["0x001D"] == 0
    assert stats[1].counts["0x001D"] == 1


def test_unmonitored_codepoint_still_counts_toward_total():
    records = [
        Record(timestamp=0, codepoint="0x11EC"),
        Record(timestamp=50, codepoint="0x0018"),  # secp384r1 — outside the monitored set
    ]
    stats = rollup(records, window_seconds=300)
    assert stats[0].total == 2
    assert stats[0].counts["0x11EC"] == 1
    assert "0x0018" not in stats[0].counts


def test_zero_or_negative_window_raises():
    with pytest.raises(ValueError):
        rollup([Record(timestamp=0, codepoint="0x11EC")], 0)
    with pytest.raises(ValueError):
        rollup([Record(timestamp=0, codepoint="0x11EC")], -1)


def test_read_csv_skips_header_and_comments(tmp_path: Path):
    csv_path = tmp_path / "records.csv"
    csv_path.write_text(
        "timestamp,codepoint\n"
        "# a comment\n"
        "1700000000,0x11EC\n"
        "1700000005,0x001D\n"
        "1700000010,0x11EC\n"
    )
    records = read_csv(csv_path)
    assert len(records) == 3
    assert records[0].timestamp == 1700000000
    assert records[-1].codepoint == "0x11EC"


def test_rollup_over_csv_fixture(tmp_path: Path):
    csv_path = tmp_path / "records.csv"
    lines = ["timestamp,codepoint"]
    for t in range(0, 10):
        lines.append(f"{t},0x11EC")
    for t in range(10, 15):
        lines.append(f"{t},0x001D")
    for t in range(15, 20):
        lines.append(f"{t},0x0017")
    csv_path.write_text("\n".join(lines) + "\n")
    records = read_csv(csv_path)
    stats = rollup(records, window_seconds=300)
    assert len(stats) == 1
    assert stats[0].total == 20
    assert abs(stats[0].percent("0x11EC") - 50.0) < 1e-9
    assert abs(stats[0].percent("0x001D") - 25.0) < 1e-9


def test_monitored_dict_has_expected_codepoints():
    assert "0x11EC" in MONITORED
    assert MONITORED["0x11EC"] == "X25519MLKEM768"
    assert "0x001D" in MONITORED
    assert MONITORED["0x001D"] == "X25519"
