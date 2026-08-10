"""Rejection sampling for ML-DSA (FIPS 204 §7.3, plus §7.1's Algorithms 14-15).

Every structured value in ML-DSA is squeezed out of a SHAKE stream and filtered:

* ``ExpandA`` (SHAKE128) fills the public matrix A directly in the NTT domain,
  rejecting three-byte reads that land at or above q.
* ``ExpandS`` (SHAKE256) fills the short secret vectors s1, s2, rejecting
  half-bytes outside the small window that maps into [-eta, eta].
* ``ExpandMask`` (SHAKE256) fills the per-attempt mask y; it does *not* reject,
  it BitUnpacks a fixed number of bytes into the range (-gamma1, gamma1].
* ``SampleInBall`` (SHAKE256) builds the challenge c: exactly tau coefficients set
  to +-1 and the rest zero, placed by a Fisher-Yates-style swap driven by the
  stream, with the signs taken from the first eight squeezed bytes.

The SHAKE stream is grown on demand by re-squeezing the same hash object to a
larger length (its output is a stable prefix), the same idiom used by
``ch11-mlkem/sampling.py``.
"""

from __future__ import annotations

import hashlib

import numpy as np

from .params import ML_DSA_Q as Q, MLDSAParams
from .hashes import integer_to_bytes
from .encode import bit_unpack


# Bytes to extend the squeeze by when a sampler runs out. hashlib's SHAKE digest
# is a stable prefix, so any positive step is correct regardless of sponge rate;
# 168 (the SHAKE128 rate) is just a convenient granularity.
_BLOCK = 168


# --- Coefficient predicates (FIPS 204 Algorithms 14-15). ---

def coeff_from_three_bytes(b0: int, b1: int, b2: int) -> int | None:
    """FIPS 204 Algorithm 14. Little-endian 23-bit value (top bit of b2 cleared),
    accepted iff < q."""
    # EXERCISE: implement this function.
    #
    # Read three stream bytes little-endian into a 23-bit value (clear the
    # top bit of b2, then z = (b2 << 16) | (b1 << 8) | b0). Accept z iff z <
    # q, else return None. This is the rejection predicate ExpandA uses to
    # fill A directly in the NTT domain.
    #
    # Reference: Chapter 12, 'Sampling: SampleInBall, ExpandA, ExpandS, ExpandMask' (FIPS 204 Algorithm 14)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_sampling.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: coeff_from_three_bytes")


def coeff_from_half_byte(b: int, eta: int) -> int | None:
    """FIPS 204 Algorithm 15. Map a half-byte into [-eta, eta] or reject."""
    # EXERCISE: implement this function.
    #
    # Map a half-byte b into [-eta, eta] or reject. For eta = 2, accept b <
    # 15 and return 2 - (b % 5). For eta = 4, accept b < 9 and return 4 - b.
    # Anything else returns None. This is the predicate ExpandS uses for the
    # short secret coefficients.
    #
    # Reference: Chapter 12, 'Sampling: SampleInBall, ExpandA, ExpandS, ExpandMask' (FIPS 204 Algorithm 15)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_sampling.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: coeff_from_half_byte")


# --- Challenge sampler (FIPS 204 Algorithm 29). ---

def sample_in_ball(params: MLDSAParams, rho: bytes) -> np.ndarray:
    """Sample the challenge c: tau coefficients of +-1, the rest zero."""
    assert len(rho) == params.c_tilde_len(), (
        f"sample_in_ball: rho must be {params.c_tilde_len()} bytes, got {len(rho)}"
    )
    tau = params.tau
    xof = hashlib.shake_256(rho)
    need = 8
    stream = xof.digest(need)
    signs = int.from_bytes(stream[:8], "little")  # bit n == BytesToBits(s)[n]
    c = np.zeros(256, dtype=np.int64)
    pos = 8
    for i in range(256 - tau, 256):
        while True:
            if pos >= len(stream):
                need += _BLOCK
                stream = xof.digest(need)
            j = stream[pos]
            pos += 1
            if j <= i:
                break
        c[i] = c[j]
        bit = (signs >> (i + tau - 256)) & 1
        c[j] = -1 if bit else 1
    return c


# --- Matrix expansion (FIPS 204 Algorithms 30, 32). ---

def rej_ntt_poly(rho_prime: bytes) -> np.ndarray:
    """FIPS 204 Algorithm 30. One NTT-domain polynomial by three-byte rejection."""
    # EXERCISE: implement this function.
    #
    # Fill one NTT-domain polynomial from a SHAKE128 stream by reading three
    # bytes at a time through coeff_from_three_bytes, keeping the accepted
    # values and squeezing more bytes when the buffer runs low, until 256
    # coefficients are collected.
    #
    # Reference: Chapter 12, 'Sampling: SampleInBall, ExpandA, ExpandS, ExpandMask' (FIPS 204 Algorithm 30)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_sampling.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: rej_ntt_poly")


def expand_a(params: MLDSAParams, rho: bytes) -> np.ndarray:
    """FIPS 204 Algorithm 32. The k-by-l public matrix A in the NTT domain.

    The seed for entry (r, s) appends the column index s *then* the row index r
    (both one byte): rho || IntegerToBytes(s, 1) || IntegerToBytes(r, 1).
    """
    # EXERCISE: implement this function.
    #
    # Build the k-by-l matrix A in the NTT domain. Entry (r, s) is
    # rej_ntt_poly seeded with rho || IntegerToBytes(s, 1) ||
    # IntegerToBytes(r, 1); note the column index s comes before the row
    # index r, so A[r][s] and A[s][r] differ.
    #
    # Reference: Chapter 12, 'Sampling: SampleInBall, ExpandA, ExpandS, ExpandMask' (FIPS 204 Algorithm 32)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_sampling.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: expand_a")


# --- Secret expansion (FIPS 204 Algorithms 31, 33). ---

def rej_bounded_poly(rho_prime: bytes, eta: int) -> np.ndarray:
    """FIPS 204 Algorithm 31. One polynomial with coefficients in [-eta, eta]."""
    # EXERCISE: implement this function.
    #
    # Fill one polynomial with coefficients in [-eta, eta] from a SHAKE256
    # stream. For each byte, split into its two half-bytes and pass each
    # through coeff_from_half_byte, keeping the accepted values until 256
    # coefficients are collected.
    #
    # Reference: Chapter 12, 'Sampling: SampleInBall, ExpandA, ExpandS, ExpandMask' (FIPS 204 Algorithm 31)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_sampling.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: rej_bounded_poly")


def expand_s(params: MLDSAParams, rho_prime: bytes) -> tuple[np.ndarray, np.ndarray]:
    """FIPS 204 Algorithm 33. Secret vectors s1 (l polys, nonces 0..l-1) and
    s2 (k polys, nonces l..l+k-1)."""
    # EXERCISE: implement this function.
    #
    # Draw s1 (l polynomials, nonces 0..l-1) and s2 (k polynomials, nonces
    # l..l+k-1) with rej_bounded_poly. Each polynomial's seed is rho' ||
    # IntegerToBytes(nonce, 2), and the coefficients land in [-eta, eta].
    #
    # Reference: Chapter 12, 'Sampling: SampleInBall, ExpandA, ExpandS, ExpandMask' (FIPS 204 Algorithm 33)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_sampling.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: expand_s")


# --- Mask expansion (FIPS 204 Algorithm 34). ---

def expand_mask(params: MLDSAParams, rho_dprime: bytes, kappa: int) -> np.ndarray:
    """FIPS 204 Algorithm 34. The mask y (l polys) with coeffs in (-gamma1, gamma1].

    Poly r uses seed rho'' || IntegerToBytes(kappa + r, 2) and BitUnpacks
    32*(1 + bitlen(gamma1-1)) bytes.
    """
    # EXERCISE: implement this function.
    #
    # Draw the l-polynomial mask y with coefficients in (-gamma1, gamma1].
    # Unlike the others, ExpandMask does not reject: for polynomial r,
    # squeeze 32 * gamma1_bits() bytes from SHAKE256 seeded with rho'' ||
    # IntegerToBytes(kappa + r, 2) and BitUnpack them at (gamma1 - 1,
    # gamma1).
    #
    # Reference: Chapter 12, 'Sampling: SampleInBall, ExpandA, ExpandS, ExpandMask' (FIPS 204 Algorithm 34)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_sampling.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: expand_mask")
