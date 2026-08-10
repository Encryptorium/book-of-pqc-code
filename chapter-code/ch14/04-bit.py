# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 14: One-time signatures from hash functions
# Section: "Why "one-time" is load-bearing"
# https://book.encryptorium.com/part-3-hash-based/ch14-one-time-signatures-from-hash/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch14/04-bit.py

import hashlib

seed = b"ch14-full"
n = 256

sk = []
pk = []
for i in range(n):
    s0 = hashlib.sha256(seed + (2 * i).to_bytes(4, "big")).digest()
    s1 = hashlib.sha256(seed + (2 * i + 1).to_bytes(4, "big")).digest()
    sk.append((s0, s1))
    pk.append((hashlib.sha256(s0).digest(), hashlib.sha256(s1).digest()))

def bit(digest, i):
    return (digest[i // 8] >> (7 - (i % 8))) & 1

m1 = b"first message"
m2 = b"second message"
d1 = hashlib.sha256(m1).digest()
d2 = hashlib.sha256(m2).digest()

sig1 = [sk[i][bit(d1, i)] for i in range(n)]
sig2 = [sk[i][bit(d2, i)] for i in range(n)]

hamming = sum(bin(a ^ b).count("1") for a, b in zip(d1, d2))
print(hamming)
# ==> 132
