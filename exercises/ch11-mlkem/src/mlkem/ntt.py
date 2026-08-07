"""The specialized partial NTT for $R_{3329}$ (FIPS 203 §4.3, Appendix A).

ML-KEM works over the ring $R_q = \\mathbb{Z}_{3329}[x]/(x^{256}+1)$
with $q = 3329$, a prime satisfying $256 | q - 1$ but **not**
$512 | q - 1$. Consequently $\\mathbb{Z}_q$ contains a primitive
$256$-th root of unity but not a primitive $512$-th root. FIPS 203
fixes $\\zeta = 17$ as the primitive $256$-th root of unity and uses
the factorization

.. math::

    x^{256} + 1 = \\prod_{i=0}^{127}
        \\bigl(x^2 - \\zeta^{2 \\cdot \\text{BitRev}_7(i) + 1}\\bigr)
        \\pmod{q}

to split $R_q$ into 128 quadratic extensions. The NTT is the
isomorphism $R_q \\to \\prod_{i=0}^{127} \\mathbb{Z}_q[X]/(X^2 - \\gamma_i)$
given by simultaneous reduction modulo each factor, where
$\\gamma_i = \\zeta^{2 \\cdot \\text{BitRev}_7(i) + 1}$.

The forward NTT (Algorithm 9) is the iterative Cooley-Tukey form with
bit-reversed twiddle factors. The inverse (Algorithm 10) runs the
Gentleman-Sande butterflies backwards and scales by $128^{-1} = 3303$
mod $q$. Multiplication in the NTT domain (Algorithm 11) is **not**
pointwise: each pair of coefficients represents a degree-1 polynomial
in a different $\\mathbb{Z}_q[X]/(X^2 - \\gamma_i)$ slot, and the base
case (Algorithm 12) multiplies two degree-1 polynomials modulo the
relevant $(X^2 - \\gamma)$ in the straightforward way.

Implementation style: pedagogical integer arithmetic over numpy int64
arrays, no Montgomery form, no Barrett reduction, no SIMD. The
butterflies match FIPS 203's variable names literally. Correctness
checks against an independent $O(n^2)$ schoolbook multiplication live
in the test suite.
"""

from __future__ import annotations

import numpy as np


# The primitive 256-th root of unity in Z_3329 fixed by FIPS 203.
Q = 3329
N = 256
ZETA = 17
# The inverse of 128 mod q, used to scale the output of InverseNTT.
# pow(128, -1, 3329) == 3303 in Python 3.10+, so this is not guessed.
INV_128 = pow(128, -1, Q)
assert INV_128 == 3303, f"INV_128 must equal 3303, got {INV_128}"


def _bit_rev_7(i: int) -> int:
    """Return the 7-bit bit-reversal of ``i`` (0 <= i < 128).

    FIPS 203 names this function BitRev_7. The output is the integer
    whose 7-bit binary representation is the reverse of ``i``'s 7-bit
    binary representation. Used to index the zeta table so the NTT
    butterflies sweep the DFT in decimation-in-time order.
    """
    assert 0 <= i < 128, f"_bit_rev_7: i must be in [0, 128), got {i}"
    out = 0
    for _ in range(7):
        out = (out << 1) | (i & 1)
        i >>= 1
    return out


# The zeta tables indexed 0 .. 127 (Algorithms 9 and 10 use entries
# 1 .. 127; entry 0 is unused but kept for index alignment).
ZETAS_NTT: list[int] = [pow(ZETA, _bit_rev_7(k), Q) for k in range(128)]

# The gamma values used inside MultiplyNTTs and BaseCaseMultiply.
# These are ζ^(2 * BitRev_7(i) + 1) for i = 0, 1, ..., 127.
ZETAS_MUL: list[int] = [
    pow(ZETA, 2 * _bit_rev_7(k) + 1, Q) for k in range(128)
]


def ntt(f: np.ndarray) -> np.ndarray:
    """Compute the NTT of a polynomial in $R_q$ (FIPS 203 Algorithm 9).

    Accepts a length-256 int64 array ``f`` of coefficients reduced
    modulo $q$ and returns a length-256 int64 array ``f_hat`` in the
    NTT domain. The forward NTT is performed in place on a copy; the
    input is not mutated.
    """
    f = np.asarray(f, dtype=np.int64).copy() % Q
    assert f.shape == (N,), f"ntt: expected length-{N}, got {f.shape}"
    f_hat = f.copy()
    i = 1
    length = 128
    while length >= 2:
        start = 0
        while start < N:
            zeta = ZETAS_NTT[i]
            i += 1
            for j in range(start, start + length):
                t = (zeta * int(f_hat[j + length])) % Q
                f_hat[j + length] = (int(f_hat[j]) - t) % Q
                f_hat[j] = (int(f_hat[j]) + t) % Q
            start += 2 * length
        length //= 2
    return f_hat


def inverse_ntt(f_hat: np.ndarray) -> np.ndarray:
    """Compute the inverse NTT (FIPS 203 Algorithm 10).

    Accepts a length-256 int64 array in the NTT domain and returns the
    corresponding length-256 int64 array of coefficients in $R_q$. The
    inverse runs the Gentleman-Sande butterflies in decreasing length
    order and scales by $128^{-1} = 3303$ mod $q$ at the end.
    """
    f_hat = np.asarray(f_hat, dtype=np.int64).copy() % Q
    assert f_hat.shape == (N,), (
        f"inverse_ntt: expected length-{N}, got {f_hat.shape}"
    )
    f = f_hat.copy()
    i = 127
    length = 2
    while length <= 128:
        start = 0
        while start < N:
            zeta = ZETAS_NTT[i]
            i -= 1
            for j in range(start, start + length):
                t = int(f[j])
                f[j] = (t + int(f[j + length])) % Q
                f[j + length] = (zeta * (int(f[j + length]) - t)) % Q
            start += 2 * length
        length *= 2
    return (f * INV_128) % Q


def _base_case_multiply(
    a0: int, a1: int, b0: int, b1: int, gamma: int
) -> tuple[int, int]:
    """Multiply two degree-1 polynomials modulo $X^2 - \\gamma$.

    FIPS 203 Algorithm 12. Computes
    $(a_0 + a_1 X)(b_0 + b_1 X) \\bmod (X^2 - \\gamma)$ as

    .. math::

        c_0 = a_0 b_0 + a_1 b_1 \\gamma, \\quad
        c_1 = a_0 b_1 + a_1 b_0,

    all reductions mod $q$.
    """
    # EXERCISE: implement this function.
    #
    # Multiply the degree-1 polynomials (a0 + a1 X) and (b0 + b1 X) modulo
    # X^2 - gamma. The X^2 term folds back down as gamma, so c0 = a0 * b0 +
    # a1 * b1 * gamma and c1 = a0 * b1 + a1 * b0, both reduced modulo q.
    # Return the pair (c0, c1).
    #
    # Reference: Chapter 11, 'The specialized partial NTT at (256, 3329)' (FIPS 203 Algorithm 12)
    #
    # Proved by:
    #   tests/ch11/test_mlkem_ntt.py
    raise NotImplementedError("exercise: _base_case_multiply")


def multiply_ntts(f_hat: np.ndarray, g_hat: np.ndarray) -> np.ndarray:
    """Multiply two polynomials in the NTT domain (FIPS 203 Algorithm 11).

    Each pair of coefficients $(f_\\text{hat}[2i], f_\\text{hat}[2i+1])$
    represents a degree-1 polynomial in
    $\\mathbb{Z}_q[X]/(X^2 - \\gamma_i)$ where
    $\\gamma_i = \\zeta^{2 \\cdot \\text{BitRev}_7(i) + 1}$. Multiplication
    is not pointwise; each of the 128 slots runs ``BaseCaseMultiply``.
    """
    f_hat = np.asarray(f_hat, dtype=np.int64) % Q
    g_hat = np.asarray(g_hat, dtype=np.int64) % Q
    assert f_hat.shape == (N,), (
        f"multiply_ntts: f_hat shape {f_hat.shape} not ({N},)"
    )
    assert g_hat.shape == (N,), (
        f"multiply_ntts: g_hat shape {g_hat.shape} not ({N},)"
    )
    h_hat = np.zeros(N, dtype=np.int64)
    for i in range(128):
        gamma = ZETAS_MUL[i]
        c0, c1 = _base_case_multiply(
            int(f_hat[2 * i]),
            int(f_hat[2 * i + 1]),
            int(g_hat[2 * i]),
            int(g_hat[2 * i + 1]),
            gamma,
        )
        h_hat[2 * i] = c0
        h_hat[2 * i + 1] = c1
    return h_hat


def schoolbook_ring_multiply(f: np.ndarray, g: np.ndarray) -> np.ndarray:
    """Independent $O(n^2)$ reference multiplication in $R_q$.

    Exists only to cross-check the NTT pipeline. Computes
    $h = f \\cdot g \\bmod (x^{256}+1)$ by direct convolution, applying
    the negacyclic wrap $x^{256} = -1$ to degrees $256 \\leq k < 512$.
    Used by the test suite to verify
    ``inverse_ntt(multiply_ntts(ntt(f), ntt(g))) == schoolbook_ring_multiply(f, g)``.
    """
    f = np.asarray(f, dtype=np.int64) % Q
    g = np.asarray(g, dtype=np.int64) % Q
    assert f.shape == (N,) and g.shape == (N,)
    h = np.zeros(N, dtype=np.int64)
    for i in range(N):
        fi = int(f[i])
        if fi == 0:
            continue
        for j in range(N):
            k = i + j
            term = (fi * int(g[j])) % Q
            if k < N:
                h[k] = (int(h[k]) + term) % Q
            else:
                h[k - N] = (int(h[k - N]) - term) % Q
    return h
