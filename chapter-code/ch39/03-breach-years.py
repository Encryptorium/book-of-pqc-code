# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 39: Consensus and staking signatures
# Section: "Plan the validator-key rotation cadence"
# https://book.encryptorium.com/part-7-pqc-blockchain/ch39-consensus-staking-signatures/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch39/03-breach-years.py

# Block 3: pedagogical slice of consensus_staking.consensus_mosca
# (stdlib only).
def breach_years(X, Y, Z):
    return X + Y - Z


def recommend(X, Y, Z):
    breach = breach_years(X, Y, Z)
    safe_window = max(0, Z - Y)
    if breach <= 0:
        return ("per-epoch", 0)
    if safe_window >= 1:
        return ("every-N-epochs", safe_window)
    return ("hard-fork-trigger", 0)


# Strand consensus surface from Ch 36: X=2, Y=1.
X, Y = 2, 1
SCENARIOS = (
    ("aggressive   Z=0",  0),
    ("narrow       Z=2",  2),
    ("ncsc-2035    Z=9",  9),
    ("mid-2040     Z=14", 14),
)
for label, Z in SCENARIOS:
    cadence, N = recommend(X, Y, Z)
    breach = breach_years(X, Y, Z)
    print(f"{label}: breach={breach:>4}y -> {cadence}, N={N}y")
# ==> aggressive   Z=0: breach=   3y -> hard-fork-trigger, N=0y
# ==> narrow       Z=2: breach=   1y -> every-N-epochs, N=1y
# ==> ncsc-2035    Z=9: breach=  -6y -> per-epoch, N=0y
# ==> mid-2040     Z=14: breach= -11y -> per-epoch, N=0y
