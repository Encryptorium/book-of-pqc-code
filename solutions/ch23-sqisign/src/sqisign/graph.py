"""BFS over the supersingular isogeny graph at p = 431.

The supersingular isogeny graph at prime p has one vertex per
supersingular j-invariant in F_{p^2} and edges for degree-l isogenies.
At p = 431 there are 37 supersingular j-invariants.  Degree-2 and
degree-3 isogenies suffice to connect the whole graph (Pizer 1990,
Ramanujan graphs are connected).

This module provides:
  - enumeration of degree-2 and degree-3 isogeny neighbors of a curve,
  - BFS to find a connecting isogeny path between two curves.

The torsion enumeration is brute-force scan over F_{p^2}: cubic and
quartic roots are found by direct evaluation.  At p = 431 this is fast
enough for a toy.  At cryptographic parameters it would be infeasible;
SQIsign solves the same path problem in time polynomial in log p by
working inside the quaternion algebra instead of on the curves.
"""

from __future__ import annotations

from collections import deque
from typing import Optional

from sqisign.fp2 import (
    fp2_add,
    fp2_eq,
    fp2_int_mul,
    fp2_mul,
    fp2_neg,
    fp2_pow,
    fp2_sqr,
    fp2_sub,
    fp2_zero,
)
from sqisign.curve import Fp2, Point, j_invariant, scalar_mul, point_add
from sqisign.velu import velu_isogeny


# ---- Torsion enumeration ----------------------------------------------------

_torsion_cache: dict[tuple[Fp2, Fp2, int], list[Point]] = {}


def _eval_cubic(x: Fp2, a: Fp2, b: Fp2, p: int) -> Fp2:
    """Evaluate f(x) = x^3 + a*x + b in F_{p^2}."""
    x2 = fp2_sqr(x, p)
    x3 = fp2_mul(x2, x, p)
    return fp2_add(fp2_add(x3, fp2_mul(a, x, p), p), b, p)


def _eval_psi3(x: Fp2, a: Fp2, b: Fp2, p: int) -> Fp2:
    """Evaluate the third division polynomial psi_3(x) = 3x^4 + 6ax^2 + 12bx - a^2."""
    x2 = fp2_sqr(x, p)
    x4 = fp2_sqr(x2, p)
    a2 = fp2_sqr(a, p)
    term1 = fp2_int_mul(3, x4, p)
    term2 = fp2_int_mul(6, fp2_mul(a, x2, p), p)
    term3 = fp2_int_mul(12, fp2_mul(b, x, p), p)
    return fp2_sub(fp2_add(fp2_add(term1, term2, p), term3, p), a2, p)


def two_torsion_points(a: Fp2, b: Fp2, p: int) -> list[Point]:
    """Find all non-identity 2-torsion points on y^2 = x^3 + ax + b.

    Scans F_{p^2} for roots of x^3 + ax + b.  Returns at most 3 points
    (the cubic has at most 3 roots).
    """
    cache_key = (a, b, p, 2)  # type: ignore
    if cache_key in _torsion_cache:
        return _torsion_cache[cache_key]

    points: list[Point] = []
    # F_p first: x = (x_re, 0).
    for x_re in range(p):
        x = (x_re, 0)
        if _eval_cubic(x, a, b, p) == (0, 0):
            points.append((x, (0, 0)))
    if len(points) < 3:
        # F_{p^2} \ F_p: x = (x_re, x_im) with x_im != 0.
        for x_re in range(p):
            for x_im in range(1, p):
                x = (x_re, x_im)
                if _eval_cubic(x, a, b, p) == (0, 0):
                    points.append((x, (0, 0)))
                    if len(points) >= 3:
                        break
            if len(points) >= 3:
                break

    _torsion_cache[cache_key] = points
    return points


def three_torsion_x_coords(a: Fp2, b: Fp2, p: int) -> list[Fp2]:
    """Find x-coordinates of points of order 3 on y^2 = x^3 + ax + b.

    These are roots of psi_3(x) = 3x^4 + 6ax^2 + 12bx - a^2.  Returns
    at most 4 distinct x-coordinates, each corresponding to a pair
    of points (x, y) and (x, -y) generating one cyclic subgroup of
    order 3.
    """
    cache_key = (a, b, p, 3)  # type: ignore
    if cache_key in _torsion_cache:
        return [x for (x, _y) in _torsion_cache[cache_key]]

    coords: list[Fp2] = []
    # F_p first.
    for x_re in range(p):
        x = (x_re, 0)
        if _eval_psi3(x, a, b, p) == (0, 0):
            coords.append(x)
    if len(coords) < 4:
        # F_{p^2} \ F_p.
        for x_re in range(p):
            for x_im in range(1, p):
                x = (x_re, x_im)
                if _eval_psi3(x, a, b, p) == (0, 0):
                    coords.append(x)
                    if len(coords) >= 4:
                        break
            if len(coords) >= 4:
                break

    return coords


def _y_coord(x: Fp2, a: Fp2, b: Fp2, p: int) -> Fp2 | None:
    """Recover a y-coordinate for x on y^2 = x^3 + ax + b, if one exists."""
    from sqisign.fp2 import fp2_sqrt
    rhs = _eval_cubic(x, a, b, p)
    return fp2_sqrt(rhs, p)


def three_torsion_points(a: Fp2, b: Fp2, p: int) -> list[Point]:
    """Find one representative of each cyclic order-3 subgroup."""
    points: list[Point] = []
    for x in three_torsion_x_coords(a, b, p):
        y = _y_coord(x, a, b, p)
        if y is not None:
            points.append((x, y))
    return points


# ---- Neighbors --------------------------------------------------------------

def neighbors(a: Fp2, b: Fp2, p: int) -> list[tuple[int, Point, Fp2, Fp2]]:
    """Return all degree-2 and degree-3 isogeny neighbors of E: y^2 = x^3 + ax + b.

    Each entry is (degree, kernel_generator, a_codomain, b_codomain).
    """
    edges: list[tuple[int, Point, Fp2, Fp2]] = []

    for T in two_torsion_points(a, b, p):
        new_a, new_b, _kernel, _aux = velu_isogeny(T, 2, a, b, p)
        edges.append((2, T, new_a, new_b))

    for T in three_torsion_points(a, b, p):
        new_a, new_b, _kernel, _aux = velu_isogeny(T, 3, a, b, p)
        edges.append((3, T, new_a, new_b))

    return edges


# ---- BFS path search --------------------------------------------------------

def _curve_key(a: Fp2, b: Fp2, p: int) -> tuple[int, int, int, int]:
    """Canonical key for a curve, by its j-invariant in F_{p^2}."""
    j = j_invariant(a, b, p)
    return (j[0] % p, j[1] % p, 0, 0)


def find_path(
    a_start: Fp2, b_start: Fp2,
    a_target: Fp2, b_target: Fp2,
    p: int,
    max_depth: int = 12,
) -> list[tuple[int, Point]] | None:
    """Find a sequence of isogenies connecting E_start to E_target.

    Returns a list of (degree, kernel_generator) steps, or None if no
    path is found within max_depth steps.

    Curves are compared by j-invariant.  Two curves with the same j
    are considered equivalent.
    """
    target_j = j_invariant(a_target, b_target, p)
    if fp2_eq(j_invariant(a_start, b_start, p), target_j, p):
        return []

    # BFS state: (a, b, path).  Visited is keyed by j-invariant.
    visited = {_curve_key(a_start, b_start, p)}
    queue: deque[tuple[Fp2, Fp2, list[tuple[int, Point]]]] = deque()
    queue.append((a_start, b_start, []))

    while queue:
        a, b, path = queue.popleft()
        if len(path) >= max_depth:
            continue
        for degree, kernel_gen, na, nb in neighbors(a, b, p):
            new_j_key = _curve_key(na, nb, p)
            new_path = path + [(degree, kernel_gen)]
            if fp2_eq(j_invariant(na, nb, p), target_j, p):
                return new_path
            if new_j_key in visited:
                continue
            visited.add(new_j_key)
            queue.append((na, nb, new_path))

    return None


def walk_path(
    a_start: Fp2, b_start: Fp2,
    path: list[tuple[int, Point]],
    p: int,
) -> tuple[Fp2, Fp2]:
    """Walk a sequence of isogenies starting at E_start, return final (a, b).

    Each step (degree, kernel_gen) applies a degree-`degree` Velu isogeny
    with kernel generated by `kernel_gen`.  Note: kernel_gen is a point
    on the CURRENT curve at the time of that step.
    """
    a, b = a_start, b_start
    for degree, kernel_gen in path:
        a, b, _k, _aux = velu_isogeny(kernel_gen, degree, a, b, p)
    return a, b
