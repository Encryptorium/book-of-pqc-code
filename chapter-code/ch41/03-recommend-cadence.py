# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 41: Governance, hard forks, and migration case studies
# Section: "Plan the governance-rotation cadence"
# https://book.encryptorium.com/part-7-pqc-blockchain/ch41-governance-hard-forks-case-studies/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch41/03-recommend-cadence.py

# Block 3: pedagogical slice of governance.governance_mosca
# (stdlib only). Recommends a governance-rotation cadence under
# the Strand governance anchor (X=4, Y=3) per the Ch 36 fixture.

X, Y = 4, 3  # Strand governance surface anchor.
SCENARIO_Z_VALUES = {"narrow": 6, "central": 9, "wide": 13}

def recommend_cadence(X, Y, Z):
    breach = X + Y - Z
    safe_window = max(0, Z - Y)
    if breach <= 0:
        return ("governance-trigger", breach, safe_window, 0)
    if safe_window >= 1:
        return ("every-N-vote-cycles", breach, safe_window, safe_window)
    return ("hard-fork-trigger", breach, safe_window, 0)

for scenario, Z in SCENARIO_Z_VALUES.items():
    cadence, breach, safe_window, interval = recommend_cadence(X, Y, Z)
    print(
        f"{scenario:8s} Z={Z:2d} breach={breach:+3d} "
        f"safe_window={safe_window:2d} interval={interval:2d} "
        f"cadence={cadence}"
    )
# ==> narrow   Z= 6 breach= +1 safe_window= 3 interval= 3 cadence=every-N-vote-cycles
# ==> central  Z= 9 breach= -2 safe_window= 6 interval= 0 cadence=governance-trigger
# ==> wide     Z=13 breach= -6 safe_window=10 interval= 0 cadence=governance-trigger
