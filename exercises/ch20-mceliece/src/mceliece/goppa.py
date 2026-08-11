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
    # EXERCISE: implement this function.
    #
    # Draw t uniform coefficients from GF(2^m), append a leading 1 to keep
    # the polynomial monic, and return as soon as poly_is_irreducible
    # accepts. Rejecting until success is the whole algorithm; roughly one
    # in t candidates passes, so the loop is short at these sizes.
    # Irreducibility earns its keep twice: it makes every nonzero polynomial
    # invertible modulo g, which Patterson's key transform needs, and it
    # guarantees g has no root in GF(2^m), so all 2^m field elements stay
    # usable as support.
    #
    # Reference: Chapter 20, 'Goppa code construction'
    #
    # Proved by:
    #   tests/ch20/test_goppa_construction.py
    #   tests/ch20/test_generator_matrix.py
    #   tests/ch20/test_patterson.py
    raise NotImplementedError("exercise: find_irreducible_goppa_poly")


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
    # EXERCISE: implement this function.
    #
    # For each support element evaluate g and invert the result to get h_j =
    # 1/g(L_j), raising ValueError if g vanishes there, since that element
    # cannot be in the support. Build the t-by-n matrix over GF(2^m) with
    # V[i][j] = L_j^i * h_j for i from 0 to t - 1, a Vandermonde pattern
    # scaled column by column by h. Then expand each field entry into m
    # binary rows, least significant bit first inside each block, giving an
    # (m*t)-by-n binary matrix. That expansion is where the algebraic
    # structure stops being visible: the binary matrix is all an attacker
    # gets.
    #
    # Reference: Chapter 20, 'Goppa code construction'
    #
    # Proved by:
    #   tests/ch20/test_goppa_construction.py
    #   tests/ch20/test_generator_matrix.py
    raise NotImplementedError("exercise: goppa_parity_check")


def full_support(m: int) -> list[int]:
    """Return all 2^m elements of GF(2^m) as the support set."""
    return list(range(1 << m))
