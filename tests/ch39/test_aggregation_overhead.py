"""Tests for the per-validator-set byte-budget calculator."""

import math

import pytest

from consensus_staking import aggregation_overhead as ao


# ---- Constant-and-shape tests -----------------------------------------


def test_candidates_carry_the_five_named_primitives(primitives):
    """The CANDIDATES dict matches the chapter's fixed five-element set."""
    assert set(ao.CANDIDATES.keys()) == set(primitives)


def test_bls_canonical_sizes_match_ietf_draft():
    """BLS sig is 96 bytes (G2 form); pubkey is 48 bytes (G1 form)."""
    assert ao.CANDIDATES["BLS-BLS12-381"]["sig_bytes"] == 96
    assert ao.CANDIDATES["BLS-BLS12-381"]["pk_bytes"] == 48


def test_ml_dsa_65_sizes_match_fips_204_table_1():
    """ML-DSA-65: 3309-byte signature, 1952-byte public key."""
    assert ao.CANDIDATES["ML-DSA-65"]["sig_bytes"] == 3309
    assert ao.CANDIDATES["ML-DSA-65"]["pk_bytes"] == 1952


def test_slh_dsa_128s_sizes_match_fips_205_table_1():
    """SLH-DSA-128s: 7856-byte signature, 32-byte public key."""
    assert ao.CANDIDATES["SLH-DSA-128s"]["sig_bytes"] == 7856
    assert ao.CANDIDATES["SLH-DSA-128s"]["pk_bytes"] == 32


def test_fn_dsa_512_sizes_match_the_falcon_512_submission():
    """FN-DSA-512: 666-byte signature, 897-byte public key.

    These are Falcon-512's figures from the Falcon specification
    v1.2 (round-3 submission), not a FIPS 206 figure: FIPS 206 has
    published neither an initial public draft nor a final standard
    at chain-tip 2026.
    """
    assert ao.CANDIDATES["FN-DSA-512"]["sig_bytes"] == 666
    assert ao.CANDIDATES["FN-DSA-512"]["pk_bytes"] == 897


def test_threshold_ml_dsa_inherits_ml_dsa_sizes():
    """Threshold ML-DSA produces an ML-DSA-65 signature on combine."""
    assert ao.CANDIDATES["threshold-ML-DSA"]["sig_bytes"] == 3309
    assert ao.CANDIDATES["threshold-ML-DSA"]["pk_bytes"] == 1952


def test_deployment_status_is_pinned_per_candidate(primitives):
    """Each candidate's deployment status, pinned to that candidate by identity.

    Nothing else in the suite reads this field: ``evaluate`` threads it
    into its envelope and the envelope test asserts the key set rather
    than any value, so before this test the five statuses were freely
    permutable. That is not a cosmetic hole. Under a swap of the
    FN-DSA-512 and threshold-ML-DSA rows, a research-stage threshold
    construction reads as a standards-track candidate and the NIST
    candidate reads as research, which inverts the chapter's whole
    deployment-status axis.
    """
    expected = {
        "BLS-BLS12-381": "deployed-legacy",
        "ML-DSA-65": "fips-final",
        "SLH-DSA-128s": "fips-final",
        "FN-DSA-512": "pre-draft",
        "threshold-ML-DSA": "research-grade",
    }
    actual = {p: ao.CANDIDATES[p]["deployment_status"] for p in primitives}
    assert actual == expected


def test_notes_name_the_candidate_they_belong_to(primitives):
    """Each candidate's notes string carries a token unique to that candidate.

    ML-DSA-65 and SLH-DSA-128s share a deployment status, so the test
    above cannot separate them; their notes are what distinguishes the
    two rows. The uniqueness loop is what makes the per-candidate
    assertion bite: without it, two rows sharing a token would satisfy
    it under a swap.
    """
    tokens = {
        "BLS-BLS12-381": "Ethereum beacon-chain baseline",
        "ML-DSA-65": "FIPS 204 final",
        "SLH-DSA-128s": "FIPS 205 final",
        "FN-DSA-512": "FIPS 206 under development",
        "threshold-ML-DSA": "combine round",
    }
    for primitive, token in tokens.items():
        assert token in ao.CANDIDATES[primitive]["notes"]
    for token in tokens.values():
        hits = [p for p in primitives if token in ao.CANDIDATES[p]["notes"]]
        assert len(hits) == 1


def test_eth_validators_anchor_is_one_million():
    """The Ethereum mainnet 2026 anchor is the round-figure 1_000_000."""
    assert ao.ETH_VALIDATORS_2026 == 1_000_000


def test_only_bls_and_threshold_aggregate():
    """BLS and threshold-ML-DSA carry aggregates=True; the three plain PQ candidates do not."""
    assert ao.CANDIDATES["BLS-BLS12-381"]["aggregates"] is True
    assert ao.CANDIDATES["threshold-ML-DSA"]["aggregates"] is True
    assert ao.CANDIDATES["ML-DSA-65"]["aggregates"] is False
    assert ao.CANDIDATES["SLH-DSA-128s"]["aggregates"] is False
    assert ao.CANDIDATES["FN-DSA-512"]["aggregates"] is False


# ---- Participation-bitmap arithmetic ----------------------------------


def test_participation_bitmap_handles_zero_validators():
    assert ao.participation_bitmap_bytes(0) == 0


def test_participation_bitmap_pads_to_byte_boundary():
    """Eight validators fit in one byte; nine validators take two bytes."""
    assert ao.participation_bitmap_bytes(8) == 1
    assert ao.participation_bitmap_bytes(9) == 2


def test_participation_bitmap_at_one_million_validators():
    """One million validators take ceil(1e6 / 8) = 125_000 bytes of bitmap."""
    assert ao.participation_bitmap_bytes(1_000_000) == 125_000


def test_participation_bitmap_rejects_negative_input():
    with pytest.raises(AssertionError):
        ao.participation_bitmap_bytes(-1)


# ---- BLS aggregate-total arithmetic -----------------------------------


def test_bls_aggregate_total_at_one_validator():
    """One BLS validator: 96 bytes sig + 1 byte bitmap = 97 bytes."""
    assert ao.bls_aggregate_total_bytes(1) == 97


def test_bls_aggregate_total_at_one_million_validators():
    """One million BLS validators: 96 bytes sig + 125_000 bytes bitmap."""
    assert ao.bls_aggregate_total_bytes(1_000_000) == 96 + 125_000


def test_bls_aggregate_signature_size_constant_in_n():
    """The aggregate signature is 96 bytes regardless of validator count."""
    assert ao.BLS_AGGREGATE_SIG_BYTES == 96


# ---- pq_total_bytes arithmetic ----------------------------------------


def test_pq_total_for_ml_dsa_65_scales_linearly(validator_count_scenarios):
    """ML-DSA-65 produces N independent 3309-byte signatures."""
    for N in validator_count_scenarios.values():
        assert ao.pq_total_bytes("ML-DSA-65", N) == N * 3309


def test_pq_total_for_slh_dsa_128s_scales_linearly(validator_count_scenarios):
    """SLH-DSA-128s produces N independent 7856-byte signatures."""
    for N in validator_count_scenarios.values():
        assert ao.pq_total_bytes("SLH-DSA-128s", N) == N * 7856


def test_pq_total_for_fn_dsa_512_scales_linearly(validator_count_scenarios):
    """FN-DSA-512 produces N independent 666-byte signatures."""
    for N in validator_count_scenarios.values():
        assert ao.pq_total_bytes("FN-DSA-512", N) == N * 666


def test_pq_total_for_bls_routes_through_aggregate():
    """BLS at any N returns the aggregate total, not N * 96."""
    assert ao.pq_total_bytes("BLS-BLS12-381", 1_000_000) == 96 + 125_000


def test_pq_total_for_threshold_ml_dsa_collapses_signature_plus_bitmap():
    """Threshold ML-DSA returns one ML-DSA-65 signature plus a per-validator bitmap.

    A deployable threshold-PQ protocol must ship a signer set on-chain
    to attribute attestation rewards and slashing; the package adds a
    ceil(N/8)-byte participation bitmap analogous to BLS.
    """
    assert ao.pq_total_bytes("threshold-ML-DSA", 1) == 3309 + 1
    assert ao.pq_total_bytes("threshold-ML-DSA", 1_000_000) == 3309 + 125_000


def test_pq_total_rejects_unknown_primitive():
    with pytest.raises(AssertionError):
        ao.pq_total_bytes("unknown", 100)


def test_pq_total_rejects_negative_n():
    with pytest.raises(AssertionError):
        ao.pq_total_bytes("ML-DSA-65", -1)


# ---- aggregation_ratio arithmetic --------------------------------------


def test_aggregation_ratio_for_plain_pq_is_one():
    """Plain PQ candidates produce ratio 1: partial total equals output."""
    for primitive in ("ML-DSA-65", "SLH-DSA-128s", "FN-DSA-512"):
        assert ao.aggregation_ratio(primitive, 1_000) == 1.0


def test_aggregation_ratio_for_bls_grows_with_n_and_saturates_near_768():
    """BLS partial total is N * 96; aggregate total is 96 + ceil(N/8).

    At large N the bitmap dominates the denominator and the ratio
    saturates near 96 * 8 = 768. The bound is the load-bearing
    property of the function.
    """
    ratio_1k = ao.aggregation_ratio("BLS-BLS12-381", 1_000)
    ratio_1m = ao.aggregation_ratio("BLS-BLS12-381", 1_000_000)
    assert ratio_1m > ratio_1k > 1.0
    assert 750 < ratio_1m < 800


def test_aggregation_ratio_for_threshold_saturates_with_bitmap():
    """Threshold ML-DSA: at large N the bitmap dominates the output.

    Partial total is N * 3309. Output total is 3309 + ceil(N/8). At
    large N the ratio approaches 8 * 3309 = 26472. At small N the
    fixed 3309-byte signature dominates the output and the ratio is
    correspondingly smaller.
    """
    ratio_100 = ao.aggregation_ratio("threshold-ML-DSA", 100)
    ratio_1m = ao.aggregation_ratio("threshold-ML-DSA", 1_000_000)
    # Small N: 100 * 3309 / (3309 + 13) = 99.6
    assert 99 < ratio_100 < 100
    # Large N: 1M * 3309 / (3309 + 125000) = 25788
    assert 25_000 < ratio_1m < 27_000


def test_aggregation_ratio_rejects_zero_n():
    with pytest.raises(AssertionError):
        ao.aggregation_ratio("BLS-BLS12-381", 0)


# ---- evaluate() shape and values --------------------------------------


def test_evaluate_returns_nine_keys_per_primitive(primitives):
    """The evaluate dict has the nine fields the chapter's Block 1 draws on.

    The count in this test's name was eight and the set below has
    always held nine. A key-set assertion also sees no value, so it
    cannot tell which candidate produced the envelope; the two tests
    below pin the two label fields it threads.
    """
    expected_keys = {
        "primitive",
        "sig_bytes",
        "pk_bytes",
        "aggregates",
        "deployment_status",
        "validator_count",
        "per_set_bytes",
        "aggregation_ratio",
        "notes",
    }
    for primitive in primitives:
        out = ao.evaluate(primitive, N=1_000)
        assert set(out.keys()) == expected_keys


def test_evaluate_threads_the_candidates_own_labels(primitives):
    """``evaluate`` reads the label fields off the row it was asked for."""
    for primitive in primitives:
        out = ao.evaluate(primitive, N=1_000)
        assert out["primitive"] == primitive
        assert out["deployment_status"] == ao.CANDIDATES[primitive]["deployment_status"]
        assert out["notes"] == ao.CANDIDATES[primitive]["notes"]


def test_evaluate_default_n_is_eth_anchor():
    """Default validator count threads the Ethereum mainnet anchor."""
    out = ao.evaluate("ML-DSA-65")
    assert out["validator_count"] == ao.ETH_VALIDATORS_2026


def test_evaluate_factor_against_bls_at_one_million():
    """At 1M validators, ML-DSA-65 per-set is N * 3309; BLS is 96 + 125_000."""
    rows = ao.per_set_bytes_against_baseline(N=1_000_000)
    bls_total = rows["BLS-BLS12-381"]["per_set_bytes"]
    ml_dsa_total = rows["ML-DSA-65"]["per_set_bytes"]
    factor = rows["ML-DSA-65"]["factor_vs_bls"]
    assert bls_total == 96 + 125_000
    assert ml_dsa_total == 1_000_000 * 3309
    assert math.isclose(factor, ml_dsa_total / bls_total)


def test_evaluate_threshold_includes_participation_bitmap():
    """Threshold ML-DSA at 1M is one 3309-byte sig plus the 125000-byte bitmap.

    The bitmap-inclusion is what makes the threshold-PQ on-chain
    payload comparable to the BLS aggregate at the same N: both ship
    a per-validator participation set, and the bitmap dominates the
    payload at large N.
    """
    rows = ao.per_set_bytes_against_baseline(N=1_000_000)
    threshold_total = rows["threshold-ML-DSA"]["per_set_bytes"]
    bls_total = rows["BLS-BLS12-381"]["per_set_bytes"]
    assert threshold_total == 3309 + 125_000
    # 128_309 vs 125_096; threshold is slightly larger than BLS at 1M
    # because the threshold-ML-DSA signature itself is 3213 bytes
    # larger than the 96-byte BLS aggregate. The two payloads are
    # within 3 percent of each other once the bitmap is included.
    assert 1.02 < threshold_total / bls_total < 1.04


def test_evaluate_deterministic_order_across_invocations(primitives):
    """The evaluate dict's keys order matches across invocations."""
    out1 = ao.evaluate(primitives[0], N=1_000)
    out2 = ao.evaluate(primitives[0], N=1_000)
    assert list(out1.keys()) == list(out2.keys())


def test_per_set_baseline_includes_every_primitive(primitives):
    """The baseline-comparison rows cover every candidate."""
    rows = ao.per_set_bytes_against_baseline(N=1_000_000)
    assert set(rows.keys()) == set(primitives)
