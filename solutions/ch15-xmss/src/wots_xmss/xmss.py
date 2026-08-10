"""XMSS: eXtended Merkle Signature Scheme.

Wraps WOTS+ one-time signatures in a Merkle tree with a stateful leaf
counter.  The signer must never reuse a leaf index; doing so degrades
the one-time security of the underlying WOTS+ key.
"""

import hashlib
import math

from .ltree import ltree
from .wots import wots_keygen, wots_sign, wots_verify


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


# ── Merkle tree (same 1-indexed flat-array pattern as Ch 14) ─────────

def _build_tree(leaves: list[bytes]) -> list[bytes]:
    """Build a complete binary Merkle tree from *leaves* (power-of-2 count)."""
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
    leaf: bytes, leaf_index: int, path: list[bytes], root_hash: bytes
) -> bool:
    """Verify that *leaf* at *leaf_index* hashes to *root_hash*."""
    current = leaf
    idx = leaf_index
    for sibling in path:
        if idx % 2 == 0:
            current = _sha256(current + sibling)
        else:
            current = _sha256(sibling + current)
        idx //= 2
    return current == root_hash


# ── XMSS keygen / sign / verify ─────────────────────────────────────

def xmss_keygen(
    d: int = 10,
    sk_seed: bytes | None = None,
    pk_seed: bytes | None = None,
    w: int = 16,
    n: int = 32,
):
    """Generate an XMSS keypair with ``2**d`` one-time keys.

    Parameters
    ----------
    d : int
        Tree depth.  The scheme supports exactly ``2**d`` signatures.
    sk_seed : bytes or None
        Private master seed for deriving WOTS+ secret keys.  If *None*,
        uses ``b"xmss-default-sk-seed"``.
    pk_seed : bytes or None
        Public seed that domain-separates the chain function and L-tree
        hashing (safe to publish alongside the root hash).  If *None*,
        uses ``b"xmss-default-pk-seed"``.
    w : int
        Winternitz parameter (default 16).
    n : int
        Hash output length in bytes (default 32 for SHA-256).

    Returns
    -------
    all_sk : list
        ``2**d`` WOTS+ secret keys.
    all_pk : list
        ``2**d`` WOTS+ public keys.
    tree : list[bytes]
        The Merkle tree (1-indexed flat array).
    root_hash : bytes
        The Merkle root (the single published public key).
    state : dict
        Mutable state with ``next_leaf`` counter and ``max_leaf`` limit.
    """
    if sk_seed is None:
        sk_seed = b"xmss-default-sk-seed"
    if pk_seed is None:
        pk_seed = b"xmss-default-pk-seed"

    num_leaves = 1 << d
    all_sk: list[list[bytes]] = []
    all_pk: list[list[bytes]] = []
    leaves: list[bytes] = []

    for i in range(num_leaves):
        sk_leaf = sk_seed + b"leaf" + i.to_bytes(4, "big")
        pk_leaf = pk_seed + b"leaf" + i.to_bytes(4, "big")
        sk, pk = wots_keygen(sk_leaf, pk_leaf, w=w, n=n)
        all_sk.append(sk)
        all_pk.append(pk)
        leaves.append(ltree(pk, pk_leaf))

    tree = _build_tree(leaves)
    root_hash = tree[1]
    state = {"next_leaf": 0, "max_leaf": num_leaves}
    return all_sk, all_pk, tree, root_hash, state


def xmss_sign(
    all_sk: list,
    all_pk: list,
    tree: list[bytes],
    state: dict,
    message: bytes,
    pk_seed: bytes,
    w: int = 16,
):
    """Sign *message* using the next available leaf.

    Raises ``RuntimeError`` if all leaves have been exhausted.
    Mutates *state* by incrementing ``next_leaf``.

    Returns
    -------
    wots_sig : list[bytes]
        The WOTS+ signature.
    wots_pk : list[bytes]
        The WOTS+ public key for this leaf.
    path : list[bytes]
        The Merkle authentication path.
    leaf_index : int
        The leaf index used for this signature.
    """
    idx = state["next_leaf"]
    if idx >= state["max_leaf"]:
        raise RuntimeError(
            f"leaf exhaustion: all {state['max_leaf']} leaves have been used"
        )

    pk_leaf = pk_seed + b"leaf" + idx.to_bytes(4, "big")
    wots_sig = wots_sign(all_sk[idx], message, pk_leaf, w=w)
    wots_pk = all_pk[idx]
    path = _auth_path(tree, idx)
    state["next_leaf"] = idx + 1
    return wots_sig, wots_pk, path, idx


def xmss_verify(
    root_hash: bytes,
    message: bytes,
    wots_sig: list[bytes],
    wots_pk: list[bytes],
    path: list[bytes],
    leaf_index: int,
    pk_seed: bytes,
    w: int = 16,
) -> bool:
    """Verify an XMSS signature.

    Checks the WOTS+ signature against the provided public key, then
    L-tree-compresses the public key to a leaf hash and verifies the
    Merkle authentication path to *root_hash*.  *pk_seed* is the public
    chain-domain seed.
    """
    pk_leaf = pk_seed + b"leaf" + leaf_index.to_bytes(4, "big")

    if not wots_verify(wots_pk, message, wots_sig, pk_leaf, w=w):
        return False

    leaf = ltree(wots_pk, pk_leaf)
    return _verify_path(leaf, leaf_index, path, root_hash)
