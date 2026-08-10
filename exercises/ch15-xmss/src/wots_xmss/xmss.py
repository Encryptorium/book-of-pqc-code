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
    # EXERCISE: implement this function.
    #
    # Default the two seeds if they are None, then for each of the 1 << d
    # leaves derive a per-leaf pair of seeds by appending b'leaf' and the
    # 4-byte big-endian index to sk_seed and to pk_seed. Run wots_keygen on
    # that pair, keep both halves, and compress the WOTS+ public key with
    # ltree under the leaf's public seed to get the Merkle leaf. Build the
    # tree with _build_tree, take the root at index 1, and return the keys,
    # the tree, the root, and a state dict holding next_leaf = 0 and
    # max_leaf = 1 << d. Only the root and the public seed are published;
    # the tree and the WOTS+ keys are the signer's material.
    #
    # Reference: Chapter 15, 'XMSS: WOTS+ in a Merkle tree' (RFC 8391 Section 4.1.7)
    #
    # Proved by:
    #   tests/ch15/test_xmss_roundtrip.py
    #   tests/ch15/test_xmss_leaf_reuse.py
    raise NotImplementedError("exercise: xmss_keygen")


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
    # EXERCISE: implement this function.
    #
    # Read next_leaf out of state and raise RuntimeError mentioning leaf
    # exhaustion once it has reached max_leaf. Otherwise rebuild that leaf's
    # public seed as pk_seed || b'leaf' || index as 4 big-endian bytes, sign
    # with wots_sign under it, take the authentication path with _auth_path,
    # and increment state['next_leaf'] before returning the WOTS+ signature,
    # that leaf's WOTS+ public key, the path, and the index. The counter
    # advance is the entire safety property: SP 800-208 requires it be
    # persisted before the signature is released, and a state dict copied
    # and restored is exactly how two signatures end up on one leaf.
    #
    # Reference: Chapter 15, 'State management and leaf exhaustion' (NIST SP 800-208 Section 8)
    #
    # Proved by:
    #   tests/ch15/test_xmss_roundtrip.py
    #   tests/ch15/test_xmss_leaf_reuse.py
    raise NotImplementedError("exercise: xmss_sign")


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
