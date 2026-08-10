"""Hypertree with ADRS for SLH-DSA (FIPS 205 Sections 6-7, Algorithms 9-13).

The hypertree consists of d layers of XMSS trees.  The bottom layer
(layer 0) signs the FORS public key; each upper layer signs the root
of the tree below.  The top-layer root is part of the SLH-DSA public
key.
"""

from __future__ import annotations

from .adrs import ADRS, TREE
from .params import SLHDSAParams
from .tweakable import H
from .wots import wots_pkgen, wots_sign, wots_pk_from_sig


def xmss_node(params: SLHDSAParams, sk_seed: bytes,
              i: int, z: int, pk_seed: bytes, adrs: ADRS) -> bytes:
    """Compute tree node at position *i* and height *z* (FIPS 205 Algorithm 9).

    Leaves (z == 0) are compressed WOTS+ public keys via wots_pkgen.
    Internal nodes combine children via H with TREE-type ADRS.
    """
    if z == 0:
        leaf_adrs = adrs.copy()
        leaf_adrs.set_keypair_address(i)
        return wots_pkgen(params, sk_seed, pk_seed, leaf_adrs)

    left = xmss_node(params, sk_seed, 2 * i, z - 1, pk_seed, adrs)
    right = xmss_node(params, sk_seed, 2 * i + 1, z - 1, pk_seed, adrs)

    node_adrs = adrs.copy()
    node_adrs.set_type(TREE)
    node_adrs.set_tree_height(z)
    node_adrs.set_tree_index(i)
    return H(params, pk_seed, node_adrs, left, right)


def _xmss_sign(params: SLHDSAParams, sk_seed: bytes, pk_seed: bytes,
               adrs: ADRS, message: bytes, idx: int) -> bytes:
    """Sign *message* at leaf *idx* in a single XMSS tree.

    Returns the WOTS+ signature || authentication path, each node n bytes.
    Total: (ell + hp) * n bytes.
    """
    hp = params.hp

    # WOTS+ sign
    sig_adrs = adrs.copy()
    sig_adrs.set_keypair_address(idx)
    sig = wots_sign(params, sk_seed, pk_seed, sig_adrs, message)

    # Authentication path: sibling nodes at each height
    auth = b""
    for j in range(hp):
        # Sibling index at height j
        s = (idx >> j) ^ 1
        auth += xmss_node(params, sk_seed, s, j, pk_seed, adrs)

    return sig + auth


# -- Hypertree sign (FIPS 205 Algorithm 12, ht_sign) -----------------------

def ht_sign(params: SLHDSAParams, sk_seed: bytes, pk_seed: bytes,
            message: bytes, idx_tree: int, idx_leaf: int) -> bytes:
    """Sign through d XMSS layers (FIPS 205 Algorithm 12).

    Returns the concatenation of d layer signatures, each
    (ell + hp) * n bytes.
    """
    # EXERCISE: implement this function.
    #
    # Layer 0 signs the caller's message: build a fresh ADRS with layer
    # address 0 and tree address idx_tree, call _xmss_sign at leaf idx_leaf,
    # then compute that subtree's root with xmss_node(0, hp). Each layer
    # above signs the root of the layer below. For layer j take the bottom
    # hp bits of idx_tree as this layer's leaf index, then shift idx_tree
    # right by hp to get this layer's tree address; splitting before the
    # shift is what keeps the two in step. Build a fresh ADRS at layer j,
    # sign the running root at that leaf, recompute the new root, and
    # append. The output is d blocks of (ell + hp) * n bytes in layer order.
    #
    # Reference: Chapter 17, 'The hypertree' (FIPS 205 Algorithm 12)
    #
    # Proved by:
    #   tests/ch17/test_hypertree_roundtrip.py
    #   tests/ch17/test_vectors.py
    raise NotImplementedError("exercise: ht_sign")


# -- Hypertree verify (FIPS 205 Algorithm 13, ht_verify) -------------------

def ht_verify(params: SLHDSAParams, pk_seed: bytes, pk_root: bytes,
              message: bytes, sig_ht: bytes,
              idx_tree: int, idx_leaf: int) -> bool:
    """Verify a hypertree signature (FIPS 205 Algorithm 13)."""
    # EXERCISE: implement this function.
    #
    # Mirror the signer with no secret material. Slice sig_ht into d fixed
    # blocks of (ell + hp) * n bytes, each an ell * n WOTS+ signature
    # followed by hp authentication nodes. Layer 0 uses idx_leaf and
    # idx_tree as given; every layer above takes the bottom hp bits of
    # idx_tree as its leaf index and shifts idx_tree right by hp for its
    # tree address. Recover the WOTS+ public key from the block with
    # wots_pk_from_sig under an address carrying the layer, tree, and
    # keypair address, then climb hp levels with H under TREE addresses at
    # tree height s + 1 and tree index idx >> 1, ordering children by the
    # low bit of idx and halving idx each level. Carry the resulting root up
    # as the next layer's message. Return whether the final root equals
    # pk_root: every intermediate root is attacker-supplied until that one
    # comparison.
    #
    # Reference: Chapter 17, 'The hypertree' (FIPS 205 Algorithm 13)
    #
    # Proved by:
    #   tests/ch17/test_hypertree_roundtrip.py
    #   tests/ch17/test_vectors.py
    raise NotImplementedError("exercise: ht_verify")
