# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 15: Many-time signatures
# Section: "XMSS: WOTS+ in a Merkle tree"
# https://book.encryptorium.com/part-3-hash-based/ch15-many-time-signatures/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch15/11-base-w.py

import hashlib, math

def base_w(data, w, out_len):
    lg_w = int(math.log2(w))
    digits = []
    for byte in data:
        for shift in range(8 - lg_w, -1, -lg_w):
            digits.append((byte >> shift) & (w - 1))
            if len(digits) == out_len:
                return digits
    return digits[:out_len]

def chain_f(x, start, steps, pk_seed, addr):
    value = x
    for i in range(start, start + steps):
        value = hashlib.sha256(
            pk_seed + addr.to_bytes(4, "big") + i.to_bytes(4, "big") + value
        ).digest()
    return value

def ltree(pk_values, pk_seed):
    nodes = list(pk_values)
    level = 0
    while len(nodes) > 1:
        next_level = []
        i = 0
        pair_index = 0
        while i + 1 < len(nodes):
            combined = hashlib.sha256(
                pk_seed + level.to_bytes(4, "big") + pair_index.to_bytes(4, "big")
                + nodes[i] + nodes[i + 1]
            ).digest()
            next_level.append(combined)
            i += 2
            pair_index += 1
        if i < len(nodes):
            next_level.append(nodes[i])
        nodes = next_level
        level += 1
    return nodes[0]

sk_seed = b"ch15-xmss-sk"
pk_seed = b"ch15-xmss-pk"
w, n, h = 16, 32, 3
lg_w = int(math.log2(w))
ell_1 = math.ceil(8 * n / lg_w)
max_c = ell_1 * (w - 1)
ell_2 = math.ceil((math.floor(math.log2(max_c)) + 1) / lg_w)
ell = ell_1 + ell_2
num_leaves = 1 << h

# Generate all WOTS+ keypairs and build the Merkle tree.
all_sk, all_pk, leaves = [], [], []
for li in range(num_leaves):
    sk_leaf = sk_seed + b"leaf" + li.to_bytes(4, "big")
    pk_leaf = pk_seed + b"leaf" + li.to_bytes(4, "big")
    sk_i = [hashlib.sha256(sk_leaf + b"sk" + j.to_bytes(4, "big")).digest() for j in range(ell)]
    pk_i = [chain_f(sk_i[j], 0, w - 1, pk_leaf, j) for j in range(ell)]
    all_sk.append(sk_i)
    all_pk.append(pk_i)
    leaves.append(ltree(pk_i, pk_leaf))

tree = [b""] * (2 * num_leaves)
for i in range(num_leaves):
    tree[num_leaves + i] = leaves[i]
for i in range(num_leaves - 1, 0, -1):
    tree[i] = hashlib.sha256(tree[2 * i] + tree[2 * i + 1]).digest()

root = tree[1]
print(root.hex()[:16])
# ==> 95751d240dbaaed6
