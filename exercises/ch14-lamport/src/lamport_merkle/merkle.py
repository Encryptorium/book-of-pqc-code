"""Binary Merkle tree with authentication paths.

The tree is stored as a 1-indexed flat list of length ``2 * num_leaves``.
Index 1 is the root; indices ``num_leaves`` through ``2 * num_leaves - 1``
are the leaves.  Each internal node is ``SHA256(left_child || right_child)``.
"""

import hashlib
import math


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def build_tree(leaves: list[bytes]) -> list[bytes]:
    """Build a complete binary Merkle tree from *leaves*.

    Parameters
    ----------
    leaves : list[bytes]
        Exactly ``2**d`` leaf hashes for some non-negative integer *d*.

    Returns
    -------
    tree : list[bytes]
        A 1-indexed flat array.  ``tree[0]`` is unused padding (empty
        bytes).  ``tree[1]`` is the root.  Leaves occupy indices
        ``num_leaves`` through ``2 * num_leaves - 1``.
    """
    # EXERCISE: implement this function.
    #
    # Store the tree as a flat list, leaves first. Each parent is the
    # SHA-256 digest of its two children concatenated left then right.
    #
    # Reference: Chapter 14, 'Merkle tree at depth 3'
    #
    # Proved by:
    #   tests/ch14/test_merkle_tree_root.py
    raise NotImplementedError("exercise: build_tree")


def root(tree: list[bytes]) -> bytes:
    """Return the Merkle root (``tree[1]``)."""
    return tree[1]


def auth_path(tree: list[bytes], leaf_index: int) -> list[bytes]:
    """Extract the authentication path for the leaf at *leaf_index*.

    Parameters
    ----------
    tree : list[bytes]
        A Merkle tree produced by :func:`build_tree`.
    leaf_index : int
        Zero-based index of the target leaf (0 is the leftmost leaf).

    Returns
    -------
    path : list[bytes]
        A list of *d* sibling hashes, ordered from the leaf level to the
        level just below the root.
    """
    # EXERCISE: implement this function.
    #
    # Walk from the leaf to the root, collecting the sibling at each level.
    # The path length is the tree depth.
    #
    # Reference: Chapter 14, 'Authentication paths'
    #
    # Proved by:
    #   tests/ch14/test_merkle_auth_path.py
    raise NotImplementedError("exercise: auth_path")


def verify_path(
    leaf: bytes,
    leaf_index: int,
    path: list[bytes],
    root_hash: bytes,
) -> bool:
    """Verify that *leaf* at *leaf_index* belongs to the tree with *root_hash*.

    Parameters
    ----------
    leaf : bytes
        The leaf hash to verify.
    leaf_index : int
        Zero-based leaf index.
    path : list[bytes]
        Authentication path produced by :func:`auth_path`.
    root_hash : bytes
        The published Merkle root.

    Returns
    -------
    bool
        *True* iff the recomputed root matches *root_hash*.
    """
    current = leaf
    idx = leaf_index
    for sibling in path:
        if idx % 2 == 0:
            current = _sha256(current + sibling)
        else:
            current = _sha256(sibling + current)
        idx //= 2
    return current == root_hash
