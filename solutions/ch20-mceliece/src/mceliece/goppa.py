"""Generalized binary Goppa code construction over GF(2^m).

Given an irreducible Goppa polynomial g(x) of degree t over GF(2^m) and
a support set L of n distinct elements of GF(2^m) (none of which are
roots of g), this module constructs the binary parity-check matrix H
and derives the generator matrix G in systematic form.
"""

from mceliece.gf2m import (
    gf2m_mul, gf2m_inv, poly_eval, poly_is_irreducible, gf2m_add,
)


def find_irreducible_goppa_poly(
    m: int, irred: int, t: int, rng
) -> list[int]:
    """Find a random irreducible polynomial of degree t over GF(2^m).

    Returns coefficients [c0, c1, ..., ct] with ct != 0.
    """
    q = 1 << m
    while True:
        coeffs = [rng.randint(0, q - 1) for _ in range(t)] + [1]  # monic
        if poly_is_irreducible(coeffs, m, irred):
            return coeffs


def goppa_parity_check(
    m: int, irred: int, g_coeffs: list[int], support: list[int]
) -> list[list[int]]:
    """Build the binary (m*t)-by-n parity-check matrix H.

    For each support element L_j, compute h_j = 1/g(L_j) in GF(2^m),
    then construct the t-by-n matrix over GF(2^m):

        V[i][j] = L_j^i * h_j,   i = 0..t-1

    Finally, expand each GF(2^m) entry into m binary rows, giving
    the (m*t)-by-n binary parity-check matrix.
    """
    t = len(g_coeffs) - 1
    n = len(support)

    # evaluate g at each support point and invert
    h = []
    for lj in support:
        gval = poly_eval(g_coeffs, lj, m, irred)
        if gval == 0:
            raise ValueError(f"support element {lj} is a root of g(x)")
        h.append(gf2m_inv(gval, m, irred))

    # build t-by-n matrix over GF(2^m)
    V = []
    for i in range(t):
        row = []
        for j in range(n):
            # L_j^i * h_j
            lj_pow = 1
            for _ in range(i):
                lj_pow = gf2m_mul(lj_pow, support[j], m, irred)
            row.append(gf2m_mul(lj_pow, h[j], m, irred))
        V.append(row)

    # expand to binary: each GF(2^m) entry becomes m binary rows
    H_bin = []
    for row in V:
        for bit in range(m):
            H_bin.append([(entry >> bit) & 1 for entry in row])

    return H_bin


def full_support(m: int) -> list[int]:
    """Return all 2^m elements of GF(2^m) as the support set."""
    return list(range(1 << m))
