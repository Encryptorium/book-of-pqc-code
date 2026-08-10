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
    b2 = b2 & 0x7F
    z = (b2 << 16) | (b1 << 8) | b0
    return z if z < Q else None


def coeff_from_half_byte(b: int, eta: int) -> int | None:
    """FIPS 204 Algorithm 15. Map a half-byte into [-eta, eta] or reject."""
    if eta == 2 and b < 15:
        return 2 - (b % 5)
    if eta == 4 and b < 9:
        return 4 - b
    return None


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
    xof = hashlib.shake_128(rho_prime)
    need = _BLOCK
    stream = xof.digest(need)
    a = np.empty(256, dtype=np.int64)
    j = 0
    pos = 0
    while j < 256:
        if pos + 3 > len(stream):
            need += _BLOCK
            stream = xof.digest(need)
        coeff = coeff_from_three_bytes(stream[pos], stream[pos + 1], stream[pos + 2])
        pos += 3
        if coeff is not None:
            a[j] = coeff
            j += 1
    return a


def expand_a(params: MLDSAParams, rho: bytes) -> np.ndarray:
    """FIPS 204 Algorithm 32. The k-by-l public matrix A in the NTT domain.

    The seed for entry (r, s) appends the column index s *then* the row index r
    (both one byte): rho || IntegerToBytes(s, 1) || IntegerToBytes(r, 1).
    """
    assert len(rho) == 32, f"expand_a: rho must be 32 bytes, got {len(rho)}"
    A = np.empty((params.k, params.l, 256), dtype=np.int64)
    for r in range(params.k):
        for s in range(params.l):
            rho_prime = rho + integer_to_bytes(s, 1) + integer_to_bytes(r, 1)
            A[r][s] = rej_ntt_poly(rho_prime)
    return A


# --- Secret expansion (FIPS 204 Algorithms 31, 33). ---

def rej_bounded_poly(rho_prime: bytes, eta: int) -> np.ndarray:
    """FIPS 204 Algorithm 31. One polynomial with coefficients in [-eta, eta]."""
    xof = hashlib.shake_256(rho_prime)
    need = _BLOCK
    stream = xof.digest(need)
    a = np.empty(256, dtype=np.int64)
    j = 0
    pos = 0
    while j < 256:
        if pos >= len(stream):
            need += _BLOCK
            stream = xof.digest(need)
        z = stream[pos]
        pos += 1
        z0 = coeff_from_half_byte(z % 16, eta)
        z1 = coeff_from_half_byte(z // 16, eta)
        if z0 is not None:
            a[j] = z0
            j += 1
        if z1 is not None and j < 256:
            a[j] = z1
            j += 1
    return a


def expand_s(params: MLDSAParams, rho_prime: bytes) -> tuple[np.ndarray, np.ndarray]:
    """FIPS 204 Algorithm 33. Secret vectors s1 (l polys, nonces 0..l-1) and
    s2 (k polys, nonces l..l+k-1)."""
    assert len(rho_prime) == 64, f"expand_s: rho' must be 64 bytes, got {len(rho_prime)}"
    eta = params.eta
    s1 = np.empty((params.l, 256), dtype=np.int64)
    for i in range(params.l):
        s1[i] = rej_bounded_poly(rho_prime + integer_to_bytes(i, 2), eta)
    s2 = np.empty((params.k, 256), dtype=np.int64)
    for i in range(params.k):
        s2[i] = rej_bounded_poly(rho_prime + integer_to_bytes(i + params.l, 2), eta)
    return s1, s2


# --- Mask expansion (FIPS 204 Algorithm 34). ---

def expand_mask(params: MLDSAParams, rho_dprime: bytes, kappa: int) -> np.ndarray:
    """FIPS 204 Algorithm 34. The mask y (l polys) with coeffs in (-gamma1, gamma1].

    Poly r uses seed rho'' || IntegerToBytes(kappa + r, 2) and BitUnpacks
    32*(1 + bitlen(gamma1-1)) bytes.
    """
    assert len(rho_dprime) == 64, f"expand_mask: rho'' must be 64 bytes, got {len(rho_dprime)}"
    g1 = params.gamma_1
    c = params.gamma1_bits()  # 1 + bitlen(gamma1 - 1)
    y = np.empty((params.l, 256), dtype=np.int64)
    for r in range(params.l):
        seed = rho_dprime + integer_to_bytes(kappa + r, 2)
        v = hashlib.shake_256(seed).digest(32 * c)
        y[r] = bit_unpack(v, g1 - 1, g1)
    return y
