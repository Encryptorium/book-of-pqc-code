"""Tests for ``prelim_algebra.modular``.

The expected values are the ones Chapter 2 and its Appendix D page print. If
one of these tests fails, either the code or the book is wrong, and the two
cannot be reconciled by changing this file.
"""

import pytest

from prelim_algebra import ext_gcd, find_generator, mod_inv, mod_pow, order


def test_opening_example_matches_the_chapter() -> None:
    # The chapter opens with 7^200 mod 13 and prints 3.
    assert mod_pow(7, 200, 13) == 3


def test_fermat_shortcut_agrees_with_the_direct_route() -> None:
    # Fermat: 7^12 == 1 mod 13, and 200 == 16 * 12 + 8, so the exponent
    # collapses to 8. The chapter prints 3 for both routes.
    assert mod_pow(7, 12, 13) == 1
    assert mod_pow(7, 8, 13) == 3
    assert mod_pow(7, 200, 13) == mod_pow(7, 200 % 12, 13)


def test_mod_pow_agrees_with_the_builtin(small_primes: list[int]) -> None:
    # mod_pow exists to show what pow(base, exp, mod) does inside, so the two
    # must not diverge anywhere the book might use either.
    for p in small_primes:
        for base in range(p + 2):
            for exponent in range(8):
                assert mod_pow(base, exponent, p) == pow(base, exponent, p)


def test_mod_pow_zero_exponent_is_one() -> None:
    assert mod_pow(7, 0, 13) == 1


def test_mod_pow_modulus_one_is_zero() -> None:
    # result starts at 1 % modulus, not 1, so the zero ring returns its only
    # element rather than a 1 that is not in it.
    assert mod_pow(7, 200, 1) == 0


def test_mod_pow_rejects_a_negative_exponent() -> None:
    with pytest.raises(AssertionError):
        mod_pow(7, -1, 13)


def test_ext_gcd_returns_a_bezout_identity(small_primes: list[int]) -> None:
    # Non-negative arguments only; that is the documented precondition, and a
    # negative one can bottom the recursion out on a negative gcd.
    for a in range(0, 60):
        for b in small_primes:
            g, x, y = ext_gcd(a, b)
            assert a * x + b * y == g
            assert g > 0


def test_ext_gcd_base_case_is_the_first_argument() -> None:
    assert ext_gcd(12, 0) == (12, 1, 0)


def test_inverse_example_matches_the_chapter() -> None:
    # The chapter prints 38 for 17^-1 mod 43, then 1 for the product.
    assert mod_inv(17, 43) == 38
    assert (17 * mod_inv(17, 43)) % 43 == 1


def test_mod_inv_agrees_with_the_builtin(small_primes: list[int]) -> None:
    for p in small_primes:
        for a in range(1, p):
            assert mod_inv(a, p) == pow(a, -1, p)


def test_mod_inv_rejects_a_shared_factor() -> None:
    # 6 and 9 share the factor 3, so no inverse exists and the assert fires
    # rather than a wrong value coming back.
    with pytest.raises(AssertionError):
        mod_inv(6, 9)


def test_order_of_two_mod_17_is_eight() -> None:
    # Appendix D exercise 2: 2^8 == 1 mod 17, so 2 is not a generator.
    assert order(2, 17) == 8


def test_order_of_three_mod_17_is_sixteen() -> None:
    # Appendix D exercise 2: 3 has order exactly 16 and is a generator.
    assert order(3, 17) == 16


def test_order_divides_p_minus_one(small_primes: list[int]) -> None:
    # Lagrange's theorem, which is why an order equal to p - 1 is the whole
    # generator test.
    for p in small_primes:
        for g in range(1, p):
            assert (p - 1) % order(g, p) == 0


def test_generator_of_f17_is_three() -> None:
    # Exercise 2 asks for the first generator found by trial from 2 upward.
    assert find_generator(17) == 3


def test_powers_of_the_generator_hit_every_nonzero_element() -> None:
    # Appendix D prints this exact sequence for g = 3, p = 17.
    powers = [mod_pow(3, k, 17) for k in range(1, 17)]
    assert powers == [3, 9, 10, 13, 5, 15, 11, 16, 14, 8, 7, 4, 12, 2, 6, 1]
    assert sorted(powers) == list(range(1, 17))


def test_the_orbit_of_two_covers_half_the_group() -> None:
    # Appendix D's reason 2 fails: the orbit is 8 of the 16 nonzero elements.
    assert len({mod_pow(2, k, 17) for k in range(1, 17)}) == 8


def test_find_generator_returns_an_actual_generator(small_primes: list[int]) -> None:
    for p in small_primes:
        if p == 2:
            continue
        g = find_generator(p)
        assert order(g, p) == p - 1
        assert sorted(pow(g, k, p) for k in range(1, p)) == list(range(1, p))
