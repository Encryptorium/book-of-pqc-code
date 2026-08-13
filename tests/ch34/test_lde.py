"""Tests for starks.lde."""

from __future__ import annotations

import pytest

from starks.arithmetization import (
    DEFAULT_PRIME,
    TRACE_DOMAIN_GENERATOR,
    TRACE_LENGTH,
    fibonacci_trace,
    interpolate_trace,
)
from starks.lde import (
    COSET_SHIFT,
    LDE_BLOWUP,
    LDE_GENERATOR,
    LDE_SIZE,
    eval_poly,
    extend_polynomial,
    lde_domain,
    mod_inv,
    trace_domain,
    vanishing_polynomial,
)


def test_trace_domain_size_and_generator_order():
    dom = trace_domain()
    assert len(dom) == TRACE_LENGTH
    assert dom[0] == 1
    # g_8 has order EXACTLY 8 mod 97. Asserting only that g^8 == 1 proves
    # the order divides 8, which every order-1, -2 and -4 element also
    # satisfies: g = 22 has order 4 and passes that weaker check.
    power = 1
    for step in range(1, TRACE_LENGTH + 1):
        power = (power * TRACE_DOMAIN_GENERATOR) % DEFAULT_PRIME
        assert (power == 1) == (step == TRACE_LENGTH)


def test_domain_constants_match_the_values_the_chapter_prints():
    """Pin the three constants Chapter 34 prints as literals.

    Block 3 prints TRACE_GEN = 64, LDE_GEN = 28 and COSET_SHIFT = 5, and
    Block 4 hard-codes the resulting domain. Nothing else in this suite
    binds them: <28> and <69> are the same subgroup, and 7 sits outside
    it just as 5 does, so swapping either constant leaves every
    structural property intact while silently invalidating the printed
    listings and Figure 34.2.
    """
    assert DEFAULT_PRIME == 97
    assert TRACE_LENGTH == 8
    assert TRACE_DOMAIN_GENERATOR == 64
    assert LDE_GENERATOR == 28
    assert COSET_SHIFT == 5
    assert LDE_BLOWUP == 4
    # The sequence, not just the set: this is what Block 4 hard-codes.
    assert lde_domain()[:6] == [5, 43, 40, 53, 29, 36]
    assert trace_domain() == [1, 64, 22, 50, 96, 33, 75, 47]


def test_lde_domain_size_and_coset_disjoint_from_subgroup():
    dom = lde_domain()
    assert len(dom) == LDE_SIZE
    assert LDE_SIZE == TRACE_LENGTH * LDE_BLOWUP
    # Every LDE point is coset_shift * subgroup element, so none of
    # them should equal 1 (the identity of the subgroup).
    assert 1 not in dom
    # The trace domain is inside the order-32 subgroup, so it must be
    # disjoint from the LDE coset.
    tdom = trace_domain()
    assert not (set(tdom) & set(dom))


def test_lde_domain_closed_under_negation():
    dom = lde_domain()
    # The order-32 subgroup contains -1 = 28^16 = 96, so the coset is
    # closed under negation.
    neg_set = {(-x) % DEFAULT_PRIME for x in dom}
    assert neg_set == set(dom)


def test_lde_domain_invalid_size_raises():
    with pytest.raises(ValueError):
        lde_domain(size=3)


def test_lde_domain_invalid_generator_raises():
    with pytest.raises(ValueError):
        lde_domain(generator=2)


def test_lde_domain_shift_inside_subgroup_raises():
    # 28 is the generator; it is in the subgroup itself.
    with pytest.raises(ValueError):
        lde_domain(coset_shift=LDE_GENERATOR)


def test_lde_domain_zero_shift_raises():
    with pytest.raises(ValueError):
        lde_domain(coset_shift=0)


def test_extend_polynomial_matches_direct_eval():
    trace = fibonacci_trace()
    tdom = trace_domain()
    coeffs = interpolate_trace(trace, tdom, DEFAULT_PRIME)
    ldom = lde_domain()
    codeword = extend_polynomial(coeffs, ldom, DEFAULT_PRIME)
    assert len(codeword) == LDE_SIZE
    for x, c in zip(ldom, codeword):
        assert c == eval_poly(coeffs, x, DEFAULT_PRIME)


def test_extend_polynomial_empty_coeffs_raises():
    with pytest.raises(ValueError):
        extend_polynomial([], [1, 2], DEFAULT_PRIME)


def test_extend_polynomial_empty_domain_raises():
    with pytest.raises(ValueError):
        extend_polynomial([1, 2], [], DEFAULT_PRIME)


def test_vanishing_polynomial_zero_on_trace_domain():
    tdom = trace_domain()
    for x in tdom:
        assert vanishing_polynomial(tdom, x, DEFAULT_PRIME) == 0


def test_vanishing_polynomial_nonzero_on_lde_coset():
    tdom = trace_domain()
    ldom = lde_domain()
    for x in ldom:
        assert vanishing_polynomial(tdom, x, DEFAULT_PRIME) != 0


def test_vanishing_polynomial_empty_raises():
    with pytest.raises(ValueError):
        vanishing_polynomial([], 1, DEFAULT_PRIME)


def test_mod_inv_roundtrip():
    for a in range(1, DEFAULT_PRIME):
        inv = mod_inv(a, DEFAULT_PRIME)
        assert (a * inv) % DEFAULT_PRIME == 1


def test_mod_inv_zero_raises():
    with pytest.raises(ValueError):
        mod_inv(0, DEFAULT_PRIME)


def test_eval_poly_at_zero_equals_constant_term():
    coeffs = [7, 2, 5]  # 7 + 2x + 5x^2
    assert eval_poly(coeffs, 0, DEFAULT_PRIME) == 7


def test_eval_poly_monomial():
    coeffs = [0, 0, 1]  # x^2
    assert eval_poly(coeffs, 3, DEFAULT_PRIME) == 9
    assert eval_poly(coeffs, 10, DEFAULT_PRIME) == 100 % DEFAULT_PRIME


def test_eval_poly_empty_coeffs_raises():
    with pytest.raises(ValueError):
        eval_poly([], 3, DEFAULT_PRIME)


def test_coset_shift_property_on_omega_multiplication():
    # Multiplying an LDE point by omega = g_8 = TRACE_DOMAIN_GENERATOR
    # should produce another LDE point, because g_8 = g_32^4 is in the
    # order-32 subgroup. The index shift is 4 (since LDE is indexed by
    # powers of g_32 and g_8 = g_32^4).
    ldom = lde_domain()
    for i in range(LDE_SIZE):
        expected = ldom[(i + 4) % LDE_SIZE]
        actual = (ldom[i] * TRACE_DOMAIN_GENERATOR) % DEFAULT_PRIME
        assert actual == expected
