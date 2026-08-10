"""The full 256-point number-theoretic transform over R_q (FIPS 204 §7.5).

ML-DSA works in R_q = Z_q[X]/(X^256 + 1) with q = 8380417. Because q ≡ 1 (mod 2n),
the modulus X^256 + 1 factors into 256 distinct linear terms over Z_q, so the NTT
is a *full* transform: a polynomial becomes 256 independent scalars and the ring
product becomes coefficient-wise (pointwise) multiplication. This is simpler than
ML-KEM's partial NTT, whose ring keeps degree-1 (quadratic) factors and needs a
base-case multiply.

The zeta table is ``zetas[k] = zeta^(brv8(k)) mod q`` where ``brv8`` is the
8-bit bit-reversal and zeta = 1753 is a primitive 512-th root of unity. The
forward transform is the decimation-in-time (Cooley-Tukey) butterfly; the inverse
is the Gentleman-Sande butterfly with negated zetas, followed by a single scaling
by n^{-1} mod q.

As in ``ch11-mlkem/ntt.py``, polynomials are numpy ``int64`` arrays but each
modular butterfly drops to a Python ``int`` before the ``% Q`` so a signed
subtraction never underflows the numpy dtype.
"""

from __future__ import annotations

import numpy as np

from .params import ML_DSA_Q as Q, ML_DSA_N as N, ML_DSA_ZETA as ZETA


# n^{-1} mod q, applied once at the end of the inverse transform.
N_INV = pow(N, -1, Q)
assert N_INV == 8347681, f"N_INV must equal 8347681, got {N_INV}"


def _bit_rev_8(k: int) -> int:
    """Reverse the low 8 bits of k (0 <= k < 256)."""
    assert 0 <= k < 256, f"_bit_rev_8: k out of range: {k}"
    r = 0
    for _ in range(8):
        r = (r << 1) | (k & 1)
        k >>= 1
    return r


# zetas[k] = zeta^(brv8(k)) mod q. Entry 0 is 1 and is never consumed (the
# butterfly counter starts at 1); it is kept so indexing matches FIPS 204.
ZETAS: list[int] = [pow(ZETA, _bit_rev_8(k), Q) for k in range(256)]


def ntt(w: np.ndarray) -> np.ndarray:
    """Forward NTT (FIPS 204 Algorithm 41). Returns a new length-256 array."""
    w = np.asarray(w, dtype=np.int64)
    assert w.shape == (N,), f"ntt: expected length-{N}, got {w.shape}"
    w_hat = (w % Q).copy()
    m = 0
    length = 128
    while length >= 1:
        start = 0
        while start < N:
            m += 1
            zeta = ZETAS[m]
            for j in range(start, start + length):
                t = (zeta * int(w_hat[j + length])) % Q
                w_hat[j + length] = (int(w_hat[j]) - t) % Q
                w_hat[j] = (int(w_hat[j]) + t) % Q
            start += 2 * length
        length //= 2
    return w_hat


def ntt_inverse(w_hat: np.ndarray) -> np.ndarray:
    """Inverse NTT (FIPS 204 Algorithm 42). Returns a new length-256 array."""
    w_hat = np.asarray(w_hat, dtype=np.int64)
    assert w_hat.shape == (N,), f"ntt_inverse: expected length-{N}, got {w_hat.shape}"
    w = (w_hat % Q).copy()
    m = 256
    length = 1
    while length < N:
        start = 0
        while start < N:
            m -= 1
            zeta = (-ZETAS[m]) % Q
            for j in range(start, start + length):
                t = int(w[j])
                w[j] = (t + int(w[j + length])) % Q
                w[j + length] = (zeta * (t - int(w[j + length]))) % Q
            start += 2 * length
        length *= 2
    for j in range(N):
        w[j] = (N_INV * int(w[j])) % Q
    return w


def multiply_ntts(a_hat: np.ndarray, b_hat: np.ndarray) -> np.ndarray:
    """Pointwise product of two NTT-domain polynomials (FIPS 204 §7.5).

    The full transform makes this a plain coefficient-wise multiply mod q, unlike
    ML-KEM's base-case multiply over degree-1 quotient rings.
    """
    a_hat = np.asarray(a_hat, dtype=np.int64)
    b_hat = np.asarray(b_hat, dtype=np.int64)
    assert a_hat.shape == (N,) and b_hat.shape == (N,), "multiply_ntts: length-256 inputs"
    out = np.empty(N, dtype=np.int64)
    for i in range(N):
        out[i] = (int(a_hat[i]) * int(b_hat[i])) % Q
    return out


def schoolbook_ring_multiply(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Reference O(n^2) product in Z_q[X]/(X^256 + 1). Test cross-check only."""
    a = np.asarray(a, dtype=np.int64)
    b = np.asarray(b, dtype=np.int64)
    assert a.shape == (N,) and b.shape == (N,), "schoolbook: length-256 inputs"
    out = [0] * N
    for i in range(N):
        ai = int(a[i])
        if ai == 0:
            continue
        for j in range(N):
            k = i + j
            prod = ai * int(b[j])
            if k < N:
                out[k] = (out[k] + prod) % Q
            else:  # X^256 = -1: wrap with a sign flip
                out[k - N] = (out[k - N] - prod) % Q
    return np.array(out, dtype=np.int64)
