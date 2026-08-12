# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 27: Hybrid schemes in practice
# Section: "An X25519MLKEM768 handshake"
# https://book.encryptorium.com/part-5-migration-deployment/ch27-hybrid-schemes-in-practice/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch27/01-hkdf-sha256.py

# Block 1: X25519MLKEM768 combiner shape with stubbed ML-KEM, stdlib only.
import hashlib, hmac, os

def hkdf_sha256(ikm, info, length=32):
    prk = hmac.new(b"\x00" * 32, ikm, hashlib.sha256).digest()
    out, t, counter = b"", b"", 1
    while len(out) < length:
        t = hmac.new(prk, t + info + bytes([counter]), hashlib.sha256).digest()
        out += t
        counter += 1
    return out[:length]

def combine(ss_mlkem, ss_x25519):
    # Concatenation order per RFC 10024 Section 4.3: ML-KEM secret first.
    # The label below is a pedagogical stand-in for the TLS 1.3 key schedule.
    return hkdf_sha256(ss_mlkem + ss_x25519, b"tls13 x25519_mlkem768", 32)

# Simulate two independently-generated 32-byte shared secrets.
ss_mlkem_alice = os.urandom(32)
ss_mlkem_bob   = ss_mlkem_alice          # ML-KEM: both sides agree on the same secret.
ss_x25519      = os.urandom(32)          # X25519: both sides derive the same ECDH output.

k_alice = combine(ss_mlkem_alice, ss_x25519)
k_bob   = combine(ss_mlkem_bob,   ss_x25519)
print(k_alice == k_bob, len(k_alice))
# ==> True 32
