"""Tests for ``migration_program.risk_rollup``."""

import pytest

from migration_program import (
    DEFAULT_PQRA_WEIGHTS,
    PQRA_DOMAINS,
    migration_urgency,
)


def test_default_weights_sum_to_one() -> None:
    assert abs(sum(DEFAULT_PQRA_WEIGHTS.values()) - 1.0) < 1e-9


def test_default_weights_cover_every_domain() -> None:
    assert set(DEFAULT_PQRA_WEIGHTS) == set(PQRA_DOMAINS)


def test_each_domain_carries_its_own_pqra_weight() -> None:
    """Pin every domain to its own weight, not just the total.

    The two tests above both survive a permutation of the weights: the
    sum is invariant under one, and the key set is unchanged by one. So
    two domains could swap weights, the package would disagree with the
    rubric it claims to implement, real scores would move, and all of
    it would pass. The values below are the Encryptorium PQRA v1.0
    rubric's own seven domain weights, which is what makes this test an
    outside check rather than a restatement of the module.
    """
    assert DEFAULT_PQRA_WEIGHTS == {
        "inventory": 0.20,
        "data_sensitivity": 0.15,
        "standards_compliance": 0.10,
        "migration_readiness": 0.20,
        "vendor_supply_chain": 0.15,
        "timeline_urgency": 0.10,
        "governance_policy": 0.10,
    }


def test_quantum_safe_entries_score_zero(four_touchpoint_cbom: list[dict]) -> None:
    ranked = migration_urgency(four_touchpoint_cbom)
    scores = {name: score for name, score in ranked}
    assert scores["tls_endpoint_api"] == 0.0
    assert scores["jwt_signing"] == 0.0


def test_grover_only_entries_rank_above_quantum_safe(four_touchpoint_cbom: list[dict]) -> None:
    ranked = migration_urgency(four_touchpoint_cbom)
    names = [name for name, _ in ranked]
    # password_hashing has worse data_sensitivity (2 vs 3) and
    # worse migration_readiness (3 vs 4), so it outranks webhook_hmac.
    assert names[0] == "password_hashing"
    assert names[1] == "webhook_hmac"
    assert set(names[2:]) == {"tls_endpoint_api", "jwt_signing"}


def test_vulnerable_public_outranks_grover_only(second_wave_cbom: list[dict]) -> None:
    ranked = migration_urgency(second_wave_cbom)
    names = [name for name, _ in ranked]
    assert names[0] == "legacy_api_gateway"
    # webhook_hmac (grover-only, internal) comes next
    assert names[1] == "webhook_hmac"
    assert names[2] == "tls_endpoint_api"


def test_weights_not_summing_to_one_rejected(four_touchpoint_cbom: list[dict]) -> None:
    bad_weights = {d: 0.1 for d in PQRA_DOMAINS}  # sums to 0.7
    with pytest.raises(ValueError, match="sum to 1.0"):
        migration_urgency(four_touchpoint_cbom, bad_weights)


def test_unknown_quantum_status_rejected() -> None:
    tp = [
        {
            "name": "bad",
            "quantum_status": "possibly-vulnerable",
            "exposure": "public",
            "readiness": {d: 3 for d in PQRA_DOMAINS},
        }
    ]
    with pytest.raises(ValueError, match="unknown quantum_status"):
        migration_urgency(tp)


def test_unknown_exposure_rejected() -> None:
    tp = [
        {
            "name": "bad",
            "quantum_status": "vulnerable",
            "exposure": "dmz",
            "readiness": {d: 3 for d in PQRA_DOMAINS},
        }
    ]
    with pytest.raises(ValueError, match="unknown exposure"):
        migration_urgency(tp)


def test_missing_readiness_domain_rejected() -> None:
    readiness = {d: 3 for d in PQRA_DOMAINS}
    del readiness["migration_readiness"]
    tp = [
        {
            "name": "bad",
            "quantum_status": "vulnerable",
            "exposure": "public",
            "readiness": readiness,
        }
    ]
    with pytest.raises(ValueError, match="missing a readiness score"):
        migration_urgency(tp)


def test_readiness_score_out_of_range_rejected() -> None:
    readiness = {d: 3 for d in PQRA_DOMAINS}
    readiness["inventory"] = 7
    tp = [
        {
            "name": "bad",
            "quantum_status": "vulnerable",
            "exposure": "public",
            "readiness": readiness,
        }
    ]
    with pytest.raises(ValueError, match="out of"):
        migration_urgency(tp)


def test_maximum_priority_is_24() -> None:
    # Public vulnerable with every readiness score at 1:
    # 3 * 2 * sum((5 - 1) * w) = 6 * 4 = 24 when weights sum to 1.
    tp = [
        {
            "name": "worst_case",
            "quantum_status": "vulnerable",
            "exposure": "public",
            "readiness": {d: 1 for d in PQRA_DOMAINS},
        }
    ]
    ranked = migration_urgency(tp)
    assert len(ranked) == 1
    assert ranked[0][0] == "worst_case"
    assert ranked[0][1] == pytest.approx(24.0)


def test_ties_break_alphabetically() -> None:
    base = {
        "quantum_status": "grover-only",
        "exposure": "internal",
        "readiness": {d: 3 for d in PQRA_DOMAINS},
    }
    tp = [dict(base, name="zeta"), dict(base, name="alpha"), dict(base, name="mu")]
    ranked = migration_urgency(tp)
    assert [name for name, _ in ranked] == ["alpha", "mu", "zeta"]


def test_empty_input_returns_empty_list() -> None:
    assert migration_urgency([]) == []
