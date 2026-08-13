"""Bit-margin arithmetic for Chapter 35."""

import math

import pytest

from zk_case_studies.margins import (
    bit_margin_pairing,
    composed_margin,
    decoding_radius,
    dfms20_exact_cbits,
    dfms20_required_cbits,
    query_miss_bits,
    shor_pairing_margin,
    stark_classical_margin,
)


def test_pairing_margin_is_zero_at_every_width():
    for width in (256, 381, 448, 1024):
        assert bit_margin_pairing(width) == 0
        assert shor_pairing_margin(width) == 0


def test_pairing_margin_rejects_non_positive_width():
    with pytest.raises(ValueError):
        bit_margin_pairing(0)
    with pytest.raises(ValueError):
        shor_pairing_margin(-1)


def test_the_three_radii_are_ordered_and_distinct():
    # Ch 34 Section 5.1: unique-decoding < Johnson < capacity, strictly, at
    # every rate. Only the Johnson value carries a proven proximity gap.
    for rho in (1 / 2, 1 / 4, 1 / 8, 1 / 16):
        unique = decoding_radius(rho, "unique")
        johnson = decoding_radius(rho, "johnson")
        capacity = decoding_radius(rho, "capacity")
        assert unique < johnson < capacity


def test_radii_take_their_published_values_at_rho_one_sixteenth():
    assert decoding_radius(1 / 16, "unique") == pytest.approx(0.46875)
    assert decoding_radius(1 / 16, "johnson") == pytest.approx(0.75)
    assert decoding_radius(1 / 16, "capacity") == pytest.approx(0.9375)


def test_johnson_radius_is_not_half_the_johnson_radius():
    # Guards the defect this chapter shipped with: the listings described
    # delta_0 = 1 - sqrt(rho) as conjectured and named (1 - sqrt(rho)) / 2
    # as the proven Johnson form. That halved value is no radius at all.
    rho = 1 / 16
    johnson = decoding_radius(rho, "johnson")
    assert johnson != pytest.approx(johnson / 2)
    for regime in ("unique", "johnson", "capacity"):
        assert decoding_radius(rho, regime) != pytest.approx(johnson / 2)


def test_decoding_radius_rejects_bad_rate_and_regime():
    with pytest.raises(ValueError):
        decoding_radius(0.0, "johnson")
    with pytest.raises(ValueError):
        decoding_radius(1.0, "johnson")
    with pytest.raises(ValueError):
        decoding_radius(0.25, "capacity_conjectured")


def test_stark_classical_margin_reproduces_the_boojum_listing():
    assert stark_classical_margin(field_bits=128, L=2 ** 16, N=2 ** 20,
                                  mu=40, r_FRI=16, grinding=20) == 100.0


def test_stark_classical_margin_reproduces_the_ethstark_listing():
    assert stark_classical_margin(field_bits=244, L=2 ** 20, N=2 ** 24,
                                  mu=48, r_FRI=20, grinding=20) == 116.0


def test_composed_margin_total_matches_the_listing_wrapper():
    args = dict(field_bits=128, L=2 ** 16, N=2 ** 20, mu=40, r_FRI=16,
                grinding=20)
    assert composed_margin(**args).total == stark_classical_margin(**args)


def test_the_per_round_term_dominates_at_the_chapter_configurations():
    # The three terms are log-probabilities, so the least negative dominates.
    # At both printed parameter points that is the FRI per-round term, not
    # the query-consistency term.
    for args in (dict(field_bits=128, L=2 ** 16, N=2 ** 20, mu=40, r_FRI=16,
                      grinding=20),
                 dict(field_bits=244, L=2 ** 20, N=2 ** 24, mu=48, r_FRI=20,
                      grinding=20),
                 dict(field_bits=128, L=2 ** 18, N=2 ** 22, mu=48, r_FRI=18,
                      grinding=20)):
        terms = composed_margin(**args)
        assert terms.dominant == "per_round"
        assert terms.per_round > terms.consistency
        assert terms.per_round > terms.bad_beta


def test_regime_choice_moves_the_margin_by_the_stated_amount():
    args = dict(field_bits=128, L=2 ** 16, N=2 ** 20, mu=40, r_FRI=16,
                grinding=20)
    johnson = composed_margin(**args, regime="johnson").total
    unique = composed_margin(**args, regime="unique").total
    capacity = composed_margin(**args, regime="capacity").total
    assert unique < johnson < capacity
    assert johnson == 100.0
    assert johnson - unique == pytest.approx(43.5, abs=0.1)


def test_composed_margin_rejects_a_blowup_below_one():
    with pytest.raises(ValueError):
        composed_margin(field_bits=128, L=2 ** 20, N=2 ** 16, mu=40,
                        r_FRI=16, grinding=20)
    with pytest.raises(ValueError):
        composed_margin(field_bits=128, L=2 ** 16, N=2 ** 16, mu=40,
                        r_FRI=16, grinding=20)


def test_composed_margin_rejects_negative_grinding():
    with pytest.raises(ValueError):
        composed_margin(field_bits=128, L=2 ** 16, N=2 ** 20, mu=40,
                        r_FRI=16, grinding=-1)


def test_dfms20_approximation_matches_the_printed_requirement():
    assert dfms20_required_cbits(k_target=128, q_bits=80, r_FS=6) == 182
    assert dfms20_required_cbits(k_target=80, q_bits=80, r_FS=6) == 174


def test_the_exact_dfms20_form_exceeds_the_approximation_by_about_two_bits():
    # The chapter's Block 3 comment claims the approximation drops the
    # log2(2q + 1) correction and under-estimates by roughly two bits.
    for k, q, r in ((128, 80, 6), (128, 64, 4), (80, 80, 6)):
        gap = dfms20_exact_cbits(k, q, r) - dfms20_required_cbits(k, q, r)
        assert 1 <= gap <= 3


def test_dfms20_rejects_non_positive_target_and_rounds():
    for fn in (dfms20_required_cbits, dfms20_exact_cbits):
        with pytest.raises(ValueError):
            fn(k_target=0, q_bits=80, r_FS=6)
        with pytest.raises(ValueError):
            fn(k_target=128, q_bits=80, r_FS=0)
        with pytest.raises(ValueError):
            fn(k_target=128, q_bits=-1, r_FS=6)


def test_query_miss_bits_reproduces_the_stwo_listing():
    args = dict(n_queries=70, pow_bits=26, log_blowup=1)
    assert query_miss_bits(**args, regime="capacity") == 96.0
    assert query_miss_bits(**args, regime="johnson") == 61.0
    assert query_miss_bits(**args, regime="unique") == 55.1


def test_the_stwo_headline_is_reachable_only_at_capacity():
    # At a blowup of two the capacity radius is exactly 1/2, so every query
    # path is worth exactly one bit and 70 + 26 lands on 96 with nothing
    # rounded. No other regime reaches the published figure.
    args = dict(n_queries=70, pow_bits=26, log_blowup=1)
    assert query_miss_bits(**args, regime="capacity") == 70 + 26
    for regime in ("johnson", "unique"):
        assert query_miss_bits(**args, regime=regime) < 70 + 26


def test_query_miss_bits_rejects_bad_parameters():
    with pytest.raises(ValueError):
        query_miss_bits(n_queries=0, pow_bits=26, log_blowup=1,
                        regime="johnson")
    with pytest.raises(ValueError):
        query_miss_bits(n_queries=70, pow_bits=-1, log_blowup=1,
                        regime="johnson")
    with pytest.raises(ValueError):
        query_miss_bits(n_queries=70, pow_bits=26, log_blowup=1,
                        regime="nonesuch")


def test_grinding_enters_the_budget_additively():
    base = dict(field_bits=128, L=2 ** 16, N=2 ** 20, mu=40, r_FRI=16)
    assert (composed_margin(**base, grinding=20).total
            - composed_margin(**base, grinding=0).total) == pytest.approx(20.0)
    assert math.isclose(
        query_miss_bits(n_queries=70, pow_bits=26, log_blowup=1,
                        regime="johnson")
        - query_miss_bits(n_queries=70, pow_bits=0, log_blowup=1,
                          regime="johnson"), 26.0)


def test_the_consistency_term_takes_its_stated_form():
    # mu * log2((L - 1) / N), because two distinct polynomials of degree
    # below L agree at no more than L - 1 of the N LDE points. The term is
    # numerically inert at every parameter point the chapter prints, so only
    # a test reading the term itself can hold the L - 1 in place.
    terms = composed_margin(field_bits=128, L=2 ** 16, N=2 ** 20, mu=40,
                            r_FRI=16, grinding=20)
    assert terms.consistency == pytest.approx(
        40 * math.log2((2 ** 16 - 1) / 2 ** 20))
    assert terms.consistency != pytest.approx(40 * math.log2(2 ** 16 / 2 ** 20))


def test_the_consistency_term_is_never_the_dominant_one():
    # At the Johnson radius the per-round term is mu * log2(sqrt(rho)) and
    # the consistency term is about mu * log2(rho). Since log2(rho) is
    # negative, log2(rho) < 0.5 * log2(rho) at every rate, so the query
    # consistency term is structurally subdominant rather than incidentally
    # so at the chapter's numbers.
    for log_blowup in (1, 2, 3, 4, 5):
        N = 2 ** 24
        L = N >> log_blowup
        terms = composed_margin(field_bits=244, L=L, N=N, mu=48, r_FRI=20,
                                grinding=20)
        assert terms.consistency < terms.per_round
        assert terms.dominant != "consistency"


def test_a_narrow_field_moves_the_dominant_term_to_the_bad_beta_union_bound():
    # The bad-beta term is the one mu cannot tighten; only a wider field, a
    # smaller domain, or a more conservative regime moves it.
    narrow = composed_margin(field_bits=64, L=2 ** 20, N=2 ** 24, mu=48,
                             r_FRI=20, grinding=20)
    wide = composed_margin(field_bits=244, L=2 ** 20, N=2 ** 24, mu=48,
                           r_FRI=20, grinding=20)
    assert narrow.dominant == "bad_beta"
    assert wide.dominant == "per_round"
    assert narrow.total < wide.total


def test_margin_terms_records_the_grinding_it_was_given():
    terms = composed_margin(field_bits=128, L=2 ** 16, N=2 ** 20, mu=40,
                            r_FRI=16, grinding=17)
    assert terms.grinding == 17
