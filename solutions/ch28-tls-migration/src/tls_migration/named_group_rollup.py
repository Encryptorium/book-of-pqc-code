"""Per-window adoption rollup for TLS NamedGroup connection records.

Ingests a list of ``(timestamp_seconds, codepoint_hex)`` records and
returns per-window totals plus per-codepoint counts and percentages.
Monitored codepoints are the IANA TLS Supported Groups relevant to a
post-quantum rollout:

- ``0x001D`` X25519
- ``0x0017`` secp256r1
- ``0x11EB`` SecP256r1MLKEM768
- ``0x11EC`` X25519MLKEM768
- ``0x11ED`` SecP384r1MLKEM1024

Windows are half-open intervals ``[w, w + window_seconds)`` aligned to
the first record's timestamp. Records outside the monitored set are
counted toward the window total but do not appear in the per-codepoint
breakdown. A non-positive ``window_seconds`` raises ``ValueError``; a
malformed CSV row propagates ``ValueError`` from ``int()``. An empty
``records`` list returns an empty list.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


MONITORED: dict[str, str] = {
    "0x001D": "X25519",
    "0x0017": "secp256r1",
    "0x11EB": "SecP256r1MLKEM768",
    "0x11EC": "X25519MLKEM768",
    "0x11ED": "SecP384r1MLKEM1024",
}


@dataclass(frozen=True)
class Record:
    """One TLS handshake observation."""

    timestamp: int
    codepoint: str


@dataclass(frozen=True)
class WindowStats:
    """Aggregated per-window counts and a convenience percentage method."""

    window_start: int
    window_end: int
    total: int
    counts: dict[str, int]

    def percent(self, codepoint: str) -> float:
        if self.total == 0:
            return 0.0
        return 100.0 * self.counts.get(codepoint, 0) / self.total


def rollup(records: list[Record], window_seconds: int) -> list[WindowStats]:
    """Compute per-window totals and per-codepoint counts."""
    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive")
    if not records:
        return []

    sorted_records = sorted(records, key=lambda r: r.timestamp)
    origin = sorted_records[0].timestamp
    last = sorted_records[-1].timestamp

    out: list[WindowStats] = []
    cursor = origin
    i = 0
    n = len(sorted_records)
    while cursor <= last:
        counts = {code: 0 for code in MONITORED}
        total = 0
        window_end = cursor + window_seconds
        while i < n and sorted_records[i].timestamp < window_end:
            r = sorted_records[i]
            total += 1
            if r.codepoint in counts:
                counts[r.codepoint] += 1
            i += 1
        out.append(WindowStats(
            window_start=cursor,
            window_end=window_end,
            total=total,
            counts=counts,
        ))
        cursor = window_end
    return out


def read_csv(path: str | Path) -> list[Record]:
    """Load records from a two-column CSV: ``timestamp, codepoint``."""
    path = Path(path)
    out: list[Record] = []
    with path.open() as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            head = row[0].strip()
            if not head or head.startswith("#") or head.lower() == "timestamp":
                continue
            out.append(Record(timestamp=int(head), codepoint=row[1].strip()))
    return out
