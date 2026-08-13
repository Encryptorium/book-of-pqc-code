# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 36: Quantum threat model for blockchains
# Section: "The five surfaces"
# https://book.encryptorium.com/part-7-pqc-blockchain/ch36-blockchain-threat-model/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch36/02-mosca-window.py

# Block 2: pedagogical slice of blockchain_threat.mosca_window.evaluate (stdlib only).

# Z = 9 models a 2035 planning scenario measured from 2026. NCSC and
# NSM-10 / CNSA 2.0 use 2035 as a migration deadline, not as a
# predicted CRQC arrival date.
Z_2035_PLANNING = 9

STRAND_XY = [
    ("transaction",       50, 5),
    ("consensus",          2, 1),
    ("wallet",            10, 4),
    ("on-chain-verifier",  3, 2),
    ("governance",         4, 3),
]


def mosca_window(x, y, z):
    assert x >= 0 and y >= 0 and z >= 0
    breach = x + y - z
    return breach if breach > 0 else 0


for surface, x, y in STRAND_XY:
    window = mosca_window(x, y, Z_2035_PLANNING)
    flag = "BREACH" if window > 0 else "ok"
    print(f"{surface:<18} X={x:>2} Y={y:>2} Z={Z_2035_PLANNING:>2}  window={window:>2}  {flag}")
# ==> transaction        X=50 Y= 5 Z= 9  window=46  BREACH
# ==> consensus          X= 2 Y= 1 Z= 9  window= 0  ok
# ==> wallet             X=10 Y= 4 Z= 9  window= 5  BREACH
# ==> on-chain-verifier  X= 3 Y= 2 Z= 9  window= 0  ok
# ==> governance         X= 4 Y= 3 Z= 9  window= 0  ok
