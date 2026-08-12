# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 26: Crypto agility
# Section: "Modular cryptographic architecture"
# https://book.encryptorium.com/part-5-migration-deployment/ch26-crypto-agility/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch26/03-sign.py

# Block 3: a registry with the SP 800-131A four-state vocabulary.
import hashlib, hmac

REGISTRY = {
    "HMAC-MD5":    {"hash": hashlib.md5,    "state": "disallowed"},
    "HMAC-SHA1":   {"hash": hashlib.sha1,   "state": "deprecated"},
    "HMAC-SHA256": {"hash": hashlib.sha256, "state": "acceptable"},
    "HMAC-SHA512": {"hash": hashlib.sha512, "state": "acceptable"},
}

POLICY = {
    "webhook_hmac":     "HMAC-SHA256",
    "internal_bus":     "HMAC-SHA512",
    "legacy_connector": "HMAC-SHA1",
}

def sign(touchpoint, key, body):
    alg = POLICY[touchpoint]
    entry = REGISTRY[alg]
    if entry["state"] in ("disallowed", "deprecated"):
        raise ValueError(f"{alg} is {entry['state']}")
    return alg, hmac.new(key, body, entry["hash"]).digest()

alg, sig = sign("webhook_hmac", b"key", b"body")
print(alg, len(sig))
try:
    sign("legacy_connector", b"key", b"body")
except ValueError as e:  # expected: policy rejects HMAC-SHA1 (deprecated)
    print(e)
# ==> HMAC-SHA256 32
# ==> HMAC-SHA1 is deprecated
