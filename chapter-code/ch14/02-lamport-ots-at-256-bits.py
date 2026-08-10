# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 14: One-time signatures from hash functions
# Section: "Lamport OTS at 256 bits"
# https://book.encryptorium.com/part-3-hash-based/ch14-one-time-signatures-from-hash/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch14/02-lamport-ots-at-256-bits.py

import hashlib

seed = b"ch14-full"
n = 256

# Key generation at n = 256.
sk = []
pk = []
for i in range(n):
    s0 = hashlib.sha256(seed + (2 * i).to_bytes(4, "big")).digest()
    s1 = hashlib.sha256(seed + (2 * i + 1).to_bytes(4, "big")).digest()
    sk.append((s0, s1))
    pk.append((hashlib.sha256(s0).digest(), hashlib.sha256(s1).digest()))

print(n * 2 * 32)
# ==> 16384
print(n * 32)
# ==> 8192
