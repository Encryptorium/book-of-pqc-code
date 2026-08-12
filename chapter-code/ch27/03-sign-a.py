# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 27: Hybrid schemes in practice
# Section: "ML-DSA-65+Ed25519 composite signatures"
# https://book.encryptorium.com/part-5-migration-deployment/ch27-hybrid-schemes-in-practice/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch27/03-sign-a.py

# Block 3: AND-mode explicit-composite sign/verify with HMAC stand-ins, stdlib only.
import hashlib, hmac

SECRET_A = b"ed25519-sk-stand-in"
SECRET_B = b"mldsa-sk-stand-in"

def sign_a(msg): return hmac.new(SECRET_A, msg, hashlib.sha256).digest()
def sign_b(msg): return hmac.new(SECRET_B, msg, hashlib.sha512).digest()
def verify_a(msg, sig): return hmac.compare_digest(sig, sign_a(msg))
def verify_b(msg, sig): return hmac.compare_digest(sig, sign_b(msg))

def composite_sign(msg):
    return sign_a(msg) + sign_b(msg)

def composite_verify(msg, sig):
    sa, sb = sig[:32], sig[32:]
    # AND-mode: both components must pass.
    # Python's `and` short-circuits, so a failed verify_a skips verify_b.
    # That is fine for a stdlib toy. Production verifiers evaluate both
    # halves regardless to avoid partial-validity state and timing leaks.
    return verify_a(msg, sa) and verify_b(msg, sb)

msg = b"webhook-payload-2026-04-17"
sig = composite_sign(msg)
tampered_ed = bytes([sig[0] ^ 1]) + sig[1:]
tampered_mldsa = sig[:32] + bytes([sig[32] ^ 1]) + sig[33:]
print(composite_verify(msg, sig),
      composite_verify(msg, tampered_ed),
      composite_verify(msg, tampered_mldsa))
# ==> True False False
