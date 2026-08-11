"""The Deuring correspondence at p = 431 for E_0: y^2 = x^3 + x.

Deuring's theorem (1941) establishes a bijection between:
  - supersingular j-invariants over F_{p^2}, and
  - conjugacy classes of maximal orders in B_{p,inf}.

The correspondence is constructive at the level of endomorphism rings:
for any supersingular curve E, End(E) is a maximal order in B_{p,inf}.
For the special curve E_0: y^2 = x^3 + x at p = 3 mod 4, End(E_0) has
an explicit description in terms of four endomorphisms.

The four endomorphisms of E_0 over F_{p^2} are:

  id:     (x, y) -> (x, y)
  iota:   (x, y) -> (-x, i*y)         (CM by Z[i], requires i in F_{p^2})
  pi:     (x, y) -> (x^p, y^p)        (p-power Frobenius)
  iota*pi:(x, y) -> (-x^p, i*y^p)

These satisfy:
  iota^2 = [-1]              (verifiable on F_{p^2} points)
  iota*pi = -pi*iota         (verifiable on F_{p^2} points)
  pi^2 = [-p]                (algebraic; characteristic polynomial of
                              Frobenius for a supersingular curve with
                              trace 0 is x^2 + p; see Silverman 2009,
                              Theorem V.2.3.1)

Under the map iota -> i, pi -> j, iota*pi -> k, End(E_0) tensor Q is
isomorphic to B_{p,inf}.  The lattice Z<1, iota, (1+pi)/2, (iota+iota*pi)/2>
maps to O_0 = Z + Z*i + Z*(1+j)/2 + Z*(i+k)/2, the standard maximal
order for p = 3 mod 4.

References:
  Deuring 1941. Die Typen der Multiplikatorenringe elliptischer
    Funktionenkoerper.
  Silverman 2009. The Arithmetic of Elliptic Curves, 2nd ed.
  Voight 2021. Quaternion Algebras.
"""

from __future__ import annotations

from sqisign.fp2 import (
    fp2_mul,
    fp2_neg,
    fp2_pow,
    fp2_eq,
)
from sqisign.curve import Fp2, Point, scalar_mul, point_neg


# E_0: y^2 = x^3 + x over F_{p^2}.  In F_{p^2} = F_p[i]/(i^2+1), the
# element i is represented as (0, 1).
A0: Fp2 = (1, 0)
B0: Fp2 = (0, 0)


def endo_id(P: Point) -> Point:
    """The identity endomorphism."""
    return P


def endo_iota(P: Point, p: int) -> Point:
    """The CM endomorphism iota: (x, y) -> (-x, i*y).

    This is well-defined on E_0: y^2 = x^3 + x because (-x)^3 + (-x) =
    -(x^3 + x) = -y^2 = (i*y)^2 since i^2 = -1.
    """
    if P is None:
        return None
    x, y = P
    new_x = fp2_neg(x, p)
    new_y = fp2_mul((0, 1), y, p)
    return (new_x, new_y)


def endo_pi(P: Point, p: int) -> Point:
    """The p-power Frobenius endomorphism: (x, y) -> (x^p, y^p).

    For E_0 at p = 3 mod 4, all coefficients lie in F_p, so Frobenius
    is an endomorphism.
    """
    if P is None:
        return None
    x, y = P
    return (fp2_pow(x, p, p), fp2_pow(y, p, p))


def endo_iota_pi(P: Point, p: int) -> Point:
    """The composition iota . pi: (x, y) -> (-x^p, i*y^p)."""
    return endo_iota(endo_pi(P, p), p)


def verify_iota_squared_is_neg_one(P: Point, p: int) -> bool:
    """Verify iota^2 (P) = -P for a single point.

    This is the relation iota^2 = [-1] in End(E_0).
    """
    lhs = endo_iota(endo_iota(P, p), p)
    rhs = point_neg(P, p)
    if lhs is None and rhs is None:
        return True
    if lhs is None or rhs is None:
        return False
    return fp2_eq(lhs[0], rhs[0], p) and fp2_eq(lhs[1], rhs[1], p)


def verify_iota_pi_anticommutes(P: Point, p: int) -> bool:
    """Verify (iota . pi)(P) = -(pi . iota)(P) for a single point.

    This is the relation iota*pi = -pi*iota in End(E_0).
    """
    lhs = endo_iota(endo_pi(P, p), p)
    pi_iota = endo_pi(endo_iota(P, p), p)
    rhs = point_neg(pi_iota, p)
    if lhs is None and rhs is None:
        return True
    if lhs is None or rhs is None:
        return False
    return fp2_eq(lhs[0], rhs[0], p) and fp2_eq(lhs[1], rhs[1], p)


def quaternion_to_endo_action(coords: tuple[int, int, int, int],
                              P: Point, p: int) -> Point:
    """Apply the endomorphism a*1 + b*iota + c*pi + d*(iota*pi) to P.

    Each coefficient is an integer (we work with Z<1, iota, pi, iota*pi>
    rather than the full O_0 lattice, to avoid division-by-2 ambiguity
    on individual points).
    """
    a, b, c, d = coords
    a_part = scalar_mul(a, P, A0, p)
    b_part = scalar_mul(b, endo_iota(P, p), A0, p)
    c_part = scalar_mul(c, endo_pi(P, p), A0, p)
    d_part = scalar_mul(d, endo_iota_pi(P, p), A0, p)

    from sqisign.curve import point_add
    result = a_part
    for term in (b_part, c_part, d_part):
        result = point_add(result, term, A0, p)
    return result
