# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 17: SLH-DSA (FIPS 205) from scratch
# Section: "ADRS and tweakable hash functions"
# https://book.encryptorium.com/part-3-hash-based/ch17-slh-dsa-fips-205/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch17/01-sha-n.py

import hashlib, struct

n = 16  # hash output bytes
pk_seed = bytes.fromhex("f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6")
value = hashlib.sha256(b"one value").digest()[:n]

def sha_n(data):
    """Chapter 16's leaf hash: SHA-256 truncated to n bytes, and no other input."""
    return hashlib.sha256(data).digest()[:n]

def leaf_adrs(index):
    ad = bytearray(32)                     # layer, tree and keypair address 0
    struct.pack_into(">I", ad, 16, 3)      # type 3, FORS_TREE; tree height 0
    struct.pack_into(">I", ad, 28, index)  # tree index: which leaf
    return ad

def compress(ad):  # the 22 of the address's 32 bytes that F hashes
    return bytes([ad[3]]) + bytes(ad[8:16]) + bytes([ad[19]]) + bytes(ad[20:32])

def f_input(pk_s, ad, m):
    """What SHA-256 hashes inside F."""
    return pk_s + b"\x00"*(64-n) + compress(ad) + m

def tw_F(pk_s, ad, m):
    return hashlib.sha256(f_input(pk_s, ad, m)).digest()[:n]

# One value hashed into the leaf at index 5, and the same value at index 6
for index in (5, 6):
    ad = leaf_adrs(index)
    print(f"leaf {index}: sha_n {sha_n(value).hex()[:16]}...  "
          f"F {tw_F(pk_seed, ad, value).hex()[:16]}...")
in_5 = f_input(pk_seed, leaf_adrs(5), value)
in_6 = f_input(pk_seed, leaf_adrs(6), value)
print(f"F inputs differ: {in_5 != in_6}")
# ==> leaf 5: sha_n 821718ddb2e0d51e...  F 479205c2592aeadd...
# ==> leaf 6: sha_n 821718ddb2e0d51e...  F 78b2ea28bd060b80...
# ==> F inputs differ: True
