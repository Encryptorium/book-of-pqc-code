"""Toy q-ary Merkle commitment for Chapter 32.

Generalizes the binary toy Merkle tree sketched in Chapter 31 to q-ary
trees with configurable hash-output width. Binding reduces to collision
resistance of the underlying hash function. Quantum collision cost on
an n-bit hash is approximately 2^{n/3} under the QRACM model
(Brassard-Hoyer-Tapp 1998) and closer to 2^{2n/5} without QRACM
(Chailloux-Naya-Plasencia-Schrottenloher 2017); Chapter 32 uses both
bounds when sizing hash output widths for post-quantum Merkle
deployments.

The module is pedagogical: it exists to demonstrate the commit, open,
and verify round trip across configurable arities and hash widths, not
to serve as a production Merkle implementation. Leaves are byte
strings; the commit routine hashes them into fixed-width digests and
folds upward q digests at a time.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


# Supported hash output widths (bits). 256 maps to SHA-256; widths
# below 256 use SHAKE-128 (which is capped at 128-bit collision strength
# per FIPS 202 Appendix A.1, fine for the 128/192-bit demo rows); widths
# above 256 use SHAKE-256 because SHAKE-128 cannot deliver more than
# 128-bit collision strength regardless of output length.
SUPPORTED_WIDTHS = (128, 192, 256, 384, 512)


@dataclass
class MerkleCommit:
    """A commitment produced by ``commit_leaves``.

    ``root`` is the top-level digest. ``levels`` stores every level of
    the tree (level 0 is the hashed leaves, level -1 is the root) so
    the prover can produce openings without recomputing the tree.
    ``arity`` and ``width_bits`` record the tree parameters for the
    verifier.
    """

    arity: int
    width_bits: int
    num_leaves: int
    levels: list[list[bytes]]

    @property
    def root(self) -> bytes:
        return self.levels[-1][0]


@dataclass
class MerkleOpening:
    """An opening proof for a single leaf index.

    ``leaf_value`` is the raw leaf bytes. ``siblings[i]`` is the list
    of q-1 sibling digests at level ``i`` needed to reconstruct the
    parent digest along the path from the leaf to the root.
    ``leaf_index`` records the position so the verifier knows where the
    hashed leaf sits among its siblings at each level.
    """

    leaf_index: int
    leaf_value: bytes
    siblings: list[list[bytes]]


def hash_bytes(data: bytes, width_bits: int = 256) -> bytes:
    """Return a ``width_bits``-bit digest of ``data``.

    SHA-256 is used when ``width_bits == 256``. For widths below 256
    bits (128, 192) SHAKE-128 is fine because its 128-bit collision-
    strength cap matches or exceeds n/2 at those widths. For widths
    above 256 bits (384, 512) the routine uses SHAKE-256, because
    SHAKE-128's collision-resistance security strength is capped at
    128 bits regardless of output length (FIPS 202 Appendix A.1) and
    would otherwise undercut the BHT/CNPS margins this module
    reports. Raises ValueError on an unsupported width.
    """
    if width_bits not in SUPPORTED_WIDTHS:
        raise ValueError(f"unsupported width_bits {width_bits}; use one of {SUPPORTED_WIDTHS}")
    if width_bits == 256:
        return hashlib.sha256(data).digest()
    if width_bits >= 384:
        return hashlib.shake_256(data).digest(width_bits // 8)
    return hashlib.shake_128(data).digest(width_bits // 8)


def commit_leaves(
    leaves: list[bytes],
    arity: int = 2,
    width_bits: int = 256,
) -> MerkleCommit:
    """Build a q-ary Merkle tree over ``leaves``.

    Leaves are hashed into ``width_bits``-bit digests and folded q at a
    time until a single root digest remains. Leaves are padded with a
    fixed zero digest to the next power of ``arity``. Raises
    ValueError for an empty leaf list, arity below 2, or unsupported
    width.
    """
    if arity < 2:
        raise ValueError("arity must be at least 2")
    if len(leaves) == 0:
        raise ValueError("leaf list must be non-empty")

    zero_digest = bytes(width_bits // 8)
    current: list[bytes] = [hash_bytes(leaf, width_bits) for leaf in leaves]

    # Pad to the next power of arity.
    padded_len = arity
    while padded_len < len(current):
        padded_len *= arity
    while len(current) < padded_len:
        current.append(zero_digest)

    levels: list[list[bytes]] = [list(current)]
    while len(current) > 1:
        next_level: list[bytes] = []
        for i in range(0, len(current), arity):
            block = b"".join(current[i : i + arity])
            next_level.append(hash_bytes(block, width_bits))
        levels.append(next_level)
        current = next_level

    return MerkleCommit(
        arity=arity,
        width_bits=width_bits,
        num_leaves=len(leaves),
        levels=levels,
    )


def open_at(commit: MerkleCommit, leaf_index: int, leaf_value: bytes) -> MerkleOpening:
    """Produce an opening for the leaf at ``leaf_index``.

    Records the q-1 sibling digests at each level along the path from
    the hashed leaf to the root. Raises ValueError if the leaf index
    is out of range or if ``leaf_value`` does not match the committed
    digest (a guard against an opening being constructed from a leaf
    that was not part of the committed list).
    """
    if leaf_index < 0 or leaf_index >= commit.num_leaves:
        raise ValueError("leaf_index out of range")
    if hash_bytes(leaf_value, commit.width_bits) != commit.levels[0][leaf_index]:
        raise ValueError("leaf_value does not match committed digest")

    siblings: list[list[bytes]] = []
    index = leaf_index
    for level in commit.levels[:-1]:
        block_start = (index // commit.arity) * commit.arity
        block_end = block_start + commit.arity
        block_siblings = [
            level[i] for i in range(block_start, block_end) if i != index
        ]
        siblings.append(block_siblings)
        index //= commit.arity

    return MerkleOpening(
        leaf_index=leaf_index,
        leaf_value=leaf_value,
        siblings=siblings,
    )


def verify(
    root: bytes,
    opening: MerkleOpening,
    arity: int,
    width_bits: int = 256,
) -> bool:
    """Verify an opening against a committed ``root``.

    Reconstructs each parent digest from the hashed leaf and the
    recorded sibling digests, walking up to the root and comparing.
    Returns True on match, False otherwise.
    """
    current = hash_bytes(opening.leaf_value, width_bits)
    index = opening.leaf_index
    for level_siblings in opening.siblings:
        position = index % arity
        # Reassemble the full q-digest block by inserting ``current``
        # at ``position`` and the siblings elsewhere.
        block: list[bytes] = []
        sibling_iter = iter(level_siblings)
        for j in range(arity):
            if j == position:
                block.append(current)
            else:
                block.append(next(sibling_iter))
        current = hash_bytes(b"".join(block), width_bits)
        index //= arity
    return current == root


def quantum_collision_bits_bht(width_bits: int) -> int:
    """Approximate BHT 2^{n/3} bound in bits.

    With ``n = width_bits``, the BHT bound gives quantum collision-
    finding cost of approximately 2^{n/3} queries under the QRACM
    model. The return value is ``width_bits // 3`` rounded down, which
    is the figure of merit Ch 32 uses for worst-case PQ collision
    security.
    """
    if width_bits <= 0:
        raise ValueError("width_bits must be positive")
    return width_bits // 3


def quantum_collision_bits_cnps(width_bits: int) -> int:
    """Approximate CNPS 2^{2n/5} bound in bits without QRACM.

    Chailloux-Naya-Plasencia-Schrottenloher 2017 improves the no-QRACM
    bound to approximately 2^{2n/5} queries. The return value is
    ``(2 * width_bits) // 5`` rounded down.
    """
    if width_bits <= 0:
        raise ValueError("width_bits must be positive")
    return (2 * width_bits) // 5
