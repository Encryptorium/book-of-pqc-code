# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 27: Hybrid schemes in practice
# Section: "The X25519MLKEM768 hybrid KEM"
# https://book.encryptorium.com/part-5-migration-deployment/ch27-hybrid-schemes-in-practice/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch27/02-hkdf-sha256.py

# Block 2: end-to-end round-trip with two stubbed component KEMs, stdlib only.
import hashlib, hmac, os

def hkdf_sha256(ikm, info, length=32):
    prk = hmac.new(b"\x00" * 32, ikm, hashlib.sha256).digest()
    out, t, counter = b"", b"", 1
    while len(out) < length:
        t = hmac.new(prk, t + info + bytes([counter]), hashlib.sha256).digest()
        out += t
        counter += 1
    return out[:length]

# Stand-in KEM: a mock whose keygen/encaps agree on a deterministic shared secret.
def stub_keygen(seed):
    return hashlib.sha256(b"pk" + seed).digest(), seed

def stub_encaps(pk, rand):
    ss = hashlib.sha256(b"ss" + pk + rand).digest()
    ct = hashlib.sha256(b"ct" + pk + rand).digest()
    return ct, ss

# Round-trip the hybrid. Two stubs play the ML-KEM and X25519 roles.
pk_a, sk_a = stub_keygen(b"alice-mlkem-seed".ljust(32, b"0"))
pk_b, sk_b = stub_keygen(b"alice-x25519-seed".ljust(32, b"0"))
ct1, ss1 = stub_encaps(pk_a, b"m1".ljust(32, b"0"))
ct2, ss2 = stub_encaps(pk_b, b"m2".ljust(32, b"0"))
k = hkdf_sha256(ss1 + ss2, b"tls13 x25519_mlkem768")
print(len(k), k.hex()[:16])
# ==> 32 e9c2d5701e91f142
