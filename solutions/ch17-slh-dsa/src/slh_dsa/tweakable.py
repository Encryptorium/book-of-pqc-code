"""Tweakable hash functions for SLH-DSA (FIPS 205 Sections 11.1-11.2).

SLH-DSA wraps standard hash functions in tweakable constructions that
take PK.seed and an ADRS as a tweak.  Three instantiations:

SHA2, category 1 (n=16, FIPS 205 Section 11.2.1):
    All functions use SHA-256.

SHA2, categories 3 and 5 (n in {24, 32}, FIPS 205 Section 11.2.2):
    F and PRF use SHA-256 with toByte(0, 64-n) padding.
    H and T_l use SHA-512 with toByte(0, 128-n) padding.
    H_msg uses MGF1-SHA-512, PRF_msg uses HMAC-SHA-512.

SHAKE (FIPS 205 Section 11.1):
    All functions use SHAKE256 with the full 32-byte ADRS.
"""

from __future__ import annotations

import hashlib
import hmac

from .adrs import ADRS
from .params import SLHDSAParams


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _sha512(data: bytes) -> bytes:
    return hashlib.sha512(data).digest()


def _shake256(data: bytes, n: int) -> bytes:
    return hashlib.shake_256(data).digest(n)


def _mgf1_sha256(seed: bytes, length: int) -> bytes:
    """MGF1 with SHA-256 (RFC 8017 Section B.2.1)."""
    out = b""
    counter = 0
    while len(out) < length:
        out += _sha256(seed + counter.to_bytes(4, "big"))
        counter += 1
    return out[:length]


def _mgf1_sha512(seed: bytes, length: int) -> bytes:
    """MGF1 with SHA-512."""
    out = b""
    counter = 0
    while len(out) < length:
        out += _sha512(seed + counter.to_bytes(4, "big"))
        counter += 1
    return out[:length]


# -- Core tweakable hash functions -----------------------------------------

def F(params: SLHDSAParams, pk_seed: bytes, adrs: ADRS, m1: bytes) -> bytes:
    """Chain function F: always SHA-256 for SHA2 parameter sets."""
    n = params.n
    if params.hash_family == "sha2":
        # F uses SHA-256 for ALL SHA2 parameter sets (Sections 11.2.1, 11.2.2)
        padding = b"\x00" * (64 - n)
        return _sha256(pk_seed + padding + adrs.compress() + m1)[:n]
    else:
        return _shake256(pk_seed + adrs.to_bytes() + m1, n)


def H(params: SLHDSAParams, pk_seed: bytes, adrs: ADRS,
      m1: bytes, m2: bytes) -> bytes:
    """Internal tree-node hash H (two n-byte inputs).

    SHA-256 for n=16 (Section 11.2.1), SHA-512 for n>=24 (Section 11.2.2).
    """
    n = params.n
    if params.hash_family == "sha2":
        if n == 16:
            padding = b"\x00" * (64 - n)
            return _sha256(pk_seed + padding + adrs.compress() + m1 + m2)[:n]
        else:
            padding = b"\x00" * (128 - n)
            return _sha512(pk_seed + padding + adrs.compress() + m1 + m2)[:n]
    else:
        return _shake256(pk_seed + adrs.to_bytes() + m1 + m2, n)


def T_l(params: SLHDSAParams, pk_seed: bytes, adrs: ADRS,
        m: bytes) -> bytes:
    """Compression hash T_l (variable-length input).

    SHA-256 for n=16 (Section 11.2.1), SHA-512 for n>=24 (Section 11.2.2).
    """
    n = params.n
    if params.hash_family == "sha2":
        if n == 16:
            padding = b"\x00" * (64 - n)
            return _sha256(pk_seed + padding + adrs.compress() + m)[:n]
        else:
            padding = b"\x00" * (128 - n)
            return _sha512(pk_seed + padding + adrs.compress() + m)[:n]
    else:
        return _shake256(pk_seed + adrs.to_bytes() + m, n)


def PRF(params: SLHDSAParams, pk_seed: bytes, sk_seed: bytes,
        adrs: ADRS) -> bytes:
    """Secret-value PRF: always SHA-256 for SHA2 parameter sets."""
    n = params.n
    if params.hash_family == "sha2":
        # PRF uses SHA-256 for ALL SHA2 parameter sets (Sections 11.2.1, 11.2.2)
        padding = b"\x00" * (64 - n)
        return _sha256(pk_seed + padding + adrs.compress() + sk_seed)[:n]
    else:
        return _shake256(pk_seed + adrs.to_bytes() + sk_seed, n)


def PRF_msg(params: SLHDSAParams, sk_prf: bytes, opt_rand: bytes,
            m: bytes) -> bytes:
    """Randomizer PRF for message hashing.

    HMAC-SHA-256 for n=16 (Section 11.2.1),
    HMAC-SHA-512 for n>=24 (Section 11.2.2).
    """
    n = params.n
    if params.hash_family == "sha2":
        if n == 16:
            return hmac.new(sk_prf, opt_rand + m, hashlib.sha256).digest()[:n]
        else:
            return hmac.new(sk_prf, opt_rand + m, hashlib.sha512).digest()[:n]
    else:
        return _shake256(sk_prf + opt_rand + m, n)


def H_msg(params: SLHDSAParams, r: bytes, pk_seed: bytes,
          pk_root: bytes, m: bytes) -> bytes:
    """Message hash producing the FORS digest and tree/leaf indices.

    MGF1-SHA-256 for n=16 (Section 11.2.1),
    MGF1-SHA-512 for n>=24 (Section 11.2.2).
    """
    n = params.n
    md_len = params.md_len
    if params.hash_family == "sha2":
        # The MGF1 seed is R || PK.seed || digest, in that order.  R and
        # PK.seed lead; the inner digest follows them.  Putting the digest
        # first still round-trips against a verifier making the same
        # mistake, which is why only an external vector catches it.
        if n == 16:
            digest = _sha256(r + pk_seed + pk_root + m)
            return _mgf1_sha256(r + pk_seed + digest, md_len)
        else:
            digest = _sha512(r + pk_seed + pk_root + m)
            return _mgf1_sha512(r + pk_seed + digest, md_len)
    else:
        return _shake256(r + pk_seed + pk_root + m, md_len)
