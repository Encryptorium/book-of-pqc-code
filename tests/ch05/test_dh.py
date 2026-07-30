"""Toy Diffie-Hellman: the chapter's printed exchange and its order claims."""

import pytest

from kem_primitives.dh import (
    TOY_G,
    TOY_P,
    exchange,
    is_primitive_root,
    multiplicative_order,
    public_value,
    shared_value,
)


def test_chapter_block_prints_8_and_19():
    """The chapter's block prints "8 19" for a = 6, b = 15 mod 23."""
    A, B, _, _ = exchange(TOY_P, TOY_G, 6, 15)
    assert (A, B) == (8, 19)


def test_chapter_block_shared_value_is_2():
    """The chapter's block prints "True 2": both sides agree on 2."""
    _, _, K_A, K_B = exchange(TOY_P, TOY_G, 6, 15)
    assert K_A == K_B
    assert K_A == 2


def test_both_sides_agree_for_every_exponent_pair():
    """g^(ab) is symmetric in a and b, so the two views always agree."""
    for a in range(1, TOY_P):
        for b in range(1, TOY_P):
            _, _, K_A, K_B = exchange(TOY_P, TOY_G, a, b)
            assert K_A == K_B


def test_shared_value_equals_g_to_the_ab():
    """Both parties land on g^(ab) mod p, which is what the algebra claims."""
    a, b = 6, 15
    _, _, K_A, _ = exchange(TOY_P, TOY_G, a, b)
    assert K_A == pow(TOY_G, a * b, TOY_P)


def test_five_is_a_primitive_root_mod_23():
    """The chapter's comment claims ord(5) = phi(23) = 22 mod 23."""
    assert multiplicative_order(5, 23) == 22
    assert is_primitive_root(5, 23)


def test_five_is_a_primitive_root_mod_2063():
    """Exercise 1 concludes ord(5) = 2062 mod 2063, so 5 generates the group."""
    assert multiplicative_order(5, 2063) == 2062
    assert is_primitive_root(5, 2063)


def test_exercise_1_auxiliary_computation():
    """Appendix D's Exercise 1 block prints 2062, which is -1 mod 2063."""
    assert pow(5, 1031, 2063) == 2062
    assert pow(5, 1031, 2063) == 2063 - 1


def test_exercise_1_divisor_elimination():
    """The order divides 2062 = 2 * 1031, and the three proper divisors fail."""
    assert 2062 == 2 * 1031
    for proper_divisor in (1, 2, 1031):
        assert pow(5, proper_divisor, 2063) != 1


def test_a_non_generator_has_smaller_order():
    """2 is a quadratic residue mod 23, so its order is a proper divisor."""
    assert multiplicative_order(2, 23) == 11
    assert not is_primitive_root(2, 23)


def test_order_always_divides_p_minus_one():
    """Lagrange's theorem, which is what makes the divisor search exhaustive."""
    for g in range(1, 23):
        assert (23 - 1) % multiplicative_order(g, 23) == 0


def test_public_and_shared_value_compose():
    """shared_value(public_value(g, b), a) is the same as raising g to ab."""
    B = public_value(TOY_G, 15, TOY_P)
    assert shared_value(B, 6, TOY_P) == pow(TOY_G, 6 * 15, TOY_P)


def test_order_of_one_is_one():
    assert multiplicative_order(1, 23) == 1


def test_multiplicative_order_rejects_a_zero_residue():
    """0 has no order; the routine says so rather than looping."""
    with pytest.raises(ValueError):
        multiplicative_order(0, 23)
