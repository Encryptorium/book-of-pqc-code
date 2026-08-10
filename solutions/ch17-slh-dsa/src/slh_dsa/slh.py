"""Top-level SLH-DSA keygen, sign, verify (FIPS 205 Section 9, Algorithms 18-20).

This module assembles FORS, hypertree, tweakable hashes, and ADRS into
the complete SLH-DSA construction.
"""

from __future__ import annotations

import os

from .adrs import ADRS
from .params import SLHDSAParams
from .tweakable import H_msg, PRF_msg
from .fors import fors_sign, fors_pk_from_sig
from .hypertree import ht_sign, ht_verify, xmss_node


# -- Message digest parsing ------------------------------------------------

def _split_digest(params: SLHDSAParams, digest: bytes
                  ) -> tuple[bytes, int, int]:
    """Split the H_msg digest into (md, idx_tree, idx_leaf).

    md: first ceil(k*a / 8) bytes (FORS message)
    idx_tree: next ceil((h - hp) / 8) bytes, reduced mod 2^(h - hp)
    idx_leaf: next ceil(hp / 8) bytes, reduced mod 2^hp
    """
    ka_bytes = (params.k * params.a + 7) // 8
    tree_bits = params.h - params.hp
    tree_bytes = (tree_bits + 7) // 8
    leaf_bytes = (params.hp + 7) // 8

    md = digest[:ka_bytes]

    tree_raw = digest[ka_bytes : ka_bytes + tree_bytes]
    idx_tree = int.from_bytes(tree_raw, "big") & ((1 << tree_bits) - 1)

    leaf_raw = digest[ka_bytes + tree_bytes : ka_bytes + tree_bytes + leaf_bytes]
    idx_leaf = int.from_bytes(leaf_raw, "big") & ((1 << params.hp) - 1)

    return md, idx_tree, idx_leaf


# -- Keygen (FIPS 205 Algorithm 18, slh_keygen_internal) -------------------

def slh_keygen(params: SLHDSAParams,
               sk_seed: bytes | None = None,
               sk_prf: bytes | None = None,
               pk_seed: bytes | None = None) -> tuple[bytes, bytes]:
    """Generate an SLH-DSA keypair.

    Returns (sk, pk) where:
        sk = SK.seed || SK.prf || PK.seed || PK.root  (4n bytes)
        pk = PK.seed || PK.root                       (2n bytes)
    """
    n = params.n
    if sk_seed is None:
        sk_seed = os.urandom(n)
    if sk_prf is None:
        sk_prf = os.urandom(n)
    if pk_seed is None:
        pk_seed = os.urandom(n)

    return slh_keygen_internal(params, sk_seed, sk_prf, pk_seed)


def slh_keygen_internal(params: SLHDSAParams, sk_seed: bytes,
                        sk_prf: bytes, pk_seed: bytes) -> tuple[bytes, bytes]:
    """Deterministic keygen for test vector matching."""
    n = params.n
    hp = params.hp
    d = params.d

    adrs = ADRS()
    adrs.set_layer_address(d - 1)
    pk_root = xmss_node(params, sk_seed, 0, hp, pk_seed, adrs)

    sk = sk_seed + sk_prf + pk_seed + pk_root
    pk = pk_seed + pk_root
    return sk, pk


# -- Sign (FIPS 205 Algorithm 19, slh_sign_internal) ----------------------

def slh_sign(params: SLHDSAParams, sk: bytes, message: bytes,
             randomize: bool = True) -> bytes:
    """Sign a message with SLH-DSA.

    Returns the signature: R || SIG_FORS || SIG_HT.
    """
    n = params.n

    sk_seed = sk[:n]
    sk_prf = sk[n : 2 * n]
    pk_seed = sk[2 * n : 3 * n]
    pk_root = sk[3 * n : 4 * n]

    if randomize:
        opt_rand = os.urandom(n)
    else:
        opt_rand = pk_seed

    return slh_sign_internal(params, sk, message, opt_rand)


def slh_sign_internal(params: SLHDSAParams, sk: bytes, message: bytes,
                      opt_rand: bytes) -> bytes:
    """Deterministic sign for test vector matching."""
    n = params.n

    sk_seed = sk[:n]
    sk_prf = sk[n : 2 * n]
    pk_seed = sk[2 * n : 3 * n]
    pk_root = sk[3 * n : 4 * n]

    # Step 1: compute randomizer R
    r = PRF_msg(params, sk_prf, opt_rand, message)

    # Step 2: compute message digest
    digest = H_msg(params, r, pk_seed, pk_root, message)

    # Step 3: split digest into FORS message, tree index, leaf index
    md, idx_tree, idx_leaf = _split_digest(params, digest)

    # Step 4: FORS sign
    fors_adrs = ADRS()
    fors_adrs.set_layer_address(0)
    fors_adrs.set_tree_address(idx_tree)
    fors_adrs.set_keypair_address(idx_leaf)

    sig_fors = fors_sign(params, sk_seed, pk_seed, fors_adrs, md)

    # Step 5: compute FORS public key
    pk_fors = fors_pk_from_sig(params, pk_seed, fors_adrs, sig_fors, md)

    # Step 6: hypertree sign the FORS public key
    sig_ht = ht_sign(params, sk_seed, pk_seed, pk_fors, idx_tree, idx_leaf)

    return r + sig_fors + sig_ht


# -- Verify (FIPS 205 Algorithm 20, slh_verify_internal) ------------------

def slh_verify(params: SLHDSAParams, pk: bytes, message: bytes,
               sig: bytes) -> bool:
    """Verify an SLH-DSA signature."""
    n = params.n
    k = params.k
    a = params.a
    d = params.d
    hp = params.hp
    ell = params.ell

    pk_seed = pk[:n]
    pk_root = pk[n : 2 * n]

    # Parse signature
    fors_sig_len = k * (1 + a) * n
    ht_sig_len = d * (ell + hp) * n
    expected_len = n + fors_sig_len + ht_sig_len
    if len(sig) != expected_len:
        return False

    r = sig[:n]
    sig_fors = sig[n : n + fors_sig_len]
    sig_ht = sig[n + fors_sig_len :]

    # Recompute message digest
    digest = H_msg(params, r, pk_seed, pk_root, message)
    md, idx_tree, idx_leaf = _split_digest(params, digest)

    # Recover FORS public key
    fors_adrs = ADRS()
    fors_adrs.set_layer_address(0)
    fors_adrs.set_tree_address(idx_tree)
    fors_adrs.set_keypair_address(idx_leaf)
    pk_fors = fors_pk_from_sig(params, pk_seed, fors_adrs, sig_fors, md)

    # Verify hypertree signature on the FORS public key
    return ht_verify(params, pk_seed, pk_root, pk_fors, sig_ht,
                     idx_tree, idx_leaf)
