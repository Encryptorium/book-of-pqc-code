# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 36: Quantum threat model for blockchains
# Section: "The five surfaces"
# https://book.encryptorium.com/part-7-pqc-blockchain/ch36-blockchain-threat-model/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch36/01-classify.py

# Block 1: pedagogical slice of blockchain_threat.surface_taxonomy.classify_all (stdlib only).
PRIMITIVE_CLASSIFICATION = {
    "ECDSA-secp256k1":   "shor-vulnerable",
    "Schnorr-secp256k1": "shor-vulnerable",
    "BLS-BLS12-381":     "shor-vulnerable",
    "EdDSA-Ed25519":     "shor-vulnerable",
    "SHA-256":           "hash-quantum-degraded",
    "ML-DSA-65":         "post-quantum-standardized",
    "SLH-DSA-128s":      "post-quantum-standardized",
}

STRAND_ASSETS = [
    {"surface": "transaction",       "primitive": "ECDSA-secp256k1"},
    {"surface": "consensus",         "primitive": "BLS-BLS12-381"},
    {"surface": "wallet",            "primitive": "ECDSA-secp256k1"},
    {"surface": "on-chain-verifier", "primitive": "SHA-256"},
    {"surface": "governance",        "primitive": "Schnorr-secp256k1"},
]


def classify(asset):
    primitive = asset["primitive"]
    assert primitive in PRIMITIVE_CLASSIFICATION, f"unknown primitive: {primitive!r}"
    return PRIMITIVE_CLASSIFICATION[primitive]


for asset in STRAND_ASSETS:
    print(f"{asset['surface']:<18} {asset['primitive']:<19} {classify(asset)}")
# ==> transaction        ECDSA-secp256k1     shor-vulnerable
# ==> consensus          BLS-BLS12-381       shor-vulnerable
# ==> wallet             ECDSA-secp256k1     shor-vulnerable
# ==> on-chain-verifier  SHA-256             hash-quantum-degraded
# ==> governance         Schnorr-secp256k1   shor-vulnerable
