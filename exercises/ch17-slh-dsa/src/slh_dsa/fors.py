"""FORS with ADRS for SLH-DSA (FIPS 205 Section 8, Algorithms 14-17).

FORS signs by revealing selected leaves from k binary Merkle trees.
Each leaf is the hash of a PRF-derived secret value passed through the
tweakable function F, restoring the secret/public separation that
Chapter 16's teaching implementation omitted.
"""

from __future__ import annotations

from .adrs import ADRS, FORS_TREE, FORS_ROOTS, FORS_PRF
from .params import SLHDSAParams
from .tweakable import F, H, PRF, T_l


def _fors_sk_gen(params: SLHDSAParams, sk_seed: bytes, pk_seed: bytes,
                 adrs: ADRS, idx: int) -> bytes:
    """Generate the FORS secret value at global index *idx*.

    FIPS 205 Algorithm 14 (fors_skGen).
    """
    sk_adrs = adrs.copy()
    sk_adrs.set_type(FORS_PRF)
    sk_adrs.set_keypair_address(adrs.get_keypair_address())
    sk_adrs.set_tree_index(idx)
    return PRF(params, pk_seed, sk_seed, sk_adrs)


def _fors_node(params: SLHDSAParams, sk_seed: bytes, pk_seed: bytes,
               adrs: ADRS, i: int, z: int) -> bytes:
    """Compute FORS tree node at position *i* and height *z*.

    Leaf nodes (z == 0) hash the secret through F for domain separation.
    Internal nodes combine children via H.

    FIPS 205 Algorithm 15 (fors_node).
    """
    n = params.n
    a = params.a

    if z == 0:
        sk = _fors_sk_gen(params, sk_seed, pk_seed, adrs, i)
        node_adrs = adrs.copy()
        node_adrs.set_type(FORS_TREE)
        node_adrs.set_keypair_address(adrs.get_keypair_address())
        node_adrs.set_tree_height(0)
        node_adrs.set_tree_index(i)
        return F(params, pk_seed, node_adrs, sk)

    left = _fors_node(params, sk_seed, pk_seed, adrs, 2 * i, z - 1)
    right = _fors_node(params, sk_seed, pk_seed, adrs, 2 * i + 1, z - 1)

    node_adrs = adrs.copy()
    node_adrs.set_type(FORS_TREE)
    node_adrs.set_keypair_address(adrs.get_keypair_address())
    node_adrs.set_tree_height(z)
    node_adrs.set_tree_index(i)
    return H(params, pk_seed, node_adrs, left, right)


def fors_sign(params: SLHDSAParams, sk_seed: bytes, pk_seed: bytes,
              adrs: ADRS, md: bytes) -> bytes:
    """Sign with FORS (FIPS 205 Algorithm 16).

    *md* is the FORS portion of the message digest (k*a bits packed
    into bytes).  Returns the FORS signature as a byte string:
    k * (n + a * n) bytes total.
    """
    # EXERCISE: implement this function.
    #
    # Pull the k indices out of md with _extract_indices, a bits each. For
    # tree j holding index idx the global leaf index is j * t + idx: FORS
    # addresses all k trees in one flat index space, which is why the ADRS
    # tree index here is never per-tree. Emit the secret at that global
    # index from _fors_sk_gen, then a authentication nodes: at height s the
    # node on the path is (j * t + idx) >> s and the sibling to publish is
    # that value XOR 1, computed by _fors_node at height s. The result is k
    # * (1 + a) * n bytes, one secret plus a path per tree, and it reveals
    # raw secrets rather than hashed leaves.
    #
    # Reference: Chapter 17, 'FORS with ADRS and F-function separation' (FIPS 205 Algorithm 16)
    #
    # Proved by:
    #   tests/ch17/test_fors_roundtrip.py
    #   tests/ch17/test_vectors.py
    raise NotImplementedError("exercise: fors_sign")


def fors_pk_from_sig(params: SLHDSAParams, pk_seed: bytes,
                     adrs: ADRS, sig: bytes, md: bytes) -> bytes:
    """Recover the FORS public key from a signature (FIPS 205 Algorithm 17).

    Reconstruct k tree roots from the signature and compress them
    via T_l to recover the FORS public key.
    """
    # EXERCISE: implement this function.
    #
    # Walk the signature in n-byte pieces, k groups of 1 + a. For each tree
    # take the revealed secret and hash it through F under a FORS_TREE
    # address with tree height 0 and tree index j * t + idx: the secret is
    # not the leaf, and that F step is exactly what stops the public tree
    # from handing out the secret. Then climb a levels, consuming one
    # authentication node per level, setting the parent address to tree
    # height s + 1 and tree index node_idx >> (s + 1), and ordering the two
    # children by whether node_idx >> s is even. Concatenate the k
    # reconstructed roots and compress them with T_l under a FORS_ROOTS
    # address. Restore the keypair address after every set_type.
    #
    # Reference: Chapter 17, 'FORS with ADRS and F-function separation' (FIPS 205 Algorithm 17)
    #
    # Proved by:
    #   tests/ch17/test_fors_roundtrip.py
    #   tests/ch17/test_vectors.py
    raise NotImplementedError("exercise: fors_pk_from_sig")


def _extract_indices(md: bytes, k: int, a: int) -> list[int]:
    """Extract k indices from message digest, each a bits."""
    indices: list[int] = []
    bit_offset = 0
    for _ in range(k):
        value = 0
        for b in range(a):
            byte_idx = (bit_offset + b) // 8
            bit_idx = 7 - ((bit_offset + b) % 8)
            value = (value << 1) | ((md[byte_idx] >> bit_idx) & 1)
        indices.append(value)
        bit_offset += a
    return indices
