"""Tests for ``migration_program.phase_gate``."""

import pytest

from migration_program import (
    PHASE_EXIT_CRITERIA,
    PhaseGateResult,
    check,
)


def test_four_phases_defined() -> None:
    assert set(PHASE_EXIT_CRITERIA) == {
        "discovery",
        "first-wave",
        "broad-rollout",
        "end-of-migration",
    }


def test_discovery_gate_all_green_passes(discovery_gate_record: dict) -> None:
    result = check("discovery", discovery_gate_record)
    assert isinstance(result, PhaseGateResult)
    assert result.phase == "discovery"
    assert result.passed is True
    assert result.missing == ()
    assert set(result.met) == set(PHASE_EXIT_CRITERIA["discovery"])


def test_first_wave_with_missing_drill_fails(first_wave_gate_record: dict) -> None:
    result = check("first-wave", first_wave_gate_record)
    assert result.passed is False
    assert result.missing == ("rollback_drill_completed",)
    assert set(result.met) == {"public_vulnerable_migrated", "jwt_signing_migrated"}


def test_missing_key_counts_as_unmet() -> None:
    gate = {"cbom_complete": True}  # pqra_scored and owners_assigned are missing
    result = check("discovery", gate)
    assert result.passed is False
    assert result.missing == ("pqra_scored", "owners_assigned")


def test_false_counts_as_unmet() -> None:
    gate = {"cbom_complete": False, "pqra_scored": True, "owners_assigned": True}
    result = check("discovery", gate)
    assert result.passed is False
    assert result.missing == ("cbom_complete",)


def test_non_true_value_counts_as_unmet() -> None:
    # Only the literal ``True`` is treated as a met criterion.
    gate = {
        "cbom_complete": "yes",
        "pqra_scored": 1,
        "owners_assigned": True,
    }
    result = check("discovery", gate)
    assert result.passed is False
    assert set(result.missing) == {"cbom_complete", "pqra_scored"}


def test_unknown_phase_rejected() -> None:
    with pytest.raises(ValueError, match="unknown phase"):
        check("zeroth-wave", {})


def test_empty_gate_record_fails_every_criterion() -> None:
    result = check("broad-rollout", {})
    assert result.passed is False
    assert result.missing == PHASE_EXIT_CRITERIA["broad-rollout"]
    assert result.met == ()


def test_end_of_migration_passes_with_all_green() -> None:
    gate = {
        "classical_retired": True,
        "pq_only_mode": True,
        "post_migration_review_signed": True,
    }
    result = check("end-of-migration", gate)
    assert result.passed is True


def test_missing_preserves_defined_order() -> None:
    # Only ``pq_only_mode`` met; the other two should appear in
    # the declared order, not insertion order of the record.
    gate = {
        "pq_only_mode": True,
        "post_migration_review_signed": False,
        "classical_retired": False,
    }
    result = check("end-of-migration", gate)
    assert result.missing == ("classical_retired", "post_migration_review_signed")
