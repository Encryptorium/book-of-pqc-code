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
    # EXERCISE: implement this function.
    #
    # SHA-256 at width 256. Below 256 (128 and 192) SHAKE-128 is adequate
    # because its 128-bit collision-strength cap sits at or above n/2 there.
    # At 384 and above the routine must switch to SHAKE-256: SHAKE-128's
    # collision resistance caps at 128 bits however many output bytes it is
    # asked for (FIPS 202 Appendix A.1), so routing a 384-bit width through
    # it would quietly undercut the BHT and CNPS margins this module
    # reports. Reject any width outside SUPPORTED_WIDTHS.
    #
    # Reference: Chapter 32, 'Merkle: hash-based binding'
    #
    # Proved by:
    #   tests/ch32/test_merkle_pcs.py
    raise NotImplementedError("exercise: hash_bytes")


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
    # EXERCISE: implement this function.
    #
    # Hash every leaf to a width_bits digest, pad that level up to the next
    # power of arity with an all-zero digest of the same width, then fold
    # upward: take arity digests at a time, concatenate them left to right,
    # and hash the block into its parent. Keep every level in the returned
    # commitment, level 0 being the hashed leaves and the last level the
    # single root, so open_at can read siblings straight out instead of
    # rebuilding the tree. Reject an empty leaf list and an arity below 2.
    #
    # Reference: Chapter 32, 'Merkle: hash-based binding'
    #
    # Proved by:
    #   tests/ch32/test_merkle_pcs.py
    raise NotImplementedError("exercise: commit_leaves")


def open_at(commit: MerkleCommit, leaf_index: int, leaf_value: bytes) -> MerkleOpening:
    """Produce an opening for the leaf at ``leaf_index``.

    Records the q-1 sibling digests at each level along the path from
    the hashed leaf to the root. Raises ValueError if the leaf index
    is out of range or if ``leaf_value`` does not match the committed
    digest (a guard against an opening being constructed from a leaf
    that was not part of the committed list).
    """
    # EXERCISE: implement this function.
    #
    # Walk from the hashed leaf up to the root recording, at each level, the
    # arity - 1 digests that share the leaf's block. The block holding index
    # i starts at (i // arity) * arity and runs arity wide; collect every
    # position in it except i, then divide the index by arity to ascend.
    # Stop before the root level, which has no siblings. Check first that
    # the leaf index is in range and that leaf_value really hashes to the
    # committed digest at that index, so an opening cannot be assembled from
    # a leaf that was never committed.
    #
    # Reference: Chapter 32, 'Merkle: hash-based binding'
    #
    # Proved by:
    #   tests/ch32/test_merkle_pcs.py
    raise NotImplementedError("exercise: open_at")


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
    # EXERCISE: implement this function.
    #
    # Recompute the root and compare. Hash the opening's leaf value, then at
    # each level work out where the running digest sits inside its block
    # with index % arity, rebuild the full arity-wide block by dropping the
    # running digest into that position and the recorded siblings into the
    # other positions in order, hash the concatenation into the parent, and
    # divide the index by arity. Return whether the final digest equals the
    # committed root. Position is load-bearing: concatenation order is what
    # binds a leaf to its place in the tree, so siblings dropped into the
    # wrong slots produce a different root.
    #
    # Reference: Chapter 32, 'Merkle: hash-based binding'
    #
    # Proved by:
    #   tests/ch32/test_merkle_pcs.py
    raise NotImplementedError("exercise: verify")


def quantum_collision_bits_bht(width_bits: int) -> int:
    """Approximate BHT 2^{n/3} bound in bits.

    With ``n = width_bits``, the BHT bound gives quantum collision-
    finding cost of approximately 2^{n/3} queries under the QRACM
    model. The return value is ``width_bits // 3`` rounded down, which
    is the figure of merit Ch 32 uses for worst-case PQ collision
    security.
    """
    # EXERCISE: implement this function.
    #
    # Brassard-Hoyer-Tapp bound quantum collision finding on an n-bit hash
    # at roughly 2^(n/3) queries under the QRACM model, so the figure of
    # merit is n // 3 bits: 85 at n = 256, 128 at n = 384, 170 at n = 512.
    # Reject a non-positive width. This is the conservative of the two
    # bounds and is what forces n = 384 on a deployment that treats QRACM as
    # available.
    #
    # Reference: Chapter 32, 'Merkle: hash-based binding'
    #
    # Proved by:
    #   tests/ch32/test_merkle_pcs.py
    raise NotImplementedError("exercise: quantum_collision_bits_bht")


def quantum_collision_bits_cnps(width_bits: int) -> int:
    """Approximate CNPS 2^{2n/5} bound in bits without QRACM.

    Chailloux-Naya-Plasencia-Schrottenloher 2017 improves the no-QRACM
    bound to approximately 2^{2n/5} queries. The return value is
    ``(2 * width_bits) // 5`` rounded down.
    """
    # EXERCISE: implement this function.
    #
    # Chailloux-Naya-Plasencia-Schrottenloher drop the QRACM assumption and
    # reach roughly 2^(2n/5), so the figure of merit is (2 * n) // 5: 102 at
    # n = 256, 153 at n = 384, 204 at n = 512. Reject a non-positive width.
    # It is the less aggressive bound, which is why a deployment that
    # rejects QRACM as physically unrealistic can argue for n = 256 at a
    # 102-bit target where a BHT worst case needs n = 384.
    #
    # Reference: Chapter 32, 'Merkle: hash-based binding'
    #
    # Proved by:
    #   tests/ch32/test_merkle_pcs.py
    raise NotImplementedError("exercise: quantum_collision_bits_cnps")
