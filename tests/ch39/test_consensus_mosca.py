"""Tests for the consensus-surface Mosca-window calculator."""

import pytest

from consensus_staking import consensus_mosca as cm


# ---- Constants -----------------------------------------------------


def test_strand_consensus_anchor_matches_ch36_fixture(strand_consensus_xy):
    """The module's STRAND_CONSENSUS_X and STRAND_CONSENSUS_Y match the fixture."""
    X, Y = strand_consensus_xy
    assert cm.STRAND_CONSENSUS_X == X
    assert cm.STRAND_CONSENSUS_Y == Y


def test_cadence_names_carry_four_options():
    """The four cadence names are the chapter's fixed taxonomy."""
    expected = (
        "per-epoch",
        "every-N-epochs",
        "every-N-validator-rotations",
        "hard-fork-trigger",
    )
    assert cm.CADENCE_NAMES == expected


# ---- breach_years() arithmetic --------------------------------------


def test_breach_years_clears_under_mid_2040():
    """Under X=2, Y=1, Z=14 the breach window is -11 (cleared)."""
    assert cm.breach_years(2, 1, 14) == -11


def test_breach_years_breaches_under_aggressive():
    """Under X=2, Y=1, Z=0 the breach window is +3 years."""
    assert cm.breach_years(2, 1, 0) == 3


def test_breach_years_at_boundary_is_zero(strand_consensus_xy):
    """X + Y == Z is the boundary case; breach_years returns 0."""
    X, Y = strand_consensus_xy
    Z = X + Y
    assert cm.breach_years(X, Y, Z) == 0


def test_breach_years_rejects_negative():
    with pytest.raises(AssertionError):
        cm.breach_years(-1, 1, 1)


# ---- cadence_options() ----------------------------------------------


def test_cadence_options_returns_four_records(strand_consensus_xy):
    """Every (X, Y, Z) call returns exactly the four cadence records."""
    X, Y = strand_consensus_xy
    out = cm.cadence_options(X, Y, 9)
    assert set(out.keys()) == set(cm.CADENCE_NAMES)


def test_cadence_labels_are_pinned_per_cadence(strand_consensus_xy):
    """Each cadence's name, cost label and rationale, pinned by identity.

    The suite reads ``feasible`` and ``rotation_interval_years`` and
    nothing else, so the three label fields were free to move between
    records. The cost ordering is what ``recommend_cadence`` documents
    as its preference order, and a swap of ``medium`` and
    ``medium-high`` reverses it while every existing test stays green,
    because every-N-epochs and every-N-validator-rotations match on
    feasibility and interval and differ only in cost.
    """
    X, Y = strand_consensus_xy
    options = cm.cadence_options(X, Y, 2)
    expected_cost = {
        "per-epoch": "low",
        "every-N-epochs": "medium",
        "every-N-validator-rotations": "medium-high",
        "hard-fork-trigger": "high",
    }
    assert {n: o["operational_cost"] for n, o in options.items()} == expected_cost
    assert {n: o["name"] for n, o in options.items()} == {n: n for n in cm.CADENCE_NAMES}

    tokens = {
        "per-epoch": "rotate every epoch alongside the validator-set turnover",
        "every-N-epochs": "rotate every N epochs",
        "every-N-validator-rotations": "rotate alongside validator-set exit-and-entry",
        "hard-fork-trigger": "rotate at a named hard-fork event",
    }
    for name, token in tokens.items():
        assert token in options[name]["rationale"]
    for token in tokens.values():
        assert sum(token in o["rationale"] for o in options.values()) == 1


def test_per_epoch_feasible_only_when_no_breach(strand_consensus_xy):
    """per-epoch feasibility requires X + Y <= Z."""
    X, Y = strand_consensus_xy
    feasible_no_breach = cm.cadence_options(X, Y, 14)["per-epoch"]["feasible"]
    breached = cm.cadence_options(X, Y, 0)["per-epoch"]["feasible"]
    assert feasible_no_breach is True
    assert breached is False


def test_every_n_epochs_feasible_with_positive_safe_window(strand_consensus_xy):
    """every-N-epochs is feasible whenever Z - Y >= 1 and there is a breach.

    Under the Strand consensus anchor (X=2, Y=1), Z=2 produces breach=1
    and safe_window=1; the every-N-epochs cadence becomes feasible.
    """
    X, Y = strand_consensus_xy
    out = cm.cadence_options(X, Y, 2)
    assert out["every-N-epochs"]["feasible"] is True


def test_every_n_epochs_infeasible_when_safe_window_collapses(strand_consensus_xy):
    """every-N-epochs is infeasible when Z <= Y."""
    X, Y = strand_consensus_xy
    out = cm.cadence_options(X, Y, 0)
    assert out["every-N-epochs"]["feasible"] is False


def test_hard_fork_trigger_is_always_feasible(strand_consensus_xy):
    """hard-fork-trigger is the always-feasible fallback."""
    X, Y = strand_consensus_xy
    for Z in (0, 1, 5, 9, 14):
        out = cm.cadence_options(X, Y, Z)
        assert out["hard-fork-trigger"]["feasible"] is True


# ---- recommend_cadence() shape and decisions ------------------------


def test_recommend_cadence_returns_eight_keys(strand_consensus_xy):
    """The recommendation dict carries eight pedagogical fields."""
    X, Y = strand_consensus_xy
    rec = cm.recommend_cadence(X, Y, 9)
    expected_keys = {
        "X",
        "Y",
        "Z",
        "breach_years",
        "safe_window_years",
        "recommendation",
        "rotation_interval_years",
        "options",
    }
    assert set(rec.keys()) == expected_keys


def test_recommend_under_aggressive_z_is_hard_fork_trigger(
    strand_consensus_xy, mosca_z_values
):
    """Under Z = 0 the safe window collapses; recommendation is hard-fork-trigger."""
    X, Y = strand_consensus_xy
    Z = mosca_z_values["aggressive"]
    rec = cm.recommend_cadence(X, Y, Z)
    assert rec["recommendation"] == "hard-fork-trigger"
    assert rec["rotation_interval_years"] == 0


def test_recommend_under_narrow_z_is_every_n_epochs(
    strand_consensus_xy, mosca_z_values
):
    """Under Z = 2 the recommendation is every-N-epochs at N = Z - Y = 1.

    The canonical Ch 36 Z scenarios (Z=9, Z=14) both clear the Mosca
    window for the consensus surface (X=2, Y=1); the chapter's
    ``narrow`` scenario at Z=2 is the load-bearing breach example.
    """
    X, Y = strand_consensus_xy
    Z = mosca_z_values["narrow"]
    rec = cm.recommend_cadence(X, Y, Z)
    assert rec["recommendation"] == "every-N-epochs"
    assert rec["rotation_interval_years"] == Z - Y


def test_recommend_under_ncsc_z_clears_to_per_epoch(
    strand_consensus_xy, mosca_z_values
):
    """Under Z = 9 the consensus surface clears the Mosca window; per-epoch."""
    X, Y = strand_consensus_xy
    Z = mosca_z_values["ncsc_2035"]
    rec = cm.recommend_cadence(X, Y, Z)
    assert rec["recommendation"] == "per-epoch"
    assert rec["breach_years"] < 0


def test_recommend_under_mid_2040_z_is_per_epoch(
    strand_consensus_xy, mosca_z_values
):
    """Under Z = 14 the surface clears the Mosca window; per-epoch."""
    X, Y = strand_consensus_xy
    Z = mosca_z_values["mid_2040"]
    rec = cm.recommend_cadence(X, Y, Z)
    assert rec["recommendation"] == "per-epoch"
    assert rec["rotation_interval_years"] == 0


def test_recommend_under_boundary_clears(strand_consensus_xy):
    """X + Y = Z is treated as cleared; recommendation drops to per-epoch."""
    X, Y = strand_consensus_xy
    Z = X + Y
    rec = cm.recommend_cadence(X, Y, Z)
    assert rec["recommendation"] == "per-epoch"


# ---- evaluate() default-anchor wiring ------------------------------


def test_evaluate_default_anchor_matches_strand_consensus(strand_consensus_xy):
    """evaluate(Z) defaults to the Strand consensus-surface (X=2, Y=1)."""
    X, Y = strand_consensus_xy
    rec = cm.evaluate(9)
    assert rec["X"] == X
    assert rec["Y"] == Y


def test_evaluate_threads_recommendation_under_three_z_scenarios(
    mosca_z_values,
):
    """evaluate(Z) returns the same recommendation as recommend_cadence at Strand X, Y."""
    for Z in mosca_z_values.values():
        rec = cm.evaluate(Z)
        expected = cm.recommend_cadence(
            cm.STRAND_CONSENSUS_X, cm.STRAND_CONSENSUS_Y, Z
        )
        assert rec["recommendation"] == expected["recommendation"]
        assert rec["breach_years"] == expected["breach_years"]


def test_evaluate_accepts_alternate_x_y():
    """A caller can pass an alternate X or Y to model a different chain."""
    rec = cm.evaluate(9, X=5, Y=2)
    assert rec["X"] == 5
    assert rec["Y"] == 2
