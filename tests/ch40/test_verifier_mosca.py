"""Tests for the on-chain-verifier-surface Mosca-window calculator."""

import pytest

from zk_rollups import verifier_mosca as vm


# ---- Constants and scenario shape -------------------------------------


def test_strand_verifier_anchor_is_three_two():
    """Strand on-chain-verifier surface anchor: X=3, Y=2 from the Ch 36 fixture."""
    assert vm.STRAND_VERIFIER_X == 3
    assert vm.STRAND_VERIFIER_Y == 2


def test_scenario_z_values_carry_three_named_scenarios(mosca_z_scenarios):
    """SCENARIO_Z_VALUES matches the conftest mosca_z_scenarios fixture."""
    assert vm.SCENARIO_Z_VALUES == mosca_z_scenarios


def test_cadence_names_carry_four_options():
    """CADENCE_NAMES includes per-rollup-cycle through hard-fork-trigger."""
    assert vm.CADENCE_NAMES == (
        "per-rollup-cycle",
        "every-N-rollup-cycles",
        "governance-trigger",
        "hard-fork-trigger",
    )


# ---- breach_years arithmetic ------------------------------------------


def test_breach_years_strand_with_z_equals_x_plus_y_is_zero():
    """X + Y = 5 with Z = 5 produces breach = 0 (cleared per strict-inequality)."""
    assert vm.breach_years(3, 2, 5) == 0


def test_breach_years_positive_when_x_plus_y_exceeds_z():
    """X + Y > Z gives positive breach."""
    assert vm.breach_years(3, 2, 4) == 1
    assert vm.breach_years(3, 2, 0) == 5


def test_breach_years_negative_when_z_exceeds_x_plus_y():
    """Z > X + Y gives negative breach (cleared with margin)."""
    assert vm.breach_years(3, 2, 9) == -4


def test_breach_years_rejects_negative_inputs():
    with pytest.raises(AssertionError):
        vm.breach_years(-1, 2, 5)
    with pytest.raises(AssertionError):
        vm.breach_years(3, -1, 5)
    with pytest.raises(AssertionError):
        vm.breach_years(3, 2, -1)


# ---- cadence_options behavior -----------------------------------------


def test_cadence_options_returns_four_named_options():
    """The dict carries the four cadence names."""
    options = vm.cadence_options(3, 2, 9)
    assert set(options.keys()) == set(vm.CADENCE_NAMES)


def test_governance_trigger_feasible_only_when_no_breach():
    """Governance-trigger requires X + Y <= Z."""
    assert vm.cadence_options(3, 2, 9)["governance-trigger"]["feasible"] is True
    assert vm.cadence_options(3, 2, 4)["governance-trigger"]["feasible"] is False


def test_every_n_cycles_feasible_only_with_positive_safe_window():
    """Every-N-rollup-cycles needs Z > Y and a breach."""
    assert vm.cadence_options(3, 2, 4)["every-N-rollup-cycles"]["feasible"] is True
    # Z=2 means Y=Z so safe_window = 0; not feasible
    assert vm.cadence_options(3, 2, 2)["every-N-rollup-cycles"]["feasible"] is False


def test_hard_fork_trigger_always_feasible():
    """Hard-fork-trigger is the always-feasible fallback."""
    for Z in (0, 1, 2, 5, 9, 13):
        assert vm.cadence_options(3, 2, Z)["hard-fork-trigger"]["feasible"] is True


def test_per_rollup_cycle_always_feasible_but_prohibitive():
    """Per-rollup-cycle is technically feasible but operationally prohibitive."""
    for Z in (0, 1, 2, 5, 9, 13):
        opt = vm.cadence_options(3, 2, Z)["per-rollup-cycle"]
        assert opt["feasible"] is True
        assert opt["operational_cost"] == "prohibitive"


# ---- recommend_cadence behavior ---------------------------------------


def test_recommend_cadence_clears_under_central_z(strand_verifier_xy):
    """Z=9 clears the Strand on-chain-verifier surface; recommendation is governance-trigger."""
    X, Y = strand_verifier_xy
    out = vm.recommend_cadence(X, Y, 9)
    assert out["breach_years"] == -4
    assert out["recommendation"] == "governance-trigger"


def test_recommend_cadence_uses_every_n_under_narrow_z(strand_verifier_xy):
    """Z=4 forces every-N-rollup-cycles."""
    X, Y = strand_verifier_xy
    out = vm.recommend_cadence(X, Y, 4)
    assert out["breach_years"] == 1
    assert out["recommendation"] == "every-N-rollup-cycles"
    assert out["rotation_interval_years"] == 2  # safe_window = Z - Y = 4 - 2


def test_recommend_cadence_falls_to_hard_fork_when_z_below_y(strand_verifier_xy):
    """Z <= Y: no positive safe window; falls to hard-fork-trigger."""
    X, Y = strand_verifier_xy
    out = vm.recommend_cadence(X, Y, 1)
    assert out["recommendation"] == "hard-fork-trigger"


def test_recommend_cadence_returns_breach_and_safe_window(strand_verifier_xy):
    """The recommendation envelope includes breach and safe_window for the chapter table."""
    X, Y = strand_verifier_xy
    out = vm.recommend_cadence(X, Y, 9)
    assert "breach_years" in out
    assert "safe_window_years" in out


def test_recommend_cadence_includes_full_options_dict(strand_verifier_xy):
    """The recommendation envelope also carries the full options dict."""
    X, Y = strand_verifier_xy
    out = vm.recommend_cadence(X, Y, 9)
    assert set(out["options"].keys()) == set(vm.CADENCE_NAMES)


# ---- evaluate (Strand-anchored convenience) ---------------------------


def test_evaluate_threads_strand_anchor():
    """evaluate(Z) defaults to the Strand X=3 and Y=2 anchor."""
    out = vm.evaluate(9)
    assert out["X"] == 3
    assert out["Y"] == 2
    assert out["recommendation"] == "governance-trigger"


def test_evaluate_accepts_alternate_anchor():
    """The caller can override X and Y to model a different rollup."""
    out = vm.evaluate(9, X=5, Y=3)
    assert out["X"] == 5
    assert out["Y"] == 3


# ---- evaluate_named_scenario shorthand --------------------------------


def test_evaluate_narrow_yields_every_n_rollup_cycles():
    """Z=4 (narrow) breaches: recommendation is every-N-rollup-cycles."""
    out = vm.evaluate_named_scenario("narrow")
    assert out["Z"] == 4
    assert out["recommendation"] == "every-N-rollup-cycles"


def test_evaluate_central_yields_governance_trigger():
    """Z=9 (central) clears: recommendation is governance-trigger."""
    out = vm.evaluate_named_scenario("central")
    assert out["Z"] == 9
    assert out["recommendation"] == "governance-trigger"


def test_evaluate_wide_yields_governance_trigger():
    """Z=13 (wide) clears comfortably: recommendation is governance-trigger."""
    out = vm.evaluate_named_scenario("wide")
    assert out["Z"] == 13
    assert out["recommendation"] == "governance-trigger"


def test_evaluate_named_scenario_rejects_unknown_name():
    with pytest.raises(AssertionError):
        vm.evaluate_named_scenario("aggressive")


# ---- CadenceOption label fields ---------------------------------------
#
# Only per-rollup-cycle's operational_cost was asserted, so the other
# three could permute and reverse the preference order recommend_cadence
# documents. Each option's own `name` field was also free of its dict key,
# and all four rationales were interchangeable.

CADENCE_COST = {
    "per-rollup-cycle": "prohibitive",
    "every-N-rollup-cycles": "medium",
    "governance-trigger": "low",
    "hard-fork-trigger": "high",
}

CADENCE_RATIONALE_TOKENS = {
    "per-rollup-cycle": "every rollup cycle",
    "every-N-rollup-cycles": "N tuned",
    "governance-trigger": "named governance event",
    "hard-fork-trigger": "hard-fork event",
}


def test_operational_cost_is_pinned_per_cadence():
    """recommend_cadence documents a cheapest-first order; pin the labels."""
    options = vm.cadence_options(3, 2, 9)
    for name, cost in CADENCE_COST.items():
        assert options[name]["operational_cost"] == cost, name


def test_operational_costs_are_four_distinct_labels():
    """The uniqueness half: no two cadences may share a cost label."""
    options = vm.cadence_options(3, 2, 9)
    costs = [options[n]["operational_cost"] for n in vm.CADENCE_NAMES]
    assert len(set(costs)) == 4


def test_each_option_name_matches_its_key():
    """An option's own name field cannot disagree with the dict key."""
    for Z in (2, 4, 9, 13):
        for key, option in vm.cadence_options(3, 2, Z).items():
            assert option["name"] == key, (Z, key)


def test_each_cadence_rationale_names_its_own_option():
    """Each rationale explains that cadence and no other."""
    options = vm.cadence_options(3, 2, 9)
    for name, token in CADENCE_RATIONALE_TOKENS.items():
        assert token in options[name]["rationale"], name


def test_cadence_rationale_tokens_are_unique():
    """The uniqueness half for the rationales."""
    options = vm.cadence_options(3, 2, 9)
    rationales = [options[n]["rationale"] for n in vm.CADENCE_NAMES]
    for token in CADENCE_RATIONALE_TOKENS.values():
        assert sum(token in r for r in rationales) == 1, token
