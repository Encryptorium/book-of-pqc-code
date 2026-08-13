"""L2 commitment: a binary Merkle tree, for Chapter 31.

Chapter 31 prints this tree as the pedagogical slice of L2: commit to a
power-of-two list of leaves, open one of them, and check the opening
against the root. Binding follows from collision resistance of the
underlying hash, because two distinct openings at the same leaf index
traverse the same sequence of parent positions, so any divergence in
sibling values along those positions forces a collision.

What the printed block omits, and this module supplies, is domain
separation. A tree that hashes a leaf and an internal node the same way
lets a prover present an internal node as if it were a leaf, so the
depth of the tree stops being fixed by the commitment. Tagging the two
cases apart costs one byte per hash and closes that path.

Chapter 32 generalizes this tree to configurable arity and hash-output
width in ``commitment_schemes.merkle``, and sizes the hash width against
the quantum collision bounds. This module stays binary and stays on
SHA-256, because Chapter 31 needs the shape of L2 rather than its
parameters.
"""

from __future__ import annotations

import hashlib

# Domain-separation tags. One byte, prepended before hashing, so that a
# leaf digest and an internal-node digest can never be the same value
# even when the bytes underneath them are.
LEAF_TAG = b"\x00"
NODE_TAG = b"\x01"


def H(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def hash_leaf(leaf: bytes) -> bytes:
    """Hash a leaf under the leaf domain tag."""
    # EXERCISE: implement this function.
    #
    # Hash the leaf under LEAF_TAG. The tag goes in front of the value, not
    # behind it, so that no choice of leaf bytes can reproduce an internal
    # node's digest. This is the half of the tree the chapter's printed
    # block leaves out and flags in its comment.
    #
    # Reference: Chapter 31, 'The four layers in a toy running example'
    #
    # Proved by:
    #   tests/ch31/test_merkle.py
    raise NotImplementedError("exercise: hash_leaf")


def hash_node(left: bytes, right: bytes) -> bytes:
    """Hash two child digests under the internal-node domain tag."""
    # EXERCISE: implement this function.
    #
    # Hash the two child digests under NODE_TAG, left before right. Keep it
    # asymmetric: a tree whose parent hash commutes lets a prover swap a
    # leaf with its sibling and open the same root at the wrong index. The
    # tag is what stops a 64-byte leaf being passed off as this node.
    #
    # Reference: Chapter 31, 'The four layers in a toy running example'
    #
    # Proved by:
    #   tests/ch31/test_merkle.py
    raise NotImplementedError("exercise: hash_node")


def commit(leaves):
    """Fold a power-of-two list of leaves into a single root digest."""
    if len(leaves) == 0 or (len(leaves) & (len(leaves) - 1)) != 0:
        raise ValueError("leaves must be a nonempty power of two")
    nodes = [hash_leaf(leaf) for leaf in leaves]
    while len(nodes) > 1:
        nodes = [hash_node(nodes[i], nodes[i + 1]) for i in range(0, len(nodes), 2)]
    return nodes[0]


def open_path(leaves, index):
    """Collect the sibling digests on the path from ``index`` to the root.

    The opening carries siblings and nothing else. Which side of each
    sibling the leaf sits on is not part of the proof, because the leaf
    index is public and the verifier derives the sides from it. A tree
    that shipped those sides alongside the siblings would be handing the
    prover a field it has no business choosing.
    """
    path = []
    nodes = [hash_leaf(leaf) for leaf in leaves]
    while len(nodes) > 1:
        path.append(nodes[index ^ 1])
        nodes = [hash_node(nodes[i], nodes[i + 1]) for i in range(0, len(nodes), 2)]
        index //= 2
    return path


def verify_path(leaf, index, path, root) -> bool:
    """Recompute the root from one leaf and its opening, and compare.

    ``index`` drives the left-right choice at each level, which is what
    makes the chapter's binding argument concrete: two openings at the
    same index traverse the same sequence of parent positions, so any
    divergence in the siblings forces a collision.
    """
    acc = hash_leaf(leaf)
    for sibling in path:
        acc = hash_node(sibling, acc) if index & 1 else hash_node(acc, sibling)
        index //= 2
    return acc == root
