"""WOTS+ with ADRS for SLH-DSA (FIPS 205 Section 5, Algorithms 3-8).

This module re-implements WOTS+ with proper ADRS-based domain
separation, replacing the simplified chain function from Ch 15.
Every hash call carries an ADRS that encodes the chain position,
preventing cross-chain collisions.
"""

from __future__ import annotations

import math

from .adrs import ADRS, WOTS_HASH, WOTS_PK, WOTS_PRF
from .params import SLHDSAParams
from .tweakable import F, PRF, T_l


# -- Base-w encoding (FIPS 205 Algorithm 4, base_2b) -----------------------

def base_w(data: bytes, w: int, out_len: int) -> list[int]:
    """Encode *data* as *out_len* base-*w* digits, MSB-first per byte."""
    lg_w = int(math.log2(w))
    digits: list[int] = []
    for byte_val in data:
        for shift in range(8 - lg_w, -1, -lg_w):
            digits.append((byte_val >> shift) & (w - 1))
            if len(digits) == out_len:
                return digits
    return digits[:out_len]


# -- Chain function (FIPS 205 Algorithm 5) ---------------------------------

def chain(params: SLHDSAParams, x: bytes, i: int, s: int,
          pk_seed: bytes, adrs: ADRS) -> bytes:
    """Iterate the chain function F *s* times from position *i*.

    ADRS must have type WOTS_HASH and chain_address already set.
    """
    # EXERCISE: implement this function.
    #
    # Iterate F s times starting from position i, returning x unchanged when
    # s is 0. Before each call set the ADRS hash address to the current step
    # index j, running i, i + 1, ..., i + s - 1, so no two links anywhere in
    # the key hash under the same address. The caller has already set the
    # type to WOTS_HASH and the chain address, so this function moves only
    # the hash address. It mutates the ADRS it was handed rather than
    # copying, which is why every caller passes a working copy.
    #
    # Reference: Chapter 17, 'WOTS+ with ADRS' (FIPS 205 Algorithm 5)
    #
    # Proved by:
    #   tests/ch17/test_wots_roundtrip.py
    #   tests/ch17/test_vectors.py
    raise NotImplementedError("exercise: chain")


# -- WOTS+ keygen (FIPS 205 Algorithm 6, wots_pkGen) -----------------------

def wots_pkgen(params: SLHDSAParams, sk_seed: bytes, pk_seed: bytes,
               adrs: ADRS) -> bytes:
    """Generate a WOTS+ compressed public key (n bytes).

    The ADRS must have layer_address, tree_address, and keypair_address
    already set.  This function uses three ADRS types internally:
    WOTS_PRF for secret generation, WOTS_HASH for chaining, and
    WOTS_PK for public-key compression.
    """
    n = params.n
    ell = params.ell
    w = params.w

    # Generate secret values via PRF with WOTS_PRF type
    sk_adrs = adrs.copy()
    sk_adrs.set_type(WOTS_PRF)
    sk_adrs.set_keypair_address(adrs.get_keypair_address())

    # Chain each secret to the endpoint via F with WOTS_HASH type
    wots_adrs = adrs.copy()
    wots_adrs.set_type(WOTS_HASH)
    wots_adrs.set_keypair_address(adrs.get_keypair_address())

    tmp = b""
    for i in range(ell):
        sk_adrs.set_chain_address(i)
        sk_i = PRF(params, pk_seed, sk_seed, sk_adrs)

        wots_adrs.set_chain_address(i)
        tmp += chain(params, sk_i, 0, w - 1, pk_seed, wots_adrs)

    # Compress via T_l with WOTS_PK type
    pk_adrs = adrs.copy()
    pk_adrs.set_type(WOTS_PK)
    pk_adrs.set_keypair_address(adrs.get_keypair_address())

    return T_l(params, pk_seed, pk_adrs, tmp)


# -- WOTS+ sign (FIPS 205 Algorithm 7) ------------------------------------

def wots_sign(params: SLHDSAParams, sk_seed: bytes, pk_seed: bytes,
              adrs: ADRS, message: bytes) -> bytes:
    """Sign an n-byte message with WOTS+.

    Returns the signature as ell * n concatenated bytes.
    """
    # EXERCISE: implement this function.
    #
    # Encode the n-byte message as ell_1 base-w digits with base_w, then
    # compute the checksum as the sum of w - 1 - digit over them and encode
    # it as ell_2 more digits. The checksum needs left-alignment before it
    # is serialized: it occupies ell_2 * lg_w bits, so shift it left by 8 *
    # ceil(bits / 8) - bits and write that many bytes, because base_w reads
    # digits from the top of each byte downward. Then, exactly as in
    # wots_pkgen, derive secret i under a WOTS_PRF copy and chain it forward
    # digits[i] steps rather than w - 1, under a WOTS_HASH copy. The
    # signature is the ell partial chain values concatenated, ell * n bytes.
    #
    # Reference: Chapter 17, 'WOTS+ with ADRS' (FIPS 205 Algorithm 7)
    #
    # Proved by:
    #   tests/ch17/test_wots_roundtrip.py
    #   tests/ch17/test_vectors.py
    raise NotImplementedError("exercise: wots_sign")


# -- WOTS+ pk from sig (FIPS 205 Algorithm 8, wots_pkFromSig) -------------

def wots_pk_from_sig(params: SLHDSAParams, pk_seed: bytes,
                     adrs: ADRS, sig: bytes, message: bytes) -> bytes:
    """Recover the WOTS+ compressed public key from a signature.

    Used by the verifier: complete each chain from the signature value
    forward to the endpoint, then compress via T_l.
    """
    # EXERCISE: implement this function.
    #
    # Recompute the same ell digits from the message the signer did,
    # checksum and left-shift included, then finish each chain instead of
    # starting it: chain(sig_i, digits[i], w - 1 - digits[i], ...) walks
    # from where the signer stopped to the endpoint. Compress the ell
    # endpoints with T_l under a WOTS_PK copy. This returns a candidate
    # public key, never a boolean; the caller decides whether it matches.
    # The checksum digits are what make forgery hard, because advancing any
    # message digit lowers the checksum and no chain can be walked
    # backwards.
    #
    # Reference: Chapter 17, 'WOTS+ with ADRS' (FIPS 205 Algorithm 8)
    #
    # Proved by:
    #   tests/ch17/test_wots_roundtrip.py
    #   tests/ch17/test_vectors.py
    raise NotImplementedError("exercise: wots_pk_from_sig")
