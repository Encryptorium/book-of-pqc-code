"""Maximal orders and left ideals in B_{p,inf}.

For p prime with p = 3 mod 4, the standard maximal order in
B_{p,inf} = (-1, -p / Q) is the one the SQIsign specification uses:

    O_0 = Z + Z*i + Z*(i+j)/2 + Z*(1+k)/2

It contains the suborder Z<1, i, j, k> with index 4 and has reduced
discriminant p (matching the discriminant of B_{p,inf}).  Under
iota -> i, pi -> j for E_0: y^2 = x^3 + x it is End(E_0): the two
half-integer generators are (iota + pi)/2 and (1 + iota*pi)/2, which
are endomorphisms because iota + pi and 1 + iota*pi kill E_0[2].  The
conjugate order Z<1, i, (1+j)/2, (i+k)/2> is also maximal, but (1+pi)/2
is not an endomorphism of this curve model: (1+pi) sends (i, 0) to
(0, 0).

A left O_0-ideal is a Z-lattice of rank 4 in B_{p,inf} that is closed
under left multiplication by O_0.  We represent ideals by an explicit
Z-basis (a list of four quaternions).

Reference: Voight, "Quaternion Algebras", Springer GTM, 2021.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence

from sqisign.quaternion import (
    Quat,
    quat,
    quat_mul,
    quat_norm,
    quat_one,
    quat_i,
    quat_j,
    quat_k,
    quat_add,
    quat_scalar,
)


def standard_basis(p: int) -> list[Quat]:
    """Return the Z-basis of the standard maximal order O_0 for p = 3 mod 4.

    O_0 = Z + Z*i + Z*(i+j)/2 + Z*(1+k)/2
    """
    # EXERCISE: implement this function.
    #
    # Return the four generators of O_0 = Z + Z*i + Z*(i+j)/2 + Z*(1+k)/2 in
    # that order: 1, i, the quaternion with coefficients (0, 1/2, 1/2, 0),
    # and the one with (1/2, 0, 0, 1/2). Reject p not congruent to 3 mod 4
    # with ValueError, because closure under multiplication needs 4 to
    # divide p + 1; at p = 431 that quotient is 108. The two half-integer
    # generators are what make this order maximal rather than the obvious
    # Z<1, i, j, k>, which sits inside it at index 4, and they are the ones
    # that are endomorphisms of E_0 under iota -> i, pi -> j: iota + pi and
    # 1 + iota*pi kill the 2-torsion, while 1 + pi does not.
    #
    # Reference: Chapter 23, 'The maximal order O_0'
    #
    # Proved by:
    #   tests/ch23/test_maximal_orders.py
    #   tests/ch23/test_deuring_correspondence.py
    raise NotImplementedError("exercise: standard_basis")


def in_standard_order(x: Quat, p: int) -> bool:
    """Test whether x = a + bi + cj + dk lies in O_0.

    x is in O_0 = Z + Zi + Z(i+j)/2 + Z(1+k)/2 iff the coordinates
    (u_0, u_1, u_2, u_3) in the O_0 basis are all integers, where:
        u_0 = a - d,  u_1 = b - c,  u_2 = 2c,  u_3 = 2d.
    """
    if p % 4 != 3:
        raise ValueError(f"requires p = 3 mod 4, got p = {p}")
    a, b, c, d = x
    u0 = a - d
    u1 = b - c
    u2 = 2 * c
    u3 = 2 * d
    return all(u.denominator == 1 for u in (u0, u1, u2, u3))


def order_coords(x: Quat, p: int) -> tuple[int, int, int, int]:
    """Return the integer coordinates of x in the O_0 basis.

    Raises ValueError if x is not in O_0.
    """
    # EXERCISE: implement this function.
    #
    # Return the same four values in_standard_order tests, (a - d, b - c,
    # 2c, 2d), converted to Python ints, having first raised ValueError when
    # the element is not in O_0. Reconstructing the element as the integer
    # combination of the basis returned by standard_basis, in the same
    # order, must give back the original, which is the round trip the test
    # checks. Chapter 23 Exercise 2 asks for these coordinates by hand for
    # four sample elements.
    #
    # Reference: Chapter 23, 'The maximal order O_0'
    #
    # Proved by:
    #   tests/ch23/test_maximal_orders.py
    raise NotImplementedError("exercise: order_coords")


def left_ideal_basis(generator: Quat, p: int) -> list[Quat]:
    """Compute a Z-basis for the left O_0-ideal O_0 * alpha.

    Multiplies each basis element of O_0 by alpha on the right:
        O_0 * alpha = {beta * alpha : beta in O_0}
    The four products form a Z-basis for the principal left ideal.
    """
    # EXERCISE: implement this function.
    #
    # The principal left ideal O_0 * alpha is the set of products beta *
    # alpha for beta in O_0, so multiplying each of the four O_0 basis
    # elements by alpha on the right gives a Z-basis for it. Note the side:
    # alpha goes on the right of every product, because the ideal is closed
    # under multiplication by O_0 from the left and B_{p,inf} is not
    # commutative. Under the Deuring correspondence these ideals are what
    # stand in for isogenies out of E_0.
    #
    # Reference: Chapter 23, 'Maximal orders'
    #
    # Proved by:
    #   tests/ch23/test_maximal_orders.py
    raise NotImplementedError("exercise: left_ideal_basis")


def ideal_norm_principal(generator: Quat, p: int) -> Fraction:
    """For a principal left ideal I = O_0 * alpha, nrd(I) = nrd(alpha).

    The reduced norm of a principal ideal equals the reduced norm of
    any of its generators (Voight 2021, paragraph 16.3.5).
    """
    # EXERCISE: implement this function.
    #
    # For a principal left ideal the reduced norm of the ideal is the
    # reduced norm of any generator, so return quat_norm of the generator.
    # This is the quantity round-1 SQIsign asked KLPT to hit: an equivalent
    # ideal whose norm is a prescribed smooth number, which corresponds to
    # an isogeny of that degree. Round 2 bounds the norm instead of
    # prescribing it.
    #
    # Reference: Chapter 23, 'Maximal orders'
    #
    # Proved by:
    #   tests/ch23/test_maximal_orders.py
    raise NotImplementedError("exercise: ideal_norm_principal")


def is_in_lattice(x: Quat, basis: Sequence[Quat]) -> bool:
    """Test whether x lies in the Z-span of basis (rank-4 lattice).

    Solves the linear system M * v = x where M is the 4x4 matrix whose
    columns are the basis quaternions and v is the coordinate vector.
    Uses Fraction arithmetic to detect non-integer solutions.
    """
    # Build the 4x4 matrix M (columns are basis quaternions).
    M = [[basis[j][i] for j in range(4)] for i in range(4)]
    rhs = list(x)
    v = _solve_4x4(M, rhs)
    if v is None:
        return False
    return all(c.denominator == 1 for c in v)


def _solve_4x4(M: list[list[Fraction]], rhs: list[Fraction]) -> list[Fraction] | None:
    """Solve a 4x4 linear system using Gaussian elimination with Fractions.

    Returns None if the system is singular, else the solution vector.
    """
    n = 4
    # Augmented matrix.
    aug = [list(M[i]) + [rhs[i]] for i in range(n)]

    for col in range(n):
        # Find pivot.
        pivot = None
        for row in range(col, n):
            if aug[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]

        # Normalize pivot row.
        piv_val = aug[col][col]
        for j in range(col, n + 1):
            aug[col][j] = aug[col][j] / piv_val

        # Eliminate.
        for row in range(n):
            if row != col and aug[row][col] != 0:
                factor = aug[row][col]
                for j in range(col, n + 1):
                    aug[row][j] -= factor * aug[col][j]

    return [aug[i][n] for i in range(n)]
