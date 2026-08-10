# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 14: One-time signatures from hash functions
# Section: "Authentication paths"
# https://book.encryptorium.com/part-3-hash-based/ch14-one-time-signatures-from-hash/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch14/06-authentication-paths.py

import hashlib

leaves = [hashlib.sha256(f"leaf-{i}".encode()).digest() for i in range(8)]
tree = [b""] * 16
for i in range(8):
    tree[8 + i] = leaves[i]
for i in range(7, 0, -1):
    tree[i] = hashlib.sha256(tree[2 * i] + tree[2 * i + 1]).digest()

# Extract the authentication path for leaf 3.
leaf_index = 3
node = 8 + leaf_index  # = 11
path = []
for _ in range(3):
    sibling = node ^ 1  # XOR flips the last bit to get the sibling index.
    path.append(tree[sibling])
    node //= 2  # Move to the parent.

# Verify the path by recomputing the root from the leaf upward.
current = leaves[3]
idx = leaf_index
for s in path:
    if idx % 2 == 0:
        current = hashlib.sha256(current + s).digest()
    else:
        current = hashlib.sha256(s + current).digest()
    idx //= 2

print(current == tree[1])
# ==> True
