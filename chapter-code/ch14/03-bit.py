# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 14: One-time signatures from hash functions
# Section: "Lamport OTS at 256 bits"
# https://book.encryptorium.com/part-3-hash-based/ch14-one-time-signatures-from-hash/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch14/03-bit.py

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

message = b"The Encryptorium Book of PQC"
digest = hashlib.sha256(message).digest()

sig = [sk[i][bit(digest, i)] for i in range(n)]
ok = all(
    hashlib.sha256(sig[i]).digest() == pk[i][bit(digest, i)]
    for i in range(n)
)
print(ok)
# ==> True
