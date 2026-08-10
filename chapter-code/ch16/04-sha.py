# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 16: FORS and the stateless hypertree
# Section: "FORS at teaching parameters"
# https://book.encryptorium.com/part-3-hash-based/ch16-fors-and-stateless-hypertree/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch16/04-sha.py

import hashlib

def sha(data):
    return hashlib.sha256(data).digest()

seed = b"ch16-fors-teach"
k, t, n = 6, 16, 32

roots_concat = b""
for j in range(k):
    leaves = []
    for i in range(t):
        leaf = sha(seed + b"fors" + j.to_bytes(4, "big") + i.to_bytes(4, "big"))[:n]
        leaves.append(leaf)
    tree = [b""] * (2 * t)
    for i, lf in enumerate(leaves):
        tree[t + i] = lf
    for i in range(t - 1, 0, -1):
        tree[i] = sha(tree[2 * i] + tree[2 * i + 1])
    roots_concat += tree[1]

pk = sha(roots_concat)[:n]
print(f"pk: {pk.hex()[:16]}...")
# ==> pk: 957d094bad6b0cf9...
print(f"Secret key: {k * t * n} bytes")
# ==> Secret key: 3072 bytes
print(f"Signature: {k * (n + 4 * n)} bytes")
# ==> Signature: 960 bytes
print(f"Public key: {n} bytes")
# ==> Public key: 32 bytes
