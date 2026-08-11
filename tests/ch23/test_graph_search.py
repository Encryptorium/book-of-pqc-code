"""Tests for BFS over the supersingular isogeny graph at p = 431."""

import pytest

from sqisign.fp2 import fp2_eq
from sqisign.curve import j_invariant
from sqisign.deuring import A0, B0
from sqisign.graph import (
    two_torsion_points,
    three_torsion_x_coords,
    neighbors,
    find_path,
    walk_path,
)


P = 431


def test_E0_two_torsion():
    """E_0: y^2 = x^3 + x has 2-torsion at x = 0, x = i, x = -i in F_{p^2}.

    The roots of x^3 + x = x(x^2 + 1) are x = 0 and x = +/- sqrt(-1).
    Since p = 431 is 3 mod 4, sqrt(-1) is not in F_p, but sits in F_{p^2}
    as the element (0, 1) and its negative (0, -1) ≡ (0, 430).
    """
    points = two_torsion_points(A0, B0, P)
    assert len(points) == 3
    x_coords = sorted(((x[0], x[1]) for (x, _y) in points))
    assert (0, 0) in x_coords
    assert (0, 1) in x_coords or (0, P - 1) in x_coords


def test_E0_three_torsion_count():
    """E_0 has 4 distinct order-3 cyclic subgroups (degree-3 isogeny kernels)."""
    coords = three_torsion_x_coords(A0, B0, P)
    assert len(coords) == 4


def test_E0_neighbors_count():
    """E_0 has 3 degree-2 neighbors and 4 degree-3 neighbors."""
    edges = neighbors(A0, B0, P)
    deg2 = [e for e in edges if e[0] == 2]
    deg3 = [e for e in edges if e[0] == 3]
    assert len(deg2) == 3
    assert len(deg3) == 4


def test_path_from_E0_to_self_is_empty():
    """find_path with start = target returns the empty path."""
    path = find_path(A0, B0, A0, B0, P)
    assert path == []


def test_path_to_neighbor():
    """A degree-2 neighbor of E_0 is reachable in one step."""
    edges = neighbors(A0, B0, P)
    deg2_edges = [e for e in edges if e[0] == 2]
    # Pick the first degree-2 neighbor.
    _, _, na, nb = deg2_edges[0]
    j_target = j_invariant(na, nb, P)
    if fp2_eq(j_target, j_invariant(A0, B0, P), P):
        # If the neighbor has the same j as E_0, skip (j=1728 self-loops).
        return
    path = find_path(A0, B0, na, nb, P, max_depth=2)
    assert path is not None
    assert len(path) >= 1


def test_walk_path_round_trip():
    """walk_path produces a curve with the j-invariant predicted by find_path."""
    edges = neighbors(A0, B0, P)
    # Find a non-trivial degree-2 neighbor (different j-invariant).
    for degree, kernel, na, nb in edges:
        if degree != 2:
            continue
        if fp2_eq(j_invariant(na, nb, P), j_invariant(A0, B0, P), P):
            continue
        # Walk just this one step.
        a_walked, b_walked = walk_path(A0, B0, [(degree, kernel)], P)
        assert fp2_eq(j_invariant(a_walked, b_walked, P),
                      j_invariant(na, nb, P), P)
        return
    pytest.fail("no non-trivial degree-2 neighbor found")


def test_path_lands_at_target_j():
    """Walking find_path from E_start lands at a curve with target j-invariant."""
    # Pick a degree-3 neighbor of E_0 as the target.
    edges = neighbors(A0, B0, P)
    deg3_edges = [e for e in edges if e[0] == 3]
    _, _, na, nb = deg3_edges[0]
    target_j = j_invariant(na, nb, P)

    path = find_path(A0, B0, na, nb, P, max_depth=4)
    assert path is not None

    a_end, b_end = walk_path(A0, B0, path, P)
    assert fp2_eq(j_invariant(a_end, b_end, P), target_j, P)
