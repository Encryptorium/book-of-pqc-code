# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 14: One-time signatures from hash functions
# Section: "Merkle tree at depth 3"
# https://book.encryptorium.com/part-3-hash-based/ch14-one-time-signatures-from-hash/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch14/05-merkle-tree-at-depth-3.py

import hashlib

leaves = [hashlib.sha256(f"leaf-{i}".encode()).digest() for i in range(8)]

# Build the tree as a 1-indexed flat array of length 16.
# Indices 8..15 are leaves; indices 1..7 are internal nodes; index 0 is unused.
tree = [b""] * 16
for i in range(8):
    tree[8 + i] = leaves[i]
for i in range(7, 0, -1):
    tree[i] = hashlib.sha256(tree[2 * i] + tree[2 * i + 1]).digest()

root = tree[1]
print(root.hex()[:16])
# ==> 6e421edd382a1e45
