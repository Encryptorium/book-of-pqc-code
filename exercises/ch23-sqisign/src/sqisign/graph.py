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
    # EXERCISE: implement this function.
    #
    # The x-coordinates of the order-3 points are the roots of the third
    # division polynomial, which _eval_psi3 already evaluates for you. Scan
    # the same way two_torsion_points does, F_p first and then the rest of
    # F_p^2, and stop at four roots because psi_3 is a quartic. Return
    # x-coordinates rather than points: each root gives the pair (x, y) and
    # (x, -y), and those two points generate the same cyclic subgroup, so
    # four roots means four degree-3 kernels rather than eight.
    #
    # Reference: Chapter 23, 'Finding a path in the isogeny graph'
    #
    # Proved by:
    #   tests/ch23/test_graph_search.py
    raise NotImplementedError("exercise: three_torsion_x_coords")


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
    # EXERCISE: implement this function.
    #
    # Enumerate the outgoing edges of one vertex. For each 2-torsion point
    # run velu_isogeny at degree 2, and for each order-3 point run it at
    # degree 3, recording (degree, kernel_generator, a_codomain, b_codomain)
    # per edge. The kernel generator has to be kept, not just the codomain:
    # a signature is a list of these generators, and each one is a point on
    # the curve as it stood at that step. The order of this list is the
    # canonical neighbour order that the walk's kernel_index selects into,
    # so producing degree-2 edges before degree-3 edges is part of the
    # contract rather than a detail.
    #
    # Reference: Chapter 23, 'BFS over the isogeny graph'
    #
    # Proved by:
    #   tests/ch23/test_graph_search.py
    #   tests/ch23/test_sqisign_roundtrip.py
    raise NotImplementedError("exercise: neighbors")


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
    # EXERCISE: implement this function.
    #
    # Breadth-first search over the graph, with vertices identified by
    # j-invariant rather than by coefficient pair, since isomorphic curves
    # are the same vertex. Return the empty path when start and target
    # already share a j. Otherwise seed a deque with (a_start, b_start, [])
    # and a visited set holding the start key, then pop, skip anything
    # already at max_depth, and for each neighbour extend the path, return
    # it the moment the neighbour's j matches the target, and otherwise
    # enqueue the neighbour if its key is new. Return None when the queue
    # empties. Testing the target before the visited check matters: a target
    # that is also a previously visited vertex would otherwise be skipped.
    # This search costs O(p), which is exactly why the real scheme works
    # inside the quaternion algebra instead of walking the graph.
    #
    # Reference: Chapter 23, 'BFS over the isogeny graph'
    #
    # Proved by:
    #   tests/ch23/test_graph_search.py
    #   tests/ch23/test_sqisign_roundtrip.py
    raise NotImplementedError("exercise: find_path")


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
    # EXERCISE: implement this function.
    #
    # Replay a path: for each (degree, kernel_generator) step apply
    # velu_isogeny at that degree from the current coefficients and carry
    # the codomain forward, returning the final pair. The kernel generator
    # belongs to the curve as it stood at that step, so the steps only make
    # sense in order and only from the curve the path was found on. This is
    # the verifier's whole computation.
    #
    # Reference: Chapter 23, 'Toy SQIsign: verify'
    #
    # Proved by:
    #   tests/ch23/test_graph_search.py
    #   tests/ch23/test_sqisign_roundtrip.py
    raise NotImplementedError("exercise: walk_path")
