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
    n = params.n
    k = params.k
    a = params.a
    t = params.t

    # Extract k indices from md, each a bits
    indices = _extract_indices(md, k, a)

    sig = b""
    for j in range(k):
        idx = indices[j]
        # Global leaf index within this FORS instance
        global_idx = j * t + idx

        # Reveal the secret leaf value
        sig += _fors_sk_gen(params, sk_seed, pk_seed, adrs, global_idx)

        # Authentication path: sibling nodes from leaf to root
        for s in range(a):
            # The sibling at height s for leaf idx in tree j
            node_idx = (j * t + idx) >> s
            sibling_idx = node_idx ^ 1
            # Compute the sibling node at height s
            # Global position for treehash: sibling_idx at height s
            sig += _fors_node(params, sk_seed, pk_seed, adrs,
                              sibling_idx, s)

    return sig


def fors_pk_from_sig(params: SLHDSAParams, pk_seed: bytes,
                     adrs: ADRS, sig: bytes, md: bytes) -> bytes:
    """Recover the FORS public key from a signature (FIPS 205 Algorithm 17).

    Reconstruct k tree roots from the signature and compress them
    via T_l to recover the FORS public key.
    """
    n = params.n
    k = params.k
    a = params.a
    t = params.t

    indices = _extract_indices(md, k, a)

    roots = b""
    offset = 0
    for j in range(k):
        idx = indices[j]

        # The revealed leaf secret
        sk_val = sig[offset : offset + n]
        offset += n

        # Hash the secret through F to get the leaf node
        leaf_adrs = adrs.copy()
        leaf_adrs.set_type(FORS_TREE)
        leaf_adrs.set_keypair_address(adrs.get_keypair_address())
        leaf_adrs.set_tree_height(0)
        leaf_adrs.set_tree_index(j * t + idx)
        node = F(params, pk_seed, leaf_adrs, sk_val)

        # Walk up the authentication path
        node_idx = j * t + idx
        for s in range(a):
            auth_node = sig[offset : offset + n]
            offset += n

            parent_adrs = adrs.copy()
            parent_adrs.set_type(FORS_TREE)
            parent_adrs.set_keypair_address(adrs.get_keypair_address())
            parent_adrs.set_tree_height(s + 1)
            parent_adrs.set_tree_index(node_idx >> (s + 1))

            if (node_idx >> s) % 2 == 0:
                node = H(params, pk_seed, parent_adrs, node, auth_node)
            else:
                node = H(params, pk_seed, parent_adrs, auth_node, node)

        roots += node

    # Compress k roots via T_l
    fors_pk_adrs = adrs.copy()
    fors_pk_adrs.set_type(FORS_ROOTS)
    fors_pk_adrs.set_keypair_address(adrs.get_keypair_address())
    return T_l(params, pk_seed, fors_pk_adrs, roots)


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
