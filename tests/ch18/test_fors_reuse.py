"""FORS coverage: the exact form, its approximation, and the reuse thresholds.

The expected thresholds are the chapter's printed table. The approximation tests
are the part the chapter argues rather than prints: where the two forms agree,
and where the quoted one leaves its domain.
"""

import math

import pytest

from hash_cryptanalysis.fors_reuse import (
    expected_position_collisions,
    first_q_at_or_above,
    log2_fors_forgery,
    log2_fors_forgery_approx,
    single_signature_log2_forgery,
)
from hash_cryptanalysis.params import SHA2_PARAMETER_SETS, by_name


SHORT_NAMES = [ps.name.rsplit("-", 1)[-1] for ps in SHA2_PARAMETER_SETS]

#: The chapter's printed table: short name -> (log2_P at q=1, q@2^-128, q@2^-64).
PRINTED_TABLE = {
    "128s": (-168, 8, 176),
    "128f": (-198, 5, 20),
    "192s": (-238, 89, 1_253),
    "192f": (-264, 18, 78),
    "256s": (-308, 293, 2_341),
    "256f": (-315, 43, 170),
}


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_single_signature_probability_matches_the_chapter(short):
    ps = by_name(short)
    assert single_signature_log2_forgery(ps.k, ps.a) == PRINTED_TABLE[short][0]


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_exact_form_agrees_with_minus_ak_at_one_signature(short):
    """At q = 1 the exact coverage is (1/t)**k, so log2 P is exactly -ak."""
    ps = by_name(short)
    assert log2_fors_forgery(1, ps.k, ps.t) == pytest.approx(
        float(single_signature_log2_forgery(ps.k, ps.a))
    )


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_threshold_128_matches_the_chapter(short):
    ps = by_name(short)
    assert first_q_at_or_above(ps.k, ps.t, 128) == PRINTED_TABLE[short][1]


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_threshold_64_matches_the_chapter(short):
    ps = by_name(short)
    assert first_q_at_or_above(ps.k, ps.t, 64) == PRINTED_TABLE[short][2]


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_threshold_is_the_first_q_to_cross(short):
    """The returned q crosses the threshold and q - 1 does not. That is 'first'."""
    ps = by_name(short)
    for bits in (64, 128):
        q = first_q_at_or_above(ps.k, ps.t, bits)
        assert log2_fors_forgery(q, ps.k, ps.t) >= -bits
        assert log2_fors_forgery(q - 1, ps.k, ps.t) < -bits


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_coverage_is_monotone_in_q(short):
    """Monotonicity is what makes the bisection in first_q_at_or_above valid."""
    ps = by_name(short)
    values = [log2_fors_forgery(q, ps.k, ps.t) for q in range(1, 40)]
    assert all(b >= a for a, b in zip(values, values[1:]))


def test_zero_signatures_covers_nothing_in_both_forms():
    assert log2_fors_forgery(0, 14, 4_096) == float("-inf")
    assert log2_fors_forgery_approx(0, 14, 4_096) == float("-inf")


@pytest.mark.parametrize("q", [1, 2, 4, 8])
def test_approximation_tracks_the_exact_form_when_q_is_far_below_t(q):
    """At 128s, t = 4,096: the two forms agree to well under a bit at small q."""
    ps = by_name("128s")
    exact = log2_fors_forgery(q, ps.k, ps.t)
    approx = log2_fors_forgery_approx(q, ps.k, ps.t)
    assert abs(exact - approx) < 0.05


def test_approximation_upper_bounds_the_exact_form():
    """Bernoulli gives (1 - 1/t)**q >= 1 - q/t, so coverage never exceeds q/t."""
    for ps in SHA2_PARAMETER_SETS:
        for q in range(1, 200):
            assert log2_fors_forgery_approx(q, ps.k, ps.t) >= log2_fors_forgery(
                q, ps.k, ps.t
            ) - 1e-9


def test_approximation_leaves_its_domain_at_the_smallest_t():
    """At 128f, t = 64: the approximation returns a probability above 1 past q = t."""
    ps = by_name("128f")
    assert log2_fors_forgery_approx(ps.t, ps.k, ps.t) == 0.0
    assert log2_fors_forgery_approx(2 * ps.t, ps.k, ps.t) > 0.0
    assert log2_fors_forgery(2 * ps.t, ps.k, ps.t) < 0.0


def test_exact_form_never_exceeds_probability_one():
    for ps in SHA2_PARAMETER_SETS:
        for q in (1, ps.t, 10 * ps.t):
            assert log2_fors_forgery(q, ps.k, ps.t) <= 0.0


def test_position_collisions_match_the_chapter_estimate_at_h63():
    """The chapter quotes q**2 / 2**64 at h = 63, which is the pair count rounded up."""
    h = 63
    for q in (10**3, 10**6, 10**9):
        exact = expected_position_collisions(q, h)
        quoted = q**2 / 2**64
        assert exact == pytest.approx(quoted, rel=1e-6)


def test_position_collisions_are_below_one_until_roughly_two_to_the_h_over_two():
    """Below sqrt(2**h) draws a repeat is not yet expected; above it, it is."""
    h = 63
    assert expected_position_collisions(2 ** (h // 2 - 2), h) < 1.0
    assert expected_position_collisions(2 ** (h // 2 + 2), h) > 1.0


def test_position_collisions_at_the_fips_lifetime_limit():
    """2**64 signatures over 2**63 positions: about 2**64 repeated positions.

    Reuse is designed in, not designed out, which is the whole reason FORS
    carries a few-time bound rather than a one-time one.
    """
    assert math.log2(expected_position_collisions(2**64, 63)) == pytest.approx(
        64.0, abs=0.01
    )


def test_no_collisions_before_two_signatures():
    assert expected_position_collisions(0, 63) == 0.0
    assert expected_position_collisions(1, 63) == 0.0
