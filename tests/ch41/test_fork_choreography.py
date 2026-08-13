"""Tests for governance.fork_choreography."""

from governance import fork_choreography as fc


def test_cycles_constant_lists_two_cycles(cycles):
    assert fc.CYCLES == tuple(cycles)


def test_bip_cycle_constants_are_positive():
    assert fc.BIP_PROPOSAL_REVIEW_WEEKS > 0
    assert fc.BIP_ECONOMIC_ACTOR_LEAD_WEEKS > 0


def test_acd_cycle_constants_are_positive():
    assert fc.ACD_BIWEEKLY_CADENCE_WEEKS == 2
    assert fc.ACD_PROPOSAL_REVIEW_WEEKS > 0
    assert fc.ACD_CLIENT_TEAM_RELEASE_WEEKS > 0


def test_consensus_participant_update_constant_is_positive():
    assert fc.CONSENSUS_PARTICIPANT_UPDATE_WEEKS > 0


def test_infrastructure_lead_constant_is_positive():
    assert fc.INFRASTRUCTURE_LEAD_WEEKS > 0


def test_activation_window_bitcoin_sums_three_components():
    expected = (
        fc.BIP_PROPOSAL_REVIEW_WEEKS
        + fc.BIP_ECONOMIC_ACTOR_LEAD_WEEKS
        + fc.CONSENSUS_PARTICIPANT_UPDATE_WEEKS
    )
    assert fc.activation_window_weeks("bitcoin-bip-cycle") == expected


def test_activation_window_ethereum_sums_three_components():
    expected = (
        fc.ACD_PROPOSAL_REVIEW_WEEKS
        + fc.ACD_CLIENT_TEAM_RELEASE_WEEKS
        + fc.CONSENSUS_PARTICIPANT_UPDATE_WEEKS
    )
    assert fc.activation_window_weeks("ethereum-acd-cycle") == expected


def test_activation_window_does_not_stack_infrastructure_lead():
    # Infrastructure-lead weeks run in parallel with the client-team
    # release lead time and are not added to the critical path.
    btc = fc.activation_window_weeks("bitcoin-bip-cycle")
    eth = fc.activation_window_weeks("ethereum-acd-cycle")
    assert btc != fc.INFRASTRUCTURE_LEAD_WEEKS + btc
    assert eth != fc.INFRASTRUCTURE_LEAD_WEEKS + eth


def test_activation_window_rejects_unknown_cycle():
    import pytest

    with pytest.raises(AssertionError):
        fc.activation_window_weeks("solana-rollup-cycle")


def test_evaluate_returns_required_keys():
    env = fc.evaluate("bitcoin-bip-cycle")
    for key in (
        "cycle",
        "proposal_review_weeks",
        "economic_or_client_lead_weeks",
        "consensus_participant_update_weeks",
        "infrastructure_lead_weeks",
        "activation_window_weeks",
        "rationale",
    ):
        assert key in env


def test_evaluate_bitcoin_reports_bip_constants():
    env = fc.evaluate("bitcoin-bip-cycle")
    assert env["proposal_review_weeks"] == fc.BIP_PROPOSAL_REVIEW_WEEKS
    assert env["economic_or_client_lead_weeks"] == fc.BIP_ECONOMIC_ACTOR_LEAD_WEEKS
    assert env["consensus_participant_update_weeks"] == fc.CONSENSUS_PARTICIPANT_UPDATE_WEEKS
    assert env["infrastructure_lead_weeks"] == fc.INFRASTRUCTURE_LEAD_WEEKS


def test_evaluate_ethereum_reports_acd_constants():
    env = fc.evaluate("ethereum-acd-cycle")
    assert env["proposal_review_weeks"] == fc.ACD_PROPOSAL_REVIEW_WEEKS
    assert env["economic_or_client_lead_weeks"] == fc.ACD_CLIENT_TEAM_RELEASE_WEEKS
    assert env["consensus_participant_update_weeks"] == fc.CONSENSUS_PARTICIPANT_UPDATE_WEEKS
    assert env["infrastructure_lead_weeks"] == fc.INFRASTRUCTURE_LEAD_WEEKS


def test_evaluate_rejects_unknown_cycle():
    import pytest

    with pytest.raises(AssertionError):
        fc.evaluate("avalanche-tss-cycle")


def test_compare_cycles_returns_two_envelopes():
    envs = fc.compare_cycles()
    assert len(envs) == 2
    cycles_seen = {e["cycle"] for e in envs}
    assert cycles_seen == {"bitcoin-bip-cycle", "ethereum-acd-cycle"}


def test_compare_cycles_order_matches_cycles_constant():
    envs = fc.compare_cycles()
    assert [e["cycle"] for e in envs] == list(fc.CYCLES)


def test_cycle_difference_is_positive_at_chain_tip_2026():
    # Bitcoin's economic-actor lead time dominates; the cycle
    # difference is positive at the chain-tip 2026 anchors.
    assert fc.cycle_difference_weeks() > 0


def test_to_years_converts_weeks_to_fractional_years():
    assert fc.to_years(52) == 1.0
    assert fc.to_years(26) == 0.5
    assert fc.to_years(0) == 0.0


def test_to_years_rejects_negative_weeks():
    import pytest

    with pytest.raises(AssertionError):
        fc.to_years(-1)


def test_activation_window_bitcoin_above_half_year():
    weeks = fc.activation_window_weeks("bitcoin-bip-cycle")
    assert fc.to_years(weeks) > 0.75


def test_activation_window_ethereum_below_bitcoin():
    btc_weeks = fc.activation_window_weeks("bitcoin-bip-cycle")
    eth_weeks = fc.activation_window_weeks("ethereum-acd-cycle")
    assert eth_weeks < btc_weeks


def test_evaluate_returns_int_for_all_week_fields():
    for cycle in fc.CYCLES:
        env = fc.evaluate(cycle)
        for key in (
            "proposal_review_weeks",
            "economic_or_client_lead_weeks",
            "consensus_participant_update_weeks",
            "infrastructure_lead_weeks",
            "activation_window_weeks",
        ):
            assert isinstance(env[key], int)


def test_rationale_distinguishes_cycles():
    btc = fc.evaluate("bitcoin-bip-cycle")["rationale"]
    eth = fc.evaluate("ethereum-acd-cycle")["rationale"]
    assert btc != eth
    assert "BIP" in btc or "Bitcoin" in btc
    assert "AllCoreDevs" in eth or "Ethereum" in eth


def test_bip_cycle_constants_match_the_chapter_anchors():
    # The chapter prints 16 and 26 apart, Figure 41.2 draws them as
    # separate bar segments, and the claim that the Bitcoin cycle runs
    # longer "because the economic-actor lead window dominates" reads
    # the two apart rather than through their sum.
    assert fc.BIP_PROPOSAL_REVIEW_WEEKS == 16
    assert fc.BIP_ECONOMIC_ACTOR_LEAD_WEEKS == 26
    assert fc.BIP_ECONOMIC_ACTOR_LEAD_WEEKS > fc.BIP_PROPOSAL_REVIEW_WEEKS


def test_acd_cycle_constants_match_the_chapter_anchors():
    assert fc.ACD_PROPOSAL_REVIEW_WEEKS == 12
    assert fc.ACD_CLIENT_TEAM_RELEASE_WEEKS == 8
    assert fc.ACD_PROPOSAL_REVIEW_WEEKS > fc.ACD_CLIENT_TEAM_RELEASE_WEEKS


def test_shared_cycle_constants_match_the_chapter_anchors():
    assert fc.CONSENSUS_PARTICIPANT_UPDATE_WEEKS == 4
    assert fc.INFRASTRUCTURE_LEAD_WEEKS == 8


def test_acd_proposal_review_spans_six_biweekly_cycles():
    # The chapter reads the 12-week ACD review as "roughly three
    # monthly cycles of forum-call agenda inclusion (six biweekly
    # cycles)". This is the only arithmetic claim the biweekly cadence
    # constant enters; without it the constant reaches no code at all.
    assert fc.ACD_PROPOSAL_REVIEW_WEEKS // fc.ACD_BIWEEKLY_CADENCE_WEEKS == 6


def test_activation_windows_match_the_printed_totals():
    # Block 2 prints 46 and 24 and Figure 41.2 draws both to scale. The
    # two component-sum tests above recompute from the same constants,
    # so neither can see a change that moves a component and the total
    # together.
    assert fc.activation_window_weeks("bitcoin-bip-cycle") == 46
    assert fc.activation_window_weeks("ethereum-acd-cycle") == 24
    assert fc.cycle_difference_weeks() == 22


def test_printed_year_conversions_match_block_2():
    # Block 2 prints 0.885 and 0.462 at three decimal places.
    assert round(fc.to_years(46), 3) == 0.885
    assert round(fc.to_years(24), 3) == 0.462
