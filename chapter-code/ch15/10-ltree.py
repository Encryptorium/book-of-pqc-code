# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 15: Many-time signatures
# Section: "L-tree compression"
# https://book.encryptorium.com/part-3-hash-based/ch15-many-time-signatures/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch15/10-ltree.py

import hashlib

def ltree(pk_values, seed):
    """Compress a list of values into a single hash via an L-tree."""
    nodes = list(pk_values)
    level = 0
    while len(nodes) > 1:
        next_level = []
        i = 0
        pair_index = 0
        while i + 1 < len(nodes):
            combined = hashlib.sha256(
                seed
                + level.to_bytes(4, "big")
                + pair_index.to_bytes(4, "big")
                + nodes[i]
                + nodes[i + 1]
            ).digest()
            next_level.append(combined)
            i += 2
            pair_index += 1
        if i < len(nodes):
            next_level.append(nodes[i])
        nodes = next_level
        level += 1
    return nodes[0]

seed = b"ch15-ltree"
values = [hashlib.sha256(f"pk-{i}".encode()).digest() for i in range(67)]
root = ltree(values, seed)
print(root.hex()[:16])
# ==> 6df796321be29a7e
