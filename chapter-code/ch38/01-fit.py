# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 38: Wallets, addresses, and key rotation
# Section: "Pick the candidate per custody shape"
# https://book.encryptorium.com/part-7-pqc-blockchain/ch38-wallets-addresses-key-rotation/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch38/01-fit.py

# Block 1: pedagogical slice of wallet_rotation.custody_fit (stdlib only).
SHAPES = ("hot1", "hot+", "cold-hw", "msig")

PRIMS = {
    "ECDSA-secp256k1":   {"legacy": True,  "state": (1, 1, 1, 1), "marginal": (0, 0, 0, 0)},
    "ML-DSA-65":         {"legacy": False, "state": (1, 1, 1, 1), "marginal": (0, 0, 0, 0)},
    "SLH-DSA-128s":      {"legacy": False, "state": (1, 1, 1, 1), "marginal": (1, 1, 0, 0)},
    "Ed25519+ML-DSA-65": {"legacy": False, "state": (1, 1, 1, 1), "marginal": (0, 0, 0, 0)},
    "XMSS-MT":           {"legacy": False, "state": (1, 0, 1, 0), "marginal": (1, 0, 0, 0)},
    "LMS":               {"legacy": False, "state": (1, 0, 1, 0), "marginal": (1, 0, 0, 0)},
}


def fit(primitive, idx):
    p = PRIMS[primitive]
    if p["legacy"]:
        return "legacy"
    if not p["state"][idx]:
        return "unfit"
    return "marginal" if p["marginal"][idx] else "fit"


print(f"{'primitive':<19} {'hot1':<10} {'hot+':<10} {'cold-hw':<10} msig")
for primitive in PRIMS:
    a = fit(primitive, 0)
    b = fit(primitive, 1)
    c = fit(primitive, 2)
    d = fit(primitive, 3)
    print(f"{primitive:<19} {a:<10} {b:<10} {c:<10} {d}")
# ==> primitive           hot1       hot+       cold-hw    msig
# ==> ECDSA-secp256k1     legacy     legacy     legacy     legacy
# ==> ML-DSA-65           fit        fit        fit        fit
# ==> SLH-DSA-128s        marginal   marginal   fit        fit
# ==> Ed25519+ML-DSA-65   fit        fit        fit        fit
# ==> XMSS-MT             marginal   unfit      fit        unfit
# ==> LMS                 marginal   unfit      fit        unfit
