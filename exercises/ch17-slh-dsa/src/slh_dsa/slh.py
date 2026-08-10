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
    # EXERCISE: implement this function.
    #
    # Build a fresh ADRS, set only its layer address to d - 1, and call
    # xmss_node(0, hp) for PK.root. Keygen touches nothing but the top-layer
    # XMSS tree, so its cost is 2^hp WOTS+ keygens rather than 2^h, which is
    # why an 's' set with hp = 9 is slower to key than an 'f' set with hp =
    # 3. Return sk = SK.seed || SK.prf || PK.seed || PK.root, 4n bytes, and
    # pk = PK.seed || PK.root, 2n bytes. PK.root is stored inside the secret
    # key so signing never recomputes it. The ACVP keygen vectors compare
    # both of these byte for byte across all twelve parameter sets, so a
    # single wrong ADRS offset anywhere below this call surfaces here.
    #
    # Reference: Chapter 17, 'SLH-DSA at toy parameters' (FIPS 205 Algorithm 18)
    #
    # Proved by:
    #   tests/ch17/test_slhdsa_roundtrip.py
    #   tests/ch17/test_vectors.py
    raise NotImplementedError("exercise: slh_keygen_internal")


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
    # EXERCISE: implement this function.
    #
    # Slice sk into SK.seed, SK.prf, PK.seed, PK.root at n-byte boundaries,
    # then follow the five steps. R = PRF_msg(SK.prf, opt_rand, M). digest =
    # H_msg(R, PK.seed, PK.root, M). Split it with _split_digest into md,
    # idx_tree, idx_leaf. Build one ADRS at layer 0 with tree address
    # idx_tree and keypair address idx_leaf, sign md under it with
    # fors_sign, and recover PK_FORS by running fors_pk_from_sig over the
    # signature just produced rather than rebuilding the k trees.
    # Hypertree-sign PK_FORS at the same position. Return R || SIG_FORS ||
    # SIG_HT. Nothing here draws randomness: opt_rand is the caller's, which
    # is what makes the deterministic variant reproducible.
    #
    # Reference: Chapter 17, 'Full SLH-DSA signing' (FIPS 205 Algorithm 19)
    #
    # Proved by:
    #   tests/ch17/test_slhdsa_roundtrip.py
    #   tests/ch17/test_vectors.py
    raise NotImplementedError("exercise: slh_sign_internal")


# -- Verify (FIPS 205 Algorithm 20, slh_verify_internal) ------------------

def slh_verify(params: SLHDSAParams, pk: bytes, message: bytes,
               sig: bytes) -> bool:
    """Verify an SLH-DSA signature."""
    # EXERCISE: implement this function.
    #
    # Split pk into PK.seed and PK.root. Reject any signature whose length
    # is not n + k(1 + a)n + d(ell + hp)n before hashing anything, then cut
    # it at those offsets into R, SIG_FORS, SIG_HT. Recompute the digest
    # from the transmitted R with H_msg and split it exactly as the signer
    # did: the signing position is derived from the message, never carried
    # in the signature, so an attacker cannot choose it. Recover PK_FORS
    # with fors_pk_from_sig under an ADRS at layer 0 with tree address
    # idx_tree and keypair address idx_leaf, then return ht_verify on that
    # value. A wrong message moves idx_tree and idx_leaf as well as md, so a
    # forgery usually dies at the hypertree rather than inside FORS.
    #
    # Reference: Chapter 17, 'Full SLH-DSA signing' (FIPS 205 Algorithm 20)
    #
    # Proved by:
    #   tests/ch17/test_slhdsa_roundtrip.py
    #   tests/ch17/test_vectors.py
    raise NotImplementedError("exercise: slh_verify")
