# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 40: Quantum threats to ZK rollups
# Section: "Plan the verifier-upgrade cadence"
# https://book.encryptorium.com/part-7-pqc-blockchain/ch40-zk-rollups-under-quantum/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch40/03-breach-years.py

# Block 3: pedagogical slice of zk_rollups.verifier_mosca
# (stdlib only).
def breach_years(X, Y, Z):
    return X + Y - Z


def recommend(X, Y, Z):
    breach = breach_years(X, Y, Z)
    safe_window = max(0, Z - Y)
    # The second tuple element is the rotation interval the
    # recommendation prescribes. governance-trigger and
    # hard-fork-trigger are event-driven and carry interval 0.
    if breach <= 0:
        return ("governance-trigger", 0)
    if safe_window >= 1:
        return ("every-N-rollup-cycles", safe_window)
    return ("hard-fork-trigger", 0)


# Strand on-chain-verifier surface from Ch 36: X=3, Y=2.
X, Y = 3, 2
SCENARIOS = (
    ("narrow    Z=4",  4),
    ("central   Z=9",  9),
    ("wide      Z=13", 13),
)
for label, Z in SCENARIOS:
    cadence, interval = recommend(X, Y, Z)
    breach = breach_years(X, Y, Z)
    safe_window = max(0, Z - Y)
    print(f"{label}: breach={breach:>3}y -> {cadence}, interval={interval}y, safe_window={safe_window}y")
# ==> narrow    Z=4: breach=  1y -> every-N-rollup-cycles, interval=2y, safe_window=2y
# ==> central   Z=9: breach= -4y -> governance-trigger, interval=0y, safe_window=7y
# ==> wide      Z=13: breach= -8y -> governance-trigger, interval=0y, safe_window=11y
