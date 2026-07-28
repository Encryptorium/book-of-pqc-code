"""Pins every number Chapter 3 and its Appendix D print about the 2D lattice."""

from hard_problems.lattice import (
    CHAPTER_BASIS,
    determinant,
    enumerate_coefficient_box,
    in_lattice,
    lattice_points_up_to,
    shortest_vectors,
)


def test_chapter_basis_matches_the_printed_matrix():
    assert CHAPTER_BASIS == ((2, 7), (5, 3))


def test_determinant_is_the_congruence_modulus(chapter_basis):
    """The chapter's modulus 29 is not a coincidence; it is abs(det B)."""
    assert determinant(chapter_basis) == -29
    assert abs(determinant(chapter_basis)) == 29


def test_membership_congruence_is_the_chapter_s_7x_minus_2y(chapter_basis):
    """in_lattice must agree with 7x - 2y == 0 (mod 29) at every integer point."""
    for x in range(-15, 16):
        for y in range(-15, 16):
            assert in_lattice(chapter_basis, (x, y)) == ((7 * x - 2 * y) % 29 == 0)


def test_membership_congruence_agrees_with_solving_the_system(chapter_basis):
    """The congruence is sufficient, not merely necessary.

    Solve for integer coefficients directly over a range wide enough to reach
    every point in the test window, and confirm the two answers never differ.
    This is the claim the module docstring derives, checked rather than trusted.
    """
    (b11, b12), (b21, b22) = chapter_basis
    reachable = {
        (a * b11 + b * b21, a * b12 + b * b22)
        for a in range(-30, 31)
        for b in range(-30, 31)
    }
    for x in range(-14, 15):
        for y in range(-14, 15):
            assert in_lattice(chapter_basis, (x, y)) == ((x, y) in reachable)


def test_points_that_look_short_but_are_not_in_the_lattice(chapter_basis):
    """(3, 4) and (-3, -4) have norm 5 but are not in L; (-3, 4) and (3, -4) are.

    Worth pinning because the four sign combinations of (3, 4) split two-and-two,
    which is exactly the trap in the exercise's boundary check.
    """
    assert in_lattice(chapter_basis, (-3, 4))
    assert in_lattice(chapter_basis, (3, -4))
    assert not in_lattice(chapter_basis, (3, 4))
    assert not in_lattice(chapter_basis, (-3, -4))


def test_brute_search_over_the_seven_by_seven_box(chapter_basis):
    """Appendix D: 48 pairs checked, minimum squared norm 25, two minimizers."""
    found = enumerate_coefficient_box(chapter_basis, 3)
    assert len(found) == 48
    assert found[0][0] == 25
    minimizers = {(coeffs, vector) for norm, coeffs, vector in found if norm == 25}
    assert minimizers == {((1, -1), (-3, 4)), ((-1, 1), (3, -4))}


def test_basis_vectors_are_not_the_shortest(chapter_basis):
    """The chapter's opening claim: both basis vectors are longer than 5."""
    assert 53 > 25 and 34 > 25
    box = {vector: norm for norm, _, vector in enumerate_coefficient_box(chapter_basis, 3)}
    assert box[(2, 7)] == 53
    assert box[(5, 3)] == 34


def test_nothing_lies_strictly_inside_radius_five(chapter_basis):
    """The load-bearing claim of Figure 3.1 and of Appendix D's closure."""
    inside = [p for p in lattice_points_up_to(chapter_basis, 24) if p != (0, 0)]
    assert inside == []


def test_the_boundary_of_radius_five_holds_exactly_two_lattice_points(chapter_basis):
    """Twelve integer points have x^2 + y^2 == 25; two of them are in L."""
    integer_points = [
        (x, y) for x in range(-5, 6) for y in range(-5, 6) if x * x + y * y == 25
    ]
    assert len(integer_points) == 12
    on_circle = [p for p in lattice_points_up_to(chapter_basis, 25) if p != (0, 0)]
    assert sorted(on_circle) == [(-3, 4), (3, -4)]


def test_shortest_vectors_are_exact_not_best_so_far(chapter_basis):
    assert shortest_vectors(chapter_basis) == (25, [(-3, 4), (3, -4)])


def test_figure_3_1_shows_nineteen_points_out_to_norm_thirteen(chapter_basis):
    """Figure 3.1's footnote claims all nineteen; the origin is one of them."""
    points = lattice_points_up_to(chapter_basis, 169)
    assert len(points) == 19
    assert (0, 0) in points
    assert max(x * x + y * y for x, y in points) == 149


def test_no_lattice_point_sits_between_norm_thirteen_and_the_next_shell(chapter_basis):
    """Why "norm at most 13" is an honest cutoff rather than a convenient one.

    The largest point inside the cutoff has squared norm 149, and there is
    nothing between 149 and 169, so the figure is not hiding a point just past
    the line it drew.
    """
    assert lattice_points_up_to(chapter_basis, 169) == lattice_points_up_to(
        chapter_basis, 149
    )


def test_lattice_is_closed_under_negation(chapter_basis):
    for point in lattice_points_up_to(chapter_basis, 169):
        assert in_lattice(chapter_basis, (-point[0], -point[1]))
