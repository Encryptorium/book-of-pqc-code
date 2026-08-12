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
    # EXERCISE: implement this function.
    #
    # Bucket the records into fixed-width windows aligned to the earliest
    # timestamp. Reject a non-positive window_seconds with ValueError and
    # return an empty list for empty input. Sort by timestamp, set the
    # cursor to the first timestamp, and walk windows while the cursor is at
    # or below the last timestamp. Each window starts a counts dict with an
    # explicit zero for every monitored codepoint, so a codepoint that never
    # appears reports 0 rather than being absent. Consume records while
    # their timestamp is strictly below cursor + window_seconds, which is
    # what makes the interval half-open and puts a record landing exactly on
    # a boundary in the next window. Every consumed record raises the window
    # total; only monitored ones raise a per-codepoint count, so an
    # unmonitored group still shows up in the denominator. Advance the
    # cursor by the full window width rather than to the next record, so a
    # quiet period emits empty windows instead of being skipped.
    #
    # Reference: Chapter 28, 'Progressive rollout'
    #
    # Proved by:
    #   tests/ch28/test_named_group_rollup.py
    raise NotImplementedError("exercise: rollup")


def read_csv(path: str | Path) -> list[Record]:
    """Load records from a two-column CSV: ``timestamp, codepoint``."""
    # EXERCISE: implement this function.
    #
    # Read a two-column CSV of timestamp and codepoint into Record objects
    # with csv.reader. Skip rows that are empty, whose first field is blank,
    # whose first field starts with '#', or whose first field is the literal
    # 'timestamp' in any case; that last one is the header line. Parse the
    # timestamp with int() and strip the codepoint field. Connection logs
    # arrive with comments and a header, so a loader that does not drop them
    # fails at int() on the first line.
    #
    # Reference: Chapter 28, 'Progressive rollout'
    #
    # Proved by:
    #   tests/ch28/test_named_group_rollup.py
    raise NotImplementedError("exercise: read_csv")
