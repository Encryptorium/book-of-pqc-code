# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 14: One-time signatures from hash functions
# Section: "The Merkle signature scheme"
# https://book.encryptorium.com/part-3-hash-based/ch14-one-time-signatures-from-hash/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch14/07-lamport-keygen.py

import hashlib

def lamport_keygen(seed, n=256):
    sk, pk = [], []
    for i in range(n):
        s0 = hashlib.sha256(seed + (2 * i).to_bytes(4, "big")).digest()
        s1 = hashlib.sha256(seed + (2 * i + 1).to_bytes(4, "big")).digest()
        sk.append((s0, s1))
        pk.append((hashlib.sha256(s0).digest(), hashlib.sha256(s1).digest()))
    return sk, pk

def lamport_sign(sk, message):
    digest = hashlib.sha256(message).digest()
    return [sk[i][(digest[i // 8] >> (7 - (i % 8))) & 1] for i in range(len(sk))]

def lamport_verify(pk, message, sig):
    digest = hashlib.sha256(message).digest()
    return all(
        hashlib.sha256(sig[i]).digest() == pk[i][(digest[i // 8] >> (7 - (i % 8))) & 1]
        for i in range(len(pk))
    )

def serialize_pk(pk):
    return b"".join(h0 + h1 for h0, h1 in pk)

# MSS keygen at d = 3 (8 one-time keys).
d = 3
num_leaves = 1 << d
mss_seed = b"ch14-mss"

all_sk, all_pk, leaves = [], [], []
for j in range(num_leaves):
    sk_j, pk_j = lamport_keygen(mss_seed + j.to_bytes(4, "big"))
    all_sk.append(sk_j)
    all_pk.append(pk_j)
    leaves.append(hashlib.sha256(serialize_pk(pk_j)).digest())

tree = [b""] * (2 * num_leaves)
for i in range(num_leaves):
    tree[num_leaves + i] = leaves[i]
for i in range(num_leaves - 1, 0, -1):
    tree[i] = hashlib.sha256(tree[2 * i] + tree[2 * i + 1]).digest()

root = tree[1]

# MSS sign with leaf 0.
leaf_index = 0
sig_lamport = lamport_sign(all_sk[leaf_index], b"hello MSS")
pk_lamport = all_pk[leaf_index]

node = num_leaves + leaf_index
path = []
for _ in range(d):
    path.append(tree[node ^ 1])
    node //= 2

# MSS verify.
ok_lamport = lamport_verify(pk_lamport, b"hello MSS", sig_lamport)
leaf_hash = hashlib.sha256(serialize_pk(pk_lamport)).digest()
current = leaf_hash
idx = leaf_index
for s in path:
    if idx % 2 == 0:
        current = hashlib.sha256(current + s).digest()
    else:
        current = hashlib.sha256(s + current).digest()
    idx //= 2

print(ok_lamport and current == root)
# ==> True
