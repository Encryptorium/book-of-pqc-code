# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 14: One-time signatures from hash functions
# Section: "A Lamport signature at eight bits"
# https://book.encryptorium.com/part-3-hash-based/ch14-one-time-signatures-from-hash/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch14/01-a-lamport-signature-at-eight-bits.py

import hashlib

seed = b"ch14-toy"
n = 8

# Key generation: 8 secret pairs and their SHA-256 public-key hashes.
sk = []
pk = []
for i in range(n):
    s0 = hashlib.sha256(seed + (2 * i).to_bytes(4, "big")).digest()
    s1 = hashlib.sha256(seed + (2 * i + 1).to_bytes(4, "big")).digest()
    sk.append((s0, s1))
    pk.append((hashlib.sha256(s0).digest(), hashlib.sha256(s1).digest()))

# Sign the single-byte message 0xA3.
message = bytes([0xA3])
digest = hashlib.sha256(message).digest()

# Extract the first 8 bits of the digest (MSB-first within the byte).
bits = [(digest[0] >> (7 - i)) & 1 for i in range(8)]
print(bits)
# ==> [0, 1, 1, 0, 1, 1, 0, 1]

# The signature reveals one secret per digest bit.
sig = [sk[i][bits[i]] for i in range(n)]

# Verification: hash each revealed secret and compare.
ok = all(
    hashlib.sha256(sig[i]).digest() == pk[i][bits[i]]
    for i in range(n)
)
print(ok)
# ==> True
