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
    if p % 4 != 3:
        raise ValueError(f"standard maximal order requires p = 3 mod 4, got p = {p}")
    e0 = quat_one()
    e1 = quat_i()
    e2 = quat(0, Fraction(1, 2), Fraction(1, 2), 0)        # (i + j) / 2
    e3 = quat(Fraction(1, 2), 0, 0, Fraction(1, 2))        # (1 + k) / 2
    return [e0, e1, e2, e3]


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
    if not in_standard_order(x, p):
        raise ValueError(f"element {x} is not in the standard maximal order")
    a, b, c, d = x
    u0 = a - d
    u1 = b - c
    u2 = 2 * c
    u3 = 2 * d
    return (int(u0), int(u1), int(u2), int(u3))


def left_ideal_basis(generator: Quat, p: int) -> list[Quat]:
    """Compute a Z-basis for the left O_0-ideal O_0 * alpha.

    Multiplies each basis element of O_0 by alpha on the right:
        O_0 * alpha = {beta * alpha : beta in O_0}
    The four products form a Z-basis for the principal left ideal.
    """
    basis = standard_basis(p)
    return [quat_mul(b, generator, p) for b in basis]


def ideal_norm_principal(generator: Quat, p: int) -> Fraction:
    """For a principal left ideal I = O_0 * alpha, nrd(I) = nrd(alpha).

    The reduced norm of a principal ideal equals the reduced norm of
    any of its generators (Voight 2021, paragraph 16.3.5).
    """
    return quat_norm(generator, p)


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
