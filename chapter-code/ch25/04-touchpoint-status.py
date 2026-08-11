# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 25: Inventory first: CBOM
# Section: "From source code to CBOM JSON"
# https://book.encryptorium.com/part-5-migration-deployment/ch25-inventory-first-cbom/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch25/04-touchpoint-status.py

# Block 4: assemble the full CBOM and print the inventory summary.
TOUCHPOINTS = [
    {"name": "tls_endpoint_api", "primitive": "key-agree",
     "exposure": "public", "families": ["ECDHE", "ECDSA", "AES", "SHA-384"]},
    {"name": "jwt_signing", "primitive": "signature",
     "exposure": "internal", "families": ["RSA", "SHA-256"]},
    {"name": "password_hashing", "primitive": "kdf",
     "exposure": "internal", "families": ["PBKDF2", "HMAC", "SHA-256"]},
    {"name": "webhook_hmac", "primitive": "mac",
     "exposure": "internal", "families": ["HMAC", "SHA-256"]},
    {"name": "blockchain_validator_sig", "primitive": "signature",
     "exposure": "public", "families": ["ECDSA", "SHA-256"]},
]

FAMILIES = {
    "ECDHE": "vulnerable", "ECDSA": "vulnerable", "AES": "grover-only",
    "SHA-384": "grover-only", "RSA": "vulnerable", "SHA-256": "grover-only",
    "PBKDF2": "grover-only", "HMAC": "grover-only",
}

def touchpoint_status(families):
    if not families: return "unknown"
    ordered = [FAMILIES.get(f, "unknown") for f in families]
    if "vulnerable" in ordered:  return "vulnerable"
    if "unknown" in ordered:     return "unknown"
    if "grover-only" in ordered: return "grover-only"
    return "quantum-safe"

print(f"{'touchpoint':<24} {'primitive':<12} {'exposure':<10} {'status'}")
for t in TOUCHPOINTS:
    print(f"{t['name']:<24} {t['primitive']:<12} {t['exposure']:<10} "
          f"{touchpoint_status(t['families'])}")
# ==> touchpoint               primitive    exposure   status
# ==> tls_endpoint_api         key-agree    public     vulnerable
# ==> jwt_signing              signature    internal   vulnerable
# ==> password_hashing         kdf          internal   grover-only
# ==> webhook_hmac             mac          internal   grover-only
# ==> blockchain_validator_sig signature    public     vulnerable
