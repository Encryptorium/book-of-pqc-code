# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 25: Inventory first: CBOM
# Section: "From source code to CBOM JSON"
# https://book.encryptorium.com/part-5-migration-deployment/ch25-inventory-first-cbom/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch25/02-status.py

# Block 2: the three-family quantum-vulnerability lookup.
VULNERABLE = "vulnerable"
GROVER_ONLY = "grover-only"
QUANTUM_SAFE = "quantum-safe"
UNKNOWN = "unknown"

FAMILIES = {
    "RSA": VULNERABLE, "DSA": VULNERABLE, "ECDSA": VULNERABLE,
    "ECDHE": VULNERABLE, "ECDH": VULNERABLE, "DH": VULNERABLE,
    "AES": GROVER_ONLY, "SHA-256": GROVER_ONLY,
    "SHA-384": GROVER_ONLY, "SHA-512": GROVER_ONLY,
    "HMAC": GROVER_ONLY, "PBKDF2": GROVER_ONLY,
    "ML-KEM": QUANTUM_SAFE, "ML-DSA": QUANTUM_SAFE,
    "SLH-DSA": QUANTUM_SAFE,
}

def status(family):
    return FAMILIES.get(family, UNKNOWN)

def touchpoint_status(families):
    if not families: return UNKNOWN  # an empty entry is a gap, not safe
    ordered = [status(f) for f in families]
    if VULNERABLE in ordered: return VULNERABLE
    if UNKNOWN in ordered:    return UNKNOWN
    if GROVER_ONLY in ordered: return GROVER_ONLY
    return QUANTUM_SAFE

print(status("RSA"), status("HMAC"), status("ML-KEM"), status("Frobnitz"))
# ==> vulnerable grover-only quantum-safe unknown
print(touchpoint_status(["ECDHE", "ECDSA", "AES", "SHA-384"]))
# ==> vulnerable
print(touchpoint_status(["HMAC", "SHA-256"]))
# ==> grover-only
