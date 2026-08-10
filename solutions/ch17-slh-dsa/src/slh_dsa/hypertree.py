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
    d = params.d
    hp = params.hp
    n = params.n

    # Layer 0: sign the message
    adrs = ADRS()
    adrs.set_layer_address(0)
    adrs.set_tree_address(idx_tree)
    sig_ht = _xmss_sign(params, sk_seed, pk_seed, adrs, message, idx_leaf)

    # Compute the layer-0 tree root (what layer 1 will sign)
    root = xmss_node(params, sk_seed, 0, hp, pk_seed, adrs)

    # Upper layers
    for j in range(1, d):
        # The leaf index in this layer is the bottom hp bits of idx_tree
        idx_leaf_j = idx_tree & ((1 << hp) - 1)
        idx_tree = idx_tree >> hp

        adrs = ADRS()
        adrs.set_layer_address(j)
        adrs.set_tree_address(idx_tree)

        sig_ht += _xmss_sign(params, sk_seed, pk_seed, adrs, root, idx_leaf_j)
        root = xmss_node(params, sk_seed, 0, hp, pk_seed, adrs)

    return sig_ht


# -- Hypertree verify (FIPS 205 Algorithm 13, ht_verify) -------------------

def ht_verify(params: SLHDSAParams, pk_seed: bytes, pk_root: bytes,
              message: bytes, sig_ht: bytes,
              idx_tree: int, idx_leaf: int) -> bool:
    """Verify a hypertree signature (FIPS 205 Algorithm 13)."""
    d = params.d
    hp = params.hp
    n = params.n
    ell = params.ell
    layer_sig_len = (ell + hp) * n

    current_msg = message

    for j in range(d):
        if j == 0:
            leaf_j = idx_leaf
            tree_j = idx_tree
        else:
            leaf_j = idx_tree & ((1 << hp) - 1)
            idx_tree = idx_tree >> hp
            tree_j = idx_tree

        # Extract this layer's signature
        offset = j * layer_sig_len
        layer_sig = sig_ht[offset : offset + layer_sig_len]
        wots_sig = layer_sig[: ell * n]
        auth_path = layer_sig[ell * n :]

        # Recover WOTS+ public key from signature
        adrs = ADRS()
        adrs.set_layer_address(j)
        adrs.set_tree_address(tree_j)
        adrs.set_keypair_address(leaf_j)
        node = wots_pk_from_sig(params, pk_seed, adrs, wots_sig, current_msg)

        # Walk up the authentication path
        idx = leaf_j
        for s in range(hp):
            auth_node = auth_path[s * n : (s + 1) * n]
            tree_adrs = ADRS()
            tree_adrs.set_layer_address(j)
            tree_adrs.set_tree_address(tree_j)
            tree_adrs.set_type(TREE)
            tree_adrs.set_tree_height(s + 1)
            tree_adrs.set_tree_index(idx >> 1)

            if idx % 2 == 0:
                node = H(params, pk_seed, tree_adrs, node, auth_node)
            else:
                node = H(params, pk_seed, tree_adrs, auth_node, node)
            idx = idx >> 1

        current_msg = node

    return current_msg == pk_root
