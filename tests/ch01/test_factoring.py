"""Tests for ``quantum_threat.factoring``.

The expected values are the ones Chapter 1 and its Appendix D page print. If
one of these tests fails, either the code or the book is wrong, and the two
cannot be reconciled by changing this file.
"""

import math

from quantum_threat import factor_trial_division, factor_trial_division_counted


def test_chapter_modulus_factors_as_printed() -> None:
    # The chapter prints "3233 = 53 x 61".
    assert factor_trial_division(3233) == (53, 61)


def test_counted_matches_the_appendix_division_count() -> None:
    # Appendix D, exercise 2 prints "3233 = 53 x 61 (52 trial divisions)".
    assert factor_trial_division_counted(3233) == (53, 61, 52)


def test_prime_reports_no_factorization() -> None:
    assert factor_trial_division(7919) is None
    assert factor_trial_division_counted(7919) is None


def test_smallest_composite() -> None:
    # 4 is the first n whose loop body runs at all: candidate 2 divides it on
    # the first division.
    assert factor_trial_division(4) == (2, 2)
    assert factor_trial_division_counted(4) == (2, 2, 1)


def test_below_four_reports_none() -> None:
    # candidate * candidate <= n is false at once for 0 through 3, so the
    # search reports None rather than claiming a factorization.
    for n in (0, 1, 2, 3):
        assert factor_trial_division(n) is None


def test_factor_pair_multiplies_back(semiprimes: list[tuple[int, int, int]]) -> None:
    for n, p, q in semiprimes:
        assert factor_trial_division(n) == (p, q)


def test_count_is_the_smaller_factor_minus_one(
    semiprimes: list[tuple[int, int, int]],
) -> None:
    # Appendix D derives this: the loop stops at the smaller prime factor, so
    # for n = pq with p <= q it performs exactly p - 1 divisions.
    for n, p, _q in semiprimes:
        result = factor_trial_division_counted(n)
        assert result is not None
        assert result[2] == p - 1


def test_count_is_below_the_sqrt_bound(semiprimes: list[tuple[int, int, int]]) -> None:
    # The same point stated as the comparison Appendix D makes for 3233:
    # 52 divisions against a floor(sqrt(n)) of 56. The gap never closes. The
    # count is p - 1 and floor(sqrt(pq)) is at least p, so the strict
    # inequality holds even for a square, where 9409 costs 96 against 97.
    for n, _p, _q in semiprimes:
        result = factor_trial_division_counted(n)
        assert result is not None
        assert result[2] < math.isqrt(n)


def test_both_functions_agree_on_the_factor_pair(
    semiprimes: list[tuple[int, int, int]],
) -> None:
    for n, _p, _q in semiprimes:
        plain = factor_trial_division(n)
        counted = factor_trial_division_counted(n)
        assert counted is not None and plain is not None
        assert counted[:2] == plain
