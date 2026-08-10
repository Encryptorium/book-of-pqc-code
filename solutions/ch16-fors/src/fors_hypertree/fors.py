"""FORS: Forest of Random Subsets.

A few-time hash-based signature scheme.  The secret key consists of
*k* binary Merkle trees, each with *t* random leaves.  Signing hashes
the message to *k* indices (one per tree, each in {0, ..., t-1}) and
reveals the selected leaves plus their authentication paths.  The
verifier reconstructs the *k* tree roots and hashes them together to
recover the public key.

FORS tolerates a bounded number of signatures before the birthday-bound
collision probability on index values makes forgery feasible.  For *q*
signatures, the probability that any single tree position is reused is
approximately q^2 / (2t); over *k* trees the union bound gives
q^2 * k / (2t).
"""

import hashlib
import math


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


# -- Merkle tree (1-indexed flat array, same pattern as Ch 14/14) ------

def _build_tree(leaves: list[bytes]) -> list[bytes]:
    """Build a complete binary Merkle tree from *leaves*."""
    num_leaves = len(leaves)
    tree: list[bytes] = [b""] * (2 * num_leaves)
    for i, leaf in enumerate(leaves):
        tree[num_leaves + i] = leaf
    for i in range(num_leaves - 1, 0, -1):
        tree[i] = _sha256(tree[2 * i] + tree[2 * i + 1])
    return tree


def _auth_path(tree: list[bytes], leaf_index: int) -> list[bytes]:
    """Extract the authentication path for *leaf_index*."""
    num_leaves = len(tree) // 2
    depth = int(math.log2(num_leaves))
    node = num_leaves + leaf_index
    path: list[bytes] = []
    for _ in range(depth):
        path.append(tree[node ^ 1])
        node //= 2
    return path


def _verify_path(
    leaf: bytes, leaf_index: int, path: list[bytes], root: bytes
) -> bool:
    """Verify that *leaf* at *leaf_index* hashes to *root*."""
    current = leaf
    idx = leaf_index
    for sibling in path:
        if idx % 2 == 0:
            current = _sha256(current + sibling)
        else:
            current = _sha256(sibling + current)
        idx //= 2
    return current == root


# -- Index extraction --------------------------------------------------

def message_indices(message: bytes, k: int, t: int) -> list[int]:
    """Hash *message* and extract *k* indices, each in {0, ..., t-1}.

    *t* must be a power of two.  Extracts ``ceil(log2(t))`` bits per
    index from SHA-256(*message*), reading MSB-first within each byte.
    """
    assert t >= 2 and (t & (t - 1)) == 0, f"t must be a power of two, got {t}"
    lg_t = int(math.log2(t))
    digest = _sha256(message)
    # Extract lg_t bits per index from the digest bytes
    bits_needed = k * lg_t
    assert bits_needed <= 256, (
        f"k={k}, t={t} requires {bits_needed} bits but SHA-256 provides 256"
    )
    indices: list[int] = []
    bit_offset = 0
    for _ in range(k):
        value = 0
        for b in range(lg_t):
            cur_byte = bit_offset + b
            by = cur_byte // 8
            bi = 7 - (cur_byte % 8)
            value = (value << 1) | ((digest[by] >> bi) & 1)
        indices.append(value)
        bit_offset += lg_t
    return indices


# -- FORS keygen / sign / verify ---------------------------------------

def fors_keygen(
    seed: bytes, k: int = 6, t: int = 16, n: int = 32
) -> tuple[list[list[bytes]], list[list[bytes]], bytes]:
    """Generate a FORS keypair.

    Returns
    -------
    sk_leaves : list[list[bytes]]
        *k* lists of *t* secret leaf values (each *n* bytes).
    trees : list[list[bytes]]
        *k* Merkle trees (1-indexed flat arrays).
    pk : bytes
        Single *n*-byte public key: H(root_0 || ... || root_{k-1}).
    """
    sk_leaves: list[list[bytes]] = []
    trees: list[list[bytes]] = []
    roots = b""

    for j in range(k):
        leaves: list[bytes] = []
        for i in range(t):
            # Derive each leaf deterministically from the seed
            leaf_val = _sha256(
                seed + b"fors" + j.to_bytes(4, "big") + i.to_bytes(4, "big")
            )[:n]
            leaves.append(leaf_val)
        sk_leaves.append(leaves)
        tree = _build_tree(leaves)
        trees.append(tree)
        roots += tree[1]  # root is at index 1

    pk = _sha256(roots)[:n]
    return sk_leaves, trees, pk


def fors_sign(
    sk_leaves: list[list[bytes]],
    trees: list[list[bytes]],
    message: bytes,
    k: int = 6,
    t: int = 16,
    n: int = 32,
) -> list[tuple[bytes, list[bytes]]]:
    """Sign *message* with FORS.

    Returns *k* tuples of ``(revealed_leaf, auth_path)``.
    """
    indices = message_indices(message, k, t)
    sig: list[tuple[bytes, list[bytes]]] = []
    for j in range(k):
        idx = indices[j]
        leaf = sk_leaves[j][idx]
        path = _auth_path(trees[j], idx)
        sig.append((leaf, path))
    return sig


def fors_verify(
    pk: bytes,
    message: bytes,
    sig: list[tuple[bytes, list[bytes]]],
    k: int = 6,
    t: int = 16,
    n: int = 32,
) -> bool:
    """Verify a FORS signature against public key *pk*."""
    if len(sig) != k:
        return False
    indices = message_indices(message, k, t)
    roots = b""
    h = int(math.log2(t))
    for j in range(k):
        leaf, path = sig[j]
        if len(path) != h:
            return False
        # Reconstruct the root from the leaf and auth path
        current = leaf
        idx = indices[j]
        for sibling in path:
            if idx % 2 == 0:
                current = _sha256(current + sibling)
            else:
                current = _sha256(sibling + current)
            idx //= 2
        roots += current
    expected_pk = _sha256(roots)[:n]
    return expected_pk == pk
