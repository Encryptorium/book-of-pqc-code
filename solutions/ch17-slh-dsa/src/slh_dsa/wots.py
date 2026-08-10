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
    tmp = x
    for j in range(i, i + s):
        adrs.set_hash_address(j)
        tmp = F(params, pk_seed, adrs, tmp)
    return tmp


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
    n = params.n
    w = params.w
    ell = params.ell
    ell_1 = params.ell_1

    # Encode message + checksum in base w
    msg_digits = base_w(message, w, ell_1)
    csum = sum(w - 1 - d for d in msg_digits)

    # Encode checksum in base w
    lg_w = params.lg_w
    total_bits = params.ell_2 * lg_w
    num_bytes = math.ceil(total_bits / 8)
    shift = 8 * num_bytes - total_bits
    c_bytes = (csum << shift).to_bytes(num_bytes, "big")
    csum_digits = base_w(c_bytes, w, params.ell_2)

    digits = msg_digits + csum_digits

    # Generate secret values and chain to digit positions
    sk_adrs = adrs.copy()
    sk_adrs.set_type(WOTS_PRF)
    sk_adrs.set_keypair_address(adrs.get_keypair_address())

    wots_adrs = adrs.copy()
    wots_adrs.set_type(WOTS_HASH)
    wots_adrs.set_keypair_address(adrs.get_keypair_address())

    sig = b""
    for i in range(ell):
        sk_adrs.set_chain_address(i)
        sk_i = PRF(params, pk_seed, sk_seed, sk_adrs)

        wots_adrs.set_chain_address(i)
        sig += chain(params, sk_i, 0, digits[i], pk_seed, wots_adrs)

    return sig


# -- WOTS+ pk from sig (FIPS 205 Algorithm 8, wots_pkFromSig) -------------

def wots_pk_from_sig(params: SLHDSAParams, pk_seed: bytes,
                     adrs: ADRS, sig: bytes, message: bytes) -> bytes:
    """Recover the WOTS+ compressed public key from a signature.

    Used by the verifier: complete each chain from the signature value
    forward to the endpoint, then compress via T_l.
    """
    n = params.n
    w = params.w
    ell = params.ell
    ell_1 = params.ell_1

    # Encode message + checksum
    msg_digits = base_w(message, w, ell_1)
    csum = sum(w - 1 - d for d in msg_digits)

    lg_w = params.lg_w
    total_bits = params.ell_2 * lg_w
    num_bytes = math.ceil(total_bits / 8)
    shift = 8 * num_bytes - total_bits
    c_bytes = (csum << shift).to_bytes(num_bytes, "big")
    csum_digits = base_w(c_bytes, w, params.ell_2)

    digits = msg_digits + csum_digits

    # Complete each chain from the signature value
    wots_adrs = adrs.copy()
    wots_adrs.set_type(WOTS_HASH)
    wots_adrs.set_keypair_address(adrs.get_keypair_address())

    tmp = b""
    for i in range(ell):
        sig_i = sig[i * n : (i + 1) * n]
        wots_adrs.set_chain_address(i)
        tmp += chain(params, sig_i, digits[i], w - 1 - digits[i],
                     pk_seed, wots_adrs)

    # Compress via T_l
    pk_adrs = adrs.copy()
    pk_adrs.set_type(WOTS_PK)
    pk_adrs.set_keypair_address(adrs.get_keypair_address())

    return T_l(params, pk_seed, pk_adrs, tmp)
