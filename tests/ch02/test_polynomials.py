"""Tests for ``prelim_algebra.polynomials``.

The expected values are the ones Chapter 2 and its Appendix D page print. If
one of these tests fails, either the code or the book is wrong, and the two
cannot be reconciled by changing this file.
"""

import pytest

from prelim_algebra import poly_eval, poly_mod, poly_mul, roots


def test_multiplication_example_matches_the_chapter() -> None:
    # The chapter multiplies (2 + x) by (3 + x^2) in F_5[x] and prints
    # [1, 3, 2, 1], which reads back as 1 + 3x + 2x^2 + x^3.
    assert poly_mul([2, 1], [3, 0, 1], 5) == [1, 3, 2, 1]


def test_multiplication_coefficients_are_the_ones_the_prose_walks() -> None:
    # The chapter walks each coefficient: 2*3 = 6 = 1 mod 5, then 3, 2, 1.
    product = poly_mul([2, 1], [3, 0, 1], 5)
    assert product[0] == (2 * 3) % 5
    assert product[1] == (2 * 0 + 1 * 3) % 5
    assert product[2] == (2 * 1 + 1 * 0) % 5
    assert product[3] == (1 * 1) % 5


def test_product_degree_is_the_sum_of_degrees() -> None:
    for f, g in (([2, 1], [3, 0, 1]), ([1], [4, 4]), ([1, 1, 1], [1, 1])):
        assert len(poly_mul(f, g, 7)) == len(f) + len(g) - 1


def test_multiplication_is_commutative() -> None:
    assert poly_mul([2, 1], [3, 0, 1], 5) == poly_mul([3, 0, 1], [2, 1], 5)


def test_reduction_example_matches_the_chapter() -> None:
    # The chapter reduces (1 + x + x^3)(2 + x^2) modulo x^3 + x + 1 over F_7.
    # The modulus is a factor of the product by construction, so the remainder
    # is the zero polynomial, printed at full length as [0, 0, 0].
    f_mod = [1, 1, 0, 1]
    product = poly_mul(f_mod, [2, 0, 1], 7)
    assert poly_mod(product, f_mod, 7) == [0, 0, 0]


def test_reduction_does_not_trim_trailing_zeros() -> None:
    # The chapter is explicit that the zero polynomial comes back as [0, 0, 0]
    # rather than [0] or [], and that trimming is the caller's job.
    result = poly_mod([0, 0, 0, 0, 0], [1, 1, 0, 1], 7)
    assert result == [0, 0, 0]
    assert len(result) == 3


def test_reduction_output_has_degree_below_the_modulus() -> None:
    f_mod = [1, 1, 0, 1]
    for a in ([5, 0, 0, 0, 2], [1, 2, 3, 4, 5, 6], [3, 3, 3]):
        assert len(poly_mod(a, f_mod, 7)) == len(f_mod) - 1


def test_reduction_leaves_a_polynomial_already_below_degree_alone() -> None:
    assert poly_mod([3, 4], [1, 1, 0, 1], 7) == [3, 4]


def test_reduction_canonicalizes_unreduced_coefficients() -> None:
    # The loop body never runs when the input is already below deg(f), so
    # without reducing on entry an unreduced coefficient would pass straight
    # through: poly_mod([8], [1, 0, 1], 7) would answer 8 rather than 1.
    assert poly_mod([8], [1, 0, 1], 7) == [1]
    assert poly_mod([15, 22], [1, 1, 0, 1], 7) == [1, 1]


def test_reduction_output_coefficients_are_in_range() -> None:
    for a in ([100, -3, 57], [8], [0, 0], [1, 2, 3, 4, 5, 6, 7]):
        assert all(0 <= c < 7 for c in poly_mod(a, [1, 1, 0, 1], 7))


def test_reduction_rejects_a_non_monic_modulus() -> None:
    with pytest.raises(AssertionError):
        poly_mod([1, 2, 3, 4], [1, 1, 0, 2], 7)


def test_reduction_is_additive() -> None:
    # (a + b) mod f == (a mod f) + (b mod f), which is what makes the quotient
    # a ring rather than just a set of representatives.
    f_mod = [1, 1, 0, 1]
    a, b = [1, 2, 3, 4, 5], [6, 5, 4, 3, 2]
    total = [(x + y) % 7 for x, y in zip(a, b)]
    left = poly_mod(total, f_mod, 7)
    ra, rb = poly_mod(a, f_mod, 7), poly_mod(b, f_mod, 7)
    assert left == [(x + y) % 7 for x, y in zip(ra, rb)]


def test_evaluation_matches_the_appendix_value_list() -> None:
    # Appendix D exercise 3 prints f(0) through f(6) for f = 1 + x + x^3
    # over F_7.
    coeffs = [1, 1, 0, 1]
    assert [poly_eval(coeffs, k, 7) for k in range(7)] == [1, 3, 4, 3, 6, 5, 6]


def test_the_exercise_polynomial_has_no_root_in_f7() -> None:
    # Appendix D exercise 3 prints an empty root list, which is what makes
    # x^3 + x + 1 irreducible over F_7.
    assert roots([1, 1, 0, 1], 7) == []


def test_roots_found_are_actually_roots(small_primes: list[int]) -> None:
    coeffs = [1, 1, 0, 1]
    for p in small_primes:
        for k in roots(coeffs, p):
            assert poly_eval(coeffs, k, p) == 0


def test_a_polynomial_with_a_known_root_reports_it() -> None:
    # x^2 - 1 = (x - 1)(x + 1) over F_7, so the roots are 1 and 6.
    assert roots([6, 0, 1], 7) == [1, 6]


def test_degree_four_breaks_the_root_irreducibility_equivalence() -> None:
    # The exercise's own counterexample: (x^2 + 1)^2 over F_3 is reducible and
    # still has no root, which is why the equivalence stops below degree 4.
    squared = poly_mul([1, 0, 1], [1, 0, 1], 3)
    assert squared == [1, 0, 2, 0, 1]
    assert roots(squared, 3) == []
