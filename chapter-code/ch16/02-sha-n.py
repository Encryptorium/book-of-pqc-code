# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 16: FORS and the stateless hypertree
# Section: "FORS at toy parameters"
# https://book.encryptorium.com/part-3-hash-based/ch16-fors-and-stateless-hypertree/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch16/02-sha-n.py

import hashlib

def sha_n(data, n=4):
    return hashlib.sha256(data).digest()[:n]

seed = b"ch16-fors-toy"
k, t, n = 3, 4, 4

# Regenerate the key material.
all_leaves = []
all_trees = []
roots = b""
for j in range(k):
    leaves = []
    for i in range(t):
        leaf = sha_n(seed + b"fors" + j.to_bytes(4, "big") + i.to_bytes(4, "big"), n)
        leaves.append(leaf)
    all_leaves.append(leaves)
    tree = [b""] * (2 * t)
    for i, lf in enumerate(leaves):
        tree[t + i] = lf
    for i in range(t - 1, 0, -1):
        tree[i] = sha_n(tree[2 * i] + tree[2 * i + 1], n)
    all_trees.append(tree)
    roots += tree[1]
pk = sha_n(roots, n)

# Extract k=3 indices from the message hash.
message = b"test FORS"
digest = hashlib.sha256(message).digest()
indices = []
for idx_i in range(k):
    shift = 6 - idx_i * 2
    val = (digest[0] >> shift) & 0x03
    indices.append(val)
print(f"Indices: {indices}")
# ==> Indices: [3, 0, 1]

# Sign: reveal the selected leaf and its auth path from each tree.
sig = []
for j in range(k):
    leaf = all_leaves[j][indices[j]]
    node = t + indices[j]
    path = []
    for _ in range(2):  # depth = log2(t) = 2
        path.append(all_trees[j][node ^ 1])
        node //= 2
    sig.append((leaf, path))
    print(f"Tree {j}: leaf[{indices[j]}] = {leaf.hex()}")
# ==> Tree 0: leaf[3] = 176ff120
# ==> Tree 1: leaf[0] = 9c88ece5
# ==> Tree 2: leaf[1] = fe0e9264

# Verify: reconstruct each root from the revealed leaf and auth path.
recon_roots = b""
for j in range(k):
    current = sig[j][0]
    idx = indices[j]
    for sib in sig[j][1]:
        if idx % 2 == 0:
            current = sha_n(current + sib, n)
        else:
            current = sha_n(sib + current, n)
        idx //= 2
    recon_roots += current

recon_pk = sha_n(recon_roots, n)
print(recon_pk == pk)
# ==> True
