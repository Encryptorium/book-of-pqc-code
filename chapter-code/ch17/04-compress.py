# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 17: SLH-DSA (FIPS 205) from scratch
# Section: "FORS with ADRS and F-function separation"
# https://book.encryptorium.com/part-3-hash-based/ch17-slh-dsa-fips-205/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch17/04-compress.py

import hashlib, struct

n = 16

def compress(ad):
    return bytes([ad[3]]) + bytes(ad[8:16]) + bytes([ad[19]]) + bytes(ad[20:32])

def tw_F(pk_s, ad, m):
    return hashlib.sha256(pk_s + b"\x00"*(64-n) + compress(ad) + m).digest()[:n]

def tw_PRF(pk_s, sk_s, ad):
    return hashlib.sha256(pk_s + b"\x00"*(64-n) + compress(ad) + sk_s).digest()[:n]

def set_type_clear(ad, v):
    struct.pack_into(">I", ad, 16, v)
    ad[20:32] = b"\x00" * 12

def set_kp(ad, v):
    struct.pack_into(">I", ad, 20, v)

def set_idx(ad, v):
    struct.pack_into(">I", ad, 28, v)

def set_height(ad, v):
    struct.pack_into(">I", ad, 24, v)

pk_seed = bytes.fromhex("f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6")
sk_seed = bytes.fromhex("a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6")

ad = bytearray(32)

# Generate FORS secret at tree 0, leaf 5
sk_ad = bytearray(ad); set_type_clear(sk_ad, 6); set_kp(sk_ad, 0)  # FORS_PRF
set_idx(sk_ad, 5)
secret = tw_PRF(pk_seed, sk_seed, sk_ad)

# Hash through F to get the leaf node (F-function separation)
leaf_ad = bytearray(ad); set_type_clear(leaf_ad, 3); set_kp(leaf_ad, 0)  # FORS_TREE
set_height(leaf_ad, 0); set_idx(leaf_ad, 5)
leaf_node = tw_F(pk_seed, leaf_ad, secret)

print(f"FORS secret: {secret.hex()[:16]}...")
print(f"FORS leaf:   {leaf_node.hex()[:16]}...")
print(f"Different:   {secret != leaf_node}")
# ==> FORS secret: ba9ea0e47b175e85...
# ==> FORS leaf:   7663b64f96a03367...
# ==> Different:   True
