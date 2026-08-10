"""Rounding and hint algebra (FIPS 204 §7.4, Algorithms 35-40).

ML-DSA drops the low ``d`` bits of the public key (Power2Round) and works with the
high bits of the commitment ``w`` (Decompose/HighBits/LowBits). The signer cannot
transmit the exact carry those dropped bits induce, so it sends a one-bit *hint*
per coefficient (MakeHint) that lets the verifier recover the correct high bits
(UseHint). The governing identity is

    UseHint(MakeHint(z, r), r) = HighBits(r + z)   for  ||z||_inf <= gamma2,

which is why the hint is only ever a single bit: within that bound, adding ``z``
can nudge the high part by at most +-1.

All six operations are defined coefficient-wise on integers in [0, q). Each has a
scalar core and a numpy ``*_poly`` wrapper that applies it across a length-256
polynomial; the wrappers are plain elementwise loops (pedagogical clarity over
vectorized cleverness, matching the ch11 idiom).
"""

from __future__ import annotations

import numpy as np

from .params import ML_DSA_Q as Q, ML_DSA_D as D, ML_DSA_N as N


def mod_pm(r: int, alpha: int) -> int:
    """Centered modular reduction ``r mod± alpha``.

    Returns the representative m ≡ r (mod alpha) with -alpha/2 < m <= alpha/2
    (for even alpha, as used throughout ML-DSA).
    """
    m = r % alpha
    if m > alpha // 2:
        m -= alpha
    return m


def power2round(r: int) -> tuple[int, int]:
    """FIPS 204 Algorithm 35. Split r into (r1, r0) with r = r1*2^d + r0 and
    r0 = r mod± 2^d in (-2^(d-1), 2^(d-1)]."""
    r = r % Q
    r0 = mod_pm(r, 1 << D)
    r1 = (r - r0) >> D
    return r1, r0


def decompose(r: int, gamma2: int) -> tuple[int, int]:
    """FIPS 204 Algorithm 36. Split r into high/low parts around the 2*gamma2
    window, with the boundary case that keeps r1 in [0, (q-1)/(2*gamma2) - 1]."""
    r = r % Q
    r0 = mod_pm(r, 2 * gamma2)
    if r - r0 == Q - 1:
        r1 = 0
        r0 = r0 - 1
    else:
        r1 = (r - r0) // (2 * gamma2)
    return r1, r0


def high_bits(r: int, gamma2: int) -> int:
    """FIPS 204 Algorithm 37."""
    return decompose(r, gamma2)[0]


def low_bits(r: int, gamma2: int) -> int:
    """FIPS 204 Algorithm 38."""
    # EXERCISE: implement this function.
    #
    # The low part of Decompose: return decompose(r, gamma2)[1]. Sign
    # rejects an attempt when this part, on w - c*s2, gets too close to a
    # boundary.
    #
    # Reference: Chapter 12, 'Power2Round, Decompose, and the hint' (FIPS 204 Algorithm 38)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_rounding.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: low_bits")


def make_hint(z: int, r: int, gamma2: int) -> int:
    """FIPS 204 Algorithm 39. Returns 1 iff adding z changes the high bits of r."""
    r1 = high_bits(r, gamma2)
    v1 = high_bits((r + z) % Q, gamma2)
    return 1 if r1 != v1 else 0


def use_hint(h: int, r: int, gamma2: int) -> int:
    """FIPS 204 Algorithm 40. Adjust HighBits(r) by +-1 when the hint fires."""
    m = (Q - 1) // (2 * gamma2)
    r1, r0 = decompose(r, gamma2)
    if h == 1:
        if r0 > 0:
            return (r1 + 1) % m
        return (r1 - 1) % m
    return r1


# --- Polynomial (length-256) wrappers. ---

def power2round_poly(poly: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    poly = np.asarray(poly, dtype=np.int64)
    assert poly.shape == (N,), f"power2round_poly: expected length-{N}"
    r1 = np.empty(N, dtype=np.int64)
    r0 = np.empty(N, dtype=np.int64)
    for i in range(N):
        a, b = power2round(int(poly[i]))
        r1[i], r0[i] = a, b
    return r1, r0


def decompose_poly(poly: np.ndarray, gamma2: int) -> tuple[np.ndarray, np.ndarray]:
    poly = np.asarray(poly, dtype=np.int64)
    assert poly.shape == (N,), f"decompose_poly: expected length-{N}"
    r1 = np.empty(N, dtype=np.int64)
    r0 = np.empty(N, dtype=np.int64)
    for i in range(N):
        a, b = decompose(int(poly[i]), gamma2)
        r1[i], r0[i] = a, b
    return r1, r0


def high_bits_poly(poly: np.ndarray, gamma2: int) -> np.ndarray:
    return decompose_poly(poly, gamma2)[0]


def low_bits_poly(poly: np.ndarray, gamma2: int) -> np.ndarray:
    return decompose_poly(poly, gamma2)[1]


def make_hint_poly(z_poly: np.ndarray, r_poly: np.ndarray, gamma2: int) -> np.ndarray:
    z_poly = np.asarray(z_poly, dtype=np.int64)
    r_poly = np.asarray(r_poly, dtype=np.int64)
    assert z_poly.shape == (N,) and r_poly.shape == (N,), "make_hint_poly: length-256 inputs"
    h = np.empty(N, dtype=np.int64)
    for i in range(N):
        h[i] = make_hint(int(z_poly[i]), int(r_poly[i]), gamma2)
    return h


def use_hint_poly(h_poly: np.ndarray, r_poly: np.ndarray, gamma2: int) -> np.ndarray:
    h_poly = np.asarray(h_poly, dtype=np.int64)
    r_poly = np.asarray(r_poly, dtype=np.int64)
    assert h_poly.shape == (N,) and r_poly.shape == (N,), "use_hint_poly: length-256 inputs"
    out = np.empty(N, dtype=np.int64)
    for i in range(N):
        out[i] = use_hint(int(h_poly[i]), int(r_poly[i]), gamma2)
    return out
