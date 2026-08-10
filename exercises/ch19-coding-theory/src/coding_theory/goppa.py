"""Binary Goppa code basics.

A binary Goppa code Gamma(L, g) over GF(2) is defined by:
  - an irreducible polynomial g(x) of degree t over GF(2^m)
  - a support set L = {alpha_0, ..., alpha_{n-1}} of n distinct elements of GF(2^m)

The code has parameters [n, >= n - m*t, >= 2t + 1] and can correct up to t errors.
Patterson's algorithm decodes in polynomial time given g(x).  Without g(x),
the parity-check matrix looks random, and decoding falls back to syndrome
decoding (NP-hard in general).

This module provides a minimal structural example for a tiny Goppa code
(m=3, t=1 over GF(2^3)).  The full construction is Chapter 20's job.
"""


def _gf8_mul(a: int, b: int) -> int:
    """Multiply two elements of GF(2^3) = GF(2)[x]/(x^3 + x + 1).

    Elements are integers 0..7 representing polynomials of degree <= 2.
    The irreducible polynomial is x^3 + x + 1 (binary 0b1011 = 11).
    """
    p = 0
    for _ in range(3):
        if b & 1:
            p ^= a
        b >>= 1
        a <<= 1
        if a & 0b1000:
            a ^= 0b1011  # reduce mod x^3 + x + 1
    return p


def _gf8_inv(a: int) -> int:
    """Multiplicative inverse in GF(2^3).  Brute force for 7 nonzero elements."""
    for x in range(1, 8):
        if _gf8_mul(a, x) == 1:
            return x
    raise ValueError(f"no inverse for {a} in GF(8)")


def goppa_parity_check_gf8(g_root: int, support: list[int]) -> list[list[int]]:
    """Construct the binary parity-check matrix for a t=1 Goppa code over GF(2^3).

    For t=1, g(x) = x - g_root (degree 1, so g has a single root in GF(2^3)).
    The GF(2^3) parity-check row is H_gf8[j] = 1 / (support[j] - g_root)
    where subtraction is XOR in GF(2^m).

    The binary parity-check matrix is obtained by expanding each GF(2^3)
    element into its 3-bit column vector, giving a 3-by-n binary matrix
    (m*t = 3*1 = 3 rows).

    Parameters
    ----------
    g_root : int
        The root of g(x) in GF(2^3).  Must be in 1..7 and must not appear
        in the support set.
    support : list[int]
        The support set L, a list of distinct GF(2^3) elements (each 0..7)
        that do not include g_root.

    Returns
    -------
    list[list[int]]
        A 3-by-n binary parity-check matrix.
    """
    # EXERCISE: implement this function.
    #
    # For t = 1 the polynomial is g(x) = x - g_root, so the GF(2^3)
    # parity-check row is h_j = 1 / (support[j] - g_root), and subtraction
    # in characteristic 2 is XOR: invert support[j] ^ g_root. Then expand
    # each field element into a binary column of m = 3 bits, most
    # significant bit in row 0: H[2 - bit][j] = (val >> bit) & 1. The result
    # is 3-by-n, since m * t = 3. Every column is nonzero because an inverse
    # never is, and the matrix shows no visible trace of g_root or the
    # support, which is the shape of the trapdoor even though a code this
    # small hides nothing.
    #
    # Reference: Chapter 19, 'Goppa codes'
    #
    # Proved by:
    #   tests/ch19/test_goppa_parity.py
    raise NotImplementedError("exercise: goppa_parity_check_gf8")
