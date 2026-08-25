# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 39: Consensus and staking signatures
# Section: "Pick the candidate per validator-set byte budget"
# https://book.encryptorium.com/part-7-pqc-blockchain/ch39-consensus-staking-signatures/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch39/01-per-set-bytes.py

# Block 1: pedagogical slice of consensus_staking.aggregation_overhead
# (stdlib only).
N = 1_000_000  # Ethereum mainnet round-figure anchor.
BLS_AGG_BYTES = 96  # canonical G2 aggregate signature size.

CANDIDATES = {
    "BLS-BLS12-381":    {"sig_bytes":   96, "aggregates": True},
    "ML-DSA-65":        {"sig_bytes": 3309, "aggregates": False},
    "SLH-DSA-128s":     {"sig_bytes": 7856, "aggregates": False},
    "FN-DSA-512":       {"sig_bytes":  666, "aggregates": False},
    "threshold-ML-DSA": {"sig_bytes": 3309, "aggregates": True},
}


def per_set_bytes(primitive, N):
    spec = CANDIDATES[primitive]
    bitmap_bytes = (N + 7) // 8  # one bit per validator, byte-aligned.
    if primitive == "BLS-BLS12-381":
        return BLS_AGG_BYTES + bitmap_bytes
    if primitive == "threshold-ML-DSA":
        # One combined ML-DSA-65 signature plus the per-validator
        # participation bitmap the chain records for rewards. Unlike
        # BLS's bitmap it is not an input to verification.
        return spec["sig_bytes"] + bitmap_bytes
    return N * spec["sig_bytes"]


baseline = per_set_bytes("BLS-BLS12-381", N)
print(f"{'primitive':<19} {'per-set bytes':>15} {'factor vs BLS':>15}")
for primitive in CANDIDATES:
    total = per_set_bytes(primitive, N)
    factor = total / baseline
    print(f"{primitive:<19} {total:>15,} {factor:>15.2f}")
# ==> primitive             per-set bytes   factor vs BLS
# ==> BLS-BLS12-381               125,096            1.00
# ==> ML-DSA-65             3,309,000,000        26451.69
# ==> SLH-DSA-128s          7,856,000,000        62799.77
# ==> FN-DSA-512              666,000,000         5323.91
# ==> threshold-ML-DSA            128,309            1.03
