"""Tests for governance.governance_mosca."""

from governance import governance_mosca as gm


def test_strand_anchor_matches_ch36_fixture(strand_governance_xy):
    assert (gm.STRAND_GOVERNANCE_X, gm.STRAND_GOVERNANCE_Y) == strand_governance_xy


def test_scenario_z_values_match_fixture(mosca_z_scenarios):
    assert gm.SCENARIO_Z_VALUES == mosca_z_scenarios


def test_cadence_names_lists_four_cadences():
    assert gm.CADENCE_NAMES == (
        "per-vote-cycle",
        "every-N-vote-cycles",
        "governance-trigger",
        "hard-fork-trigger",
    )


def test_breach_years_at_strand_under_narrow_is_one():
    # X=4, Y=3, Z=6: breach = 7 - 6 = 1 year.
    breach = gm.breach_years(
        gm.STRAND_GOVERNANCE_X, gm.STRAND_GOVERNANCE_Y, 6
    )
    assert breach == 1


def test_breach_years_at_strand_under_central_is_negative_two():
    # X=4, Y=3, Z=9: breach = 7 - 9 = -2 (cleared by two years).
    breach = gm.breach_years(
        gm.STRAND_GOVERNANCE_X, gm.STRAND_GOVERNANCE_Y, 9
    )
    assert breach == -2


def test_breach_years_at_strand_under_wide_is_negative_six():
    # X=4, Y=3, Z=13: breach = 7 - 13 = -6.
    breach = gm.breach_years(
        gm.STRAND_GOVERNANCE_X, gm.STRAND_GOVERNANCE_Y, 13
    )
    assert breach == -6


def test_breach_years_at_boundary_is_zero():
    # Boundary X + Y == Z: breach = 0 (treated as cleared).
    breach = gm.breach_years(4, 3, 7)
    assert breach == 0


def test_breach_years_rejects_negative_inputs():
    import pytest

    with pytest.raises(AssertionError):
        gm.breach_years(-1, 3, 7)
    with pytest.raises(AssertionError):
        gm.breach_years(4, -1, 7)
    with pytest.raises(AssertionError):
        gm.breach_years(4, 3, -1)


def test_cadence_options_returns_four_cadences():
    options = gm.cadence_options(4, 3, 9)
    assert set(options.keys()) == set(gm.CADENCE_NAMES)


def test_cadence_options_per_vote_always_feasible():
    for Z in (4, 6, 9, 13, 20):
        options = gm.cadence_options(4, 3, Z)
        assert options["per-vote-cycle"]["feasible"] is True


def test_cadence_options_per_vote_always_prohibitive_cost():
    for Z in (4, 6, 9, 13, 20):
        options = gm.cadence_options(4, 3, Z)
        assert options["per-vote-cycle"]["operational_cost"] == "prohibitive"


def test_cadence_options_governance_trigger_feasible_only_when_cleared():
    # Cleared (Z >= X+Y == 7): governance-trigger feasible.
    assert gm.cadence_options(4, 3, 9)["governance-trigger"]["feasible"] is True
    assert gm.cadence_options(4, 3, 13)["governance-trigger"]["feasible"] is True
    # Boundary X+Y==Z: feasible (cleared per strict inequality).
    assert gm.cadence_options(4, 3, 7)["governance-trigger"]["feasible"] is True
    # Breach (Z < X+Y): infeasible.
    assert gm.cadence_options(4, 3, 6)["governance-trigger"]["feasible"] is False


def test_cadence_options_every_n_feasible_only_under_breach_with_safe_window():
    # Breach with safe window: feasible.
    assert gm.cadence_options(4, 3, 6)["every-N-vote-cycles"]["feasible"] is True
    # No breach: infeasible (no breach means no cadence-driven rotation).
    assert (
        gm.cadence_options(4, 3, 9)["every-N-vote-cycles"]["feasible"] is False
    )
    # Z <= Y: no positive safe window, so every-N is infeasible.
    assert (
        gm.cadence_options(4, 3, 3)["every-N-vote-cycles"]["feasible"] is False
    )


def test_cadence_options_hard_fork_always_feasible():
    for Z in (1, 3, 6, 9, 13):
        options = gm.cadence_options(4, 3, Z)
        assert options["hard-fork-trigger"]["feasible"] is True


def test_recommend_cadence_at_strand_narrow_is_every_n():
    rec = gm.recommend_cadence(4, 3, 6)
    assert rec["recommendation"] == "every-N-vote-cycles"
    assert rec["breach_years"] == 1
    assert rec["safe_window_years"] == 3


def test_recommend_cadence_at_strand_central_is_governance_trigger():
    rec = gm.recommend_cadence(4, 3, 9)
    assert rec["recommendation"] == "governance-trigger"
    assert rec["breach_years"] == -2
    assert rec["safe_window_years"] == 6


def test_recommend_cadence_at_strand_wide_is_governance_trigger():
    rec = gm.recommend_cadence(4, 3, 13)
    assert rec["recommendation"] == "governance-trigger"
    assert rec["breach_years"] == -6
    assert rec["safe_window_years"] == 10


def test_recommend_cadence_when_z_below_y_is_hard_fork():
    rec = gm.recommend_cadence(4, 3, 2)
    assert rec["recommendation"] == "hard-fork-trigger"
    assert rec["safe_window_years"] == 0


def test_recommend_cadence_returns_full_envelope():
    rec = gm.recommend_cadence(4, 3, 9)
    for key in (
        "X",
        "Y",
        "Z",
        "breach_years",
        "safe_window_years",
        "recommendation",
        "rotation_interval_years",
        "options",
    ):
        assert key in rec


def test_recommend_cadence_rotation_interval_under_breach_equals_safe_window():
    # Breach with safe window: rotation_interval_years equals
    # safe_window_years (the every-N-vote-cycles default).
    rec = gm.recommend_cadence(4, 3, 6)
    assert rec["rotation_interval_years"] == rec["safe_window_years"]


def test_recommend_cadence_rotation_interval_under_clear_is_zero():
    # Cleared: rotation_interval_years is zero (governance-trigger).
    rec = gm.recommend_cadence(4, 3, 9)
    assert rec["rotation_interval_years"] == 0


def test_evaluate_uses_strand_anchor_by_default():
    rec = gm.evaluate(9)
    assert rec["X"] == gm.STRAND_GOVERNANCE_X
    assert rec["Y"] == gm.STRAND_GOVERNANCE_Y


def test_evaluate_overrides_xy_when_provided():
    rec = gm.evaluate(9, X=2, Y=1)
    assert rec["X"] == 2
    assert rec["Y"] == 1


def test_evaluate_named_scenario_narrow():
    rec = gm.evaluate_named_scenario("narrow")
    assert rec["Z"] == 6
    assert rec["recommendation"] == "every-N-vote-cycles"


def test_evaluate_named_scenario_central():
    rec = gm.evaluate_named_scenario("central")
    assert rec["Z"] == 9
    assert rec["recommendation"] == "governance-trigger"


def test_evaluate_named_scenario_wide():
    rec = gm.evaluate_named_scenario("wide")
    assert rec["Z"] == 13
    assert rec["recommendation"] == "governance-trigger"


def test_evaluate_named_scenario_rejects_unknown():
    import pytest

    with pytest.raises(AssertionError):
        gm.evaluate_named_scenario("mid-2040")


def test_options_have_consistent_keys():
    options = gm.cadence_options(4, 3, 9)
    for option in options.values():
        for key in (
            "name",
            "feasible",
            "rotation_interval_years",
            "operational_cost",
            "rationale",
        ):
            assert key in option


def test_operational_cost_values_are_valid():
    valid = {"low", "medium", "high", "prohibitive"}
    for Z in (4, 6, 7, 9, 13):
        options = gm.cadence_options(4, 3, Z)
        for option in options.values():
            assert option["operational_cost"] in valid


def test_rationale_is_non_empty_for_all_cadences():
    options = gm.cadence_options(4, 3, 9)
    for option in options.values():
        assert isinstance(option["rationale"], str)
        assert len(option["rationale"]) > 0


def test_cadence_option_name_matches_its_key():
    # Each option's own name field is the key it is filed under.
    # Nothing else reads that field, so without this a per-vote-cycle
    # record can call itself governance-trigger.
    for Z in (2, 6, 9, 13):
        options = gm.cadence_options(4, 3, Z)
        for key, option in options.items():
            assert option["name"] == key, (
                f"option filed under {key!r} names itself {option['name']!r}"
            )


def test_operational_cost_is_pinned_per_cadence():
    # recommend_cadence documents a cheapest-first preference order and
    # nothing asserted the costs it orders on. The four labels are
    # distinct, so a permutation cannot satisfy this by two cadences
    # sharing a label.
    expected = {
        "per-vote-cycle": "prohibitive",
        "every-N-vote-cycles": "medium",
        "governance-trigger": "low",
        "hard-fork-trigger": "high",
    }
    for Z in (2, 6, 9, 13):
        options = gm.cadence_options(4, 3, Z)
        for name, cost in expected.items():
            assert options[name]["operational_cost"] == cost, (
                f"{name!r} should cost {cost!r}, "
                f"got {options[name]['operational_cost']!r}"
            )
    assert len(set(expected.values())) == len(expected)


def test_recommendation_is_the_cheapest_feasible_cadence():
    # The docstring's preference order read off the cost labels rather
    # than restated: among the feasible options the recommendation is
    # one of the cheapest.
    rank = {"low": 0, "medium": 1, "high": 2, "prohibitive": 3}
    for Z in (2, 3, 6, 7, 9, 13):
        rec = gm.recommend_cadence(4, 3, Z)
        options = rec["options"]
        feasible = [o for o in options.values() if o["feasible"]]
        cheapest = min(rank[o["operational_cost"]] for o in feasible)
        chosen = options[rec["recommendation"]]
        assert chosen["feasible"] is True
        assert rank[chosen["operational_cost"]] == cheapest, (
            f"at Z={Z} the recommendation {rec['recommendation']!r} costs "
            f"{chosen['operational_cost']!r} where a cheaper option is feasible"
        )


def test_cadence_rationales_name_their_own_trigger_and_are_distinct():
    tokens = {
        "per-vote-cycle": "every governance vote",
        "every-N-vote-cycles": "every N governance votes",
        "governance-trigger": "named governance event",
        "hard-fork-trigger": "named L1 hard-fork event",
    }
    options = gm.cadence_options(4, 3, 9)
    seen = set()
    for name, token in tokens.items():
        rationale = options[name]["rationale"]
        assert token in rationale, (
            f"{name!r} should mention {token!r}, got {rationale!r}"
        )
        seen.add(rationale)
    assert len(seen) == 4, "every cadence carries a distinct rationale"
