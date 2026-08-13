# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 39: Consensus and staking signatures
# Section: "Decide between threshold and per-validator signing"
# https://book.encryptorium.com/part-7-pqc-blockchain/ch39-consensus-staking-signatures/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch39/02-decide-between-threshold-and-per-validator-signing.py

# Block 2: pedagogical slice of consensus_staking.threshold_compare
# (stdlib only).
PRIMITIVES = (
    "BLS-BLS12-381",
    "ML-DSA-65",
    "SLH-DSA-128s",
    "FN-DSA-512",
    "threshold-ML-DSA",
)

# Each cell records the deployment status at chain-tip 2026 across
# three threshold-protocol roles. ``--`` means the cell is not a
# candidate for the operator (incompatible primitive plus role).
MATRIX = {
    "BLS-BLS12-381":    ("production", "classical-only", "--"),
    "ML-DSA-65":        ("fips-final", "--",             "research"),
    "SLH-DSA-128s":     ("fips-final", "--",             "research-early"),
    "FN-DSA-512":       ("pre-draft",  "--",             "research-early"),
    "threshold-ML-DSA": ("research",   "--",             "research"),
}

ROLES = ("no-threshold", "classical-FROST", "threshold-PQ")

print(f"{'primitive':<19} {'no-thr':<14} {'FROST':<16} threshold-PQ")
for primitive in PRIMITIVES:
    a, b, c = MATRIX[primitive]
    print(f"{primitive:<19} {a:<14} {b:<16} {c}")
# ==> primitive           no-thr         FROST            threshold-PQ
# ==> BLS-BLS12-381       production     classical-only   --
# ==> ML-DSA-65           fips-final     --               research
# ==> SLH-DSA-128s        fips-final     --               research-early
# ==> FN-DSA-512          pre-draft      --               research-early
# ==> threshold-ML-DSA    research       --               research
