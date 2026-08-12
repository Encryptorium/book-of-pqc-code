# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 28: TLS 1.3 migration
# Section: "Progressive rollout"
# https://book.encryptorium.com/part-5-migration-deployment/ch28-tls-migration/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch28/03-rollup.py

# Block 3: pedagogical slice of rollup (stdlib only).
from collections import Counter

MONITORED = {"0x001D": "X25519", "0x11EC": "X25519MLKEM768"}

def rollup(records, window_seconds):
    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive")
    sorted_records = sorted(records)
    origin = sorted_records[0][0]
    last = sorted_records[-1][0]
    out = []
    cursor = origin
    i = 0
    n = len(sorted_records)
    while cursor <= last:
        end = cursor + window_seconds
        counts = Counter()
        total = 0
        while i < n and sorted_records[i][0] < end:
            _, code = sorted_records[i]
            total += 1
            if code in MONITORED:
                counts[code] += 1
            i += 1
        out.append((cursor, total, dict(counts)))
        cursor = end
    return out

records = [
    (0, "0x11EC"), (30, "0x11EC"), (60, "0x001D"),
    (300, "0x11EC"), (330, "0x11EC"), (360, "0x11EC"),
]

for start, total, counts in rollup(records, window_seconds=300):
    pct = 100.0 * counts.get("0x11EC", 0) / total if total else 0.0
    print(f"t={start}s total={total} X25519MLKEM768={pct:.1f}%")
# ==> t=0s total=3 X25519MLKEM768=66.7%
# ==> t=300s total=3 X25519MLKEM768=100.0%
