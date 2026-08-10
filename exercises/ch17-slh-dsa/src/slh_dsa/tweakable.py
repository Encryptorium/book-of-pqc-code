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
    # EXERCISE: implement this function.
    #
    # For the SHA2 family, return the first n bytes of SHA-256(PK.seed ||
    # toByte(0, 64 - n) || ADRS_compressed || M1). PK.seed and the zero
    # padding together fill exactly one 64-byte SHA-256 block, so the
    # compressed address and M1 begin the second block. F stays on SHA-256
    # at every SHA2 parameter set, n = 24 and n = 32 included, unlike H and
    # T_l: its single n-byte input keeps the preimage margin adequate. For
    # the SHAKE family, absorb PK.seed || full 32-byte ADRS || M1 into
    # SHAKE256 and squeeze n bytes.
    #
    # Reference: Chapter 17, 'Tweakable hash functions' (FIPS 205 Sections 11.1, 11.2.1, 11.2.2)
    #
    # Proved by:
    #   tests/ch17/test_tweakable.py
    #   tests/ch17/test_vectors.py
    raise NotImplementedError("exercise: F")


def H(params: SLHDSAParams, pk_seed: bytes, adrs: ADRS,
      m1: bytes, m2: bytes) -> bytes:
    """Internal tree-node hash H (two n-byte inputs).

    SHA-256 for n=16 (Section 11.2.1), SHA-512 for n>=24 (Section 11.2.2).
    """
    # EXERCISE: implement this function.
    #
    # The two-input node hash, same shape as F with M1 || M2 in the message
    # position, but the primitive depends on n. At n = 16 use SHA-256 with
    # toByte(0, 64 - n) padding. At n = 24 or 32 switch to SHA-512 with
    # toByte(0, 128 - n) padding, keeping the one-block alignment. That
    # switch is not an efficiency choice: SHA-256's 256-bit chaining value
    # is too narrow for the multi-target second-preimage margin category 5
    # needs, which is what FIPS 205 Appendix A records. SHAKE sets take
    # SHAKE256(PK.seed || ADRS || M1 || M2) squeezed to n.
    #
    # Reference: Chapter 17, 'Hash function split for categories 3 and 5' (FIPS 205 Sections 11.1, 11.2.1, 11.2.2)
    #
    # Proved by:
    #   tests/ch17/test_tweakable.py
    #   tests/ch17/test_vectors.py
    raise NotImplementedError("exercise: H")


def T_l(params: SLHDSAParams, pk_seed: bytes, adrs: ADRS,
        m: bytes) -> bytes:
    """Compression hash T_l (variable-length input).

    SHA-256 for n=16 (Section 11.2.1), SHA-512 for n>=24 (Section 11.2.2).
    """
    # EXERCISE: implement this function.
    #
    # The variable-length compression hash: it takes the ell concatenated
    # WOTS+ chain endpoints, or the k concatenated FORS roots, and returns n
    # bytes. Identical to H except that the message is one input of
    # arbitrary length rather than two n-byte inputs, so the same padding
    # widths and the same SHA-256 at n = 16 and SHA-512 above it apply, and
    # the SHAKE branch is SHAKE256(PK.seed || ADRS || M) to n bytes.
    #
    # Reference: Chapter 17, 'Tweakable hash functions' (FIPS 205 Sections 11.1, 11.2.1, 11.2.2)
    #
    # Proved by:
    #   tests/ch17/test_tweakable.py
    #   tests/ch17/test_vectors.py
    raise NotImplementedError("exercise: T_l")


def PRF(params: SLHDSAParams, pk_seed: bytes, sk_seed: bytes,
        adrs: ADRS) -> bytes:
    """Secret-value PRF: always SHA-256 for SHA2 parameter sets."""
    # EXERCISE: implement this function.
    #
    # The secret-value PRF, block layout identical to F with SK.seed sitting
    # where M1 sits: SHA-256(PK.seed || toByte(0, 64 - n) || ADRS_compressed
    # || SK.seed) truncated to n, on SHA-256 for every SHA2 set. The SHAKE
    # branch is SHAKE256(PK.seed || ADRS || SK.seed) to n bytes. The address
    # is the entire reason one SK.seed can expand into every WOTS+ and FORS
    # secret in the key without two of them ever coinciding, so a copy with
    # a stale chain address silently produces the wrong secret rather than
    # an error.
    #
    # Reference: Chapter 17, 'Tweakable hash functions' (FIPS 205 Sections 11.1, 11.2.1, 11.2.2)
    #
    # Proved by:
    #   tests/ch17/test_tweakable.py
    #   tests/ch17/test_vectors.py
    raise NotImplementedError("exercise: PRF")


def PRF_msg(params: SLHDSAParams, sk_prf: bytes, opt_rand: bytes,
            m: bytes) -> bytes:
    """Randomizer PRF for message hashing.

    HMAC-SHA-256 for n=16 (Section 11.2.1),
    HMAC-SHA-512 for n>=24 (Section 11.2.2).
    """
    # EXERCISE: implement this function.
    #
    # Produce the randomizer R that goes into H_msg and is transmitted as
    # the first n bytes of the signature. Key an HMAC with SK.prf over
    # opt_rand || M and truncate to n: HMAC-SHA-256 at n = 16, HMAC-SHA-512
    # at n = 24 and 32. The SHAKE branch is SHAKE256(SK.prf || opt_rand ||
    # M) to n bytes, prefix-keyed with no HMAC wrapper because a sponge is
    # not length-extendable. Note that this takes no ADRS: it binds the
    # message rather than a tree position.
    #
    # Reference: Chapter 17, 'Full SLH-DSA signing' (FIPS 205 Sections 11.1, 11.2.1, 11.2.2)
    #
    # Proved by:
    #   tests/ch17/test_tweakable.py
    #   tests/ch17/test_vectors.py
    raise NotImplementedError("exercise: PRF_msg")


def H_msg(params: SLHDSAParams, r: bytes, pk_seed: bytes,
          pk_root: bytes, m: bytes) -> bytes:
    """Message hash producing the FORS digest and tree/leaf indices.

    MGF1-SHA-256 for n=16 (Section 11.2.1),
    MGF1-SHA-512 for n>=24 (Section 11.2.2).
    """
    # EXERCISE: implement this function.
    #
    # Return md_len bytes carrying the FORS message digest and the tree and
    # leaf index material together. The SHAKE branch is SHAKE256(R ||
    # PK.seed || PK.root || M) squeezed to md_len. The SHA2 branch hashes R
    # || PK.seed || PK.root || M with SHA-256 at n = 16 or SHA-512 above,
    # then seeds MGF1 with R || PK.seed || that digest, in that order,
    # taking md_len bytes. Repeating R and PK.seed ahead of the digest is a
    # FIPS 205 Appendix A change made to mitigate multi-target long-message
    # second-preimage attacks; both omitting them and appending them after
    # the digest still round-trip, so the sign and verify tests alone would
    # not catch either. The ACVP sigVer vectors are what catch them, and the
    # second of those two was live in this package until 2026-08-10.
    #
    # Reference: Chapter 17, 'Hash function split for categories 3 and 5' (FIPS 205 Sections 11.1, 11.2.1, 11.2.2)
    #
    # Proved by:
    #   tests/ch17/test_tweakable.py
    #   tests/ch17/test_vectors.py
    raise NotImplementedError("exercise: H_msg")
