# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 16: FORS and the stateless hypertree
# Section: "FORS at toy parameters"
# https://book.encryptorium.com/part-3-hash-based/ch16-fors-and-stateless-hypertree/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch16/01-sha-n.py

import hashlib

def sha_n(data, n=4):
    """SHA-256 truncated to n bytes."""
    return hashlib.sha256(data).digest()[:n]

seed = b"ch16-fors-toy"
k, t, n = 3, 4, 4

# Generate k trees of t secret leaves each.
all_leaves = []
all_trees = []
roots = b""
for j in range(k):
    leaves = []
    for i in range(t):
        leaf = sha_n(seed + b"fors" + j.to_bytes(4, "big") + i.to_bytes(4, "big"), n)
        leaves.append(leaf)
    all_leaves.append(leaves)

    # Merkle tree: 1-indexed flat array, same layout as Chapter 14.
    tree = [b""] * (2 * t)
    for i, lf in enumerate(leaves):
        tree[t + i] = lf
    for i in range(t - 1, 0, -1):
        tree[i] = sha_n(tree[2 * i] + tree[2 * i + 1], n)
    all_trees.append(tree)
    roots += tree[1]

pk = sha_n(roots, n)
print(f"Tree 0 root: {all_trees[0][1].hex()}")
# ==> Tree 0 root: 792c2503
print(f"Tree 1 root: {all_trees[1][1].hex()}")
# ==> Tree 1 root: b5f1cd02
print(f"Tree 2 root: {all_trees[2][1].hex()}")
# ==> Tree 2 root: 56b3aea7
print(f"pk = {pk.hex()}")
# ==> pk = 7a77420a
