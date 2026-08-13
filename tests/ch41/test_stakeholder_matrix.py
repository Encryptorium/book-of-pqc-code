"""Tests for governance.stakeholder_matrix."""

from governance import stakeholder_matrix as sm


def test_stakeholders_have_three_entries(stakeholders):
    assert sm.STAKEHOLDERS == tuple(stakeholders)


def test_actions_have_three_entries(actions):
    assert sm.ACTIONS == tuple(actions)


def test_lookup_returns_required_keys():
    cell = sm.lookup("protocol-developer", "propose")
    for key in (
        "stakeholder",
        "action",
        "work_stream_owner",
        "coordination_role",
        "pq_status",
        "rationale",
    ):
        assert key in cell


def test_lookup_rejects_unknown_stakeholder():
    import pytest

    with pytest.raises(AssertionError):
        sm.lookup("treasury-multisig", "propose")


def test_lookup_rejects_unknown_action():
    import pytest

    with pytest.raises(AssertionError):
        sm.lookup("protocol-developer", "ratify")


def test_decomposition_summary_renders_nine_cells():
    cells = sm.decomposition_summary()
    assert len(cells) == 9
    seen_pairs = {(c["stakeholder"], c["action"]) for c in cells}
    assert seen_pairs == {(s, a) for s in sm.STAKEHOLDERS for a in sm.ACTIONS}


def test_decomposition_summary_order_is_deterministic():
    cells = sm.decomposition_summary()
    expected_order = [
        (s, a) for s in sm.STAKEHOLDERS for a in sm.ACTIONS
    ]
    actual_order = [(c["stakeholder"], c["action"]) for c in cells]
    assert actual_order == expected_order


def test_each_action_has_at_least_one_primary_owner():
    primaries = sm.primary_owners()
    assert set(primaries.keys()) == set(sm.ACTIONS)
    for action, owners in primaries.items():
        assert len(owners) >= 1, f"action {action!r} has no primary owner"


def test_propose_primary_is_protocol_developer():
    primaries = sm.primary_owners()
    assert primaries["propose"] == ["protocol-developer"]


def test_audit_primary_is_protocol_developer():
    primaries = sm.primary_owners()
    assert primaries["audit"] == ["protocol-developer"]


def test_deploy_carries_two_primaries():
    # The deploy action has two primaries: validator-operator on
    # the consensus surface (consensus-rule rollout) and
    # infrastructure-service-provider on the read-side surface
    # (RPC API and indexer schema swap).
    primaries = sm.primary_owners()
    assert set(primaries["deploy"]) == {
        "validator-operator",
        "infrastructure-service-provider",
    }


def test_cells_with_role_primary_finds_four_cells():
    # Four primary cells: protocol-developer on propose and audit;
    # validator-operator on deploy; infrastructure-service-provider
    # on deploy.
    cells = sm.cells_with_role("primary")
    assert len(cells) == 4
    actions_seen = {a for _, a in cells}
    assert actions_seen == set(sm.ACTIONS)


def test_audit_action_has_co_owner_cells():
    cells = sm.cells_with_role("co-owner")
    actions_seen = {a for _, a in cells}
    assert sm.ACTIONS[1] in actions_seen  # audit row carries co-owner cells


def test_cells_with_role_rejects_unknown_role():
    import pytest

    with pytest.raises(AssertionError):
        sm.cells_with_role("approver")


def test_cells_with_pq_status_pending_includes_infrastructure():
    cells = sm.cells_with_pq_status("pq-pending")
    stakeholders_seen = {s for s, _ in cells}
    assert "infrastructure-service-provider" in stakeholders_seen


def test_cells_with_pq_status_deployed_includes_protocol_developer():
    cells = sm.cells_with_pq_status("deployed")
    stakeholders_seen = {s for s, _ in cells}
    assert "protocol-developer" in stakeholders_seen


def test_cells_with_pq_status_rejects_unknown_status():
    import pytest

    with pytest.raises(AssertionError):
        sm.cells_with_pq_status("approved")


def test_protocol_developer_owns_propose_action_primary():
    cell = sm.lookup("protocol-developer", "propose")
    assert cell["coordination_role"] == "primary"
    assert cell["work_stream_owner"] == "core-development-team"


def test_validator_operator_propose_is_downstream_consumer():
    cell = sm.lookup("validator-operator", "propose")
    assert cell["coordination_role"] == "downstream-consumer"


def test_infrastructure_service_provider_deploy_is_primary_for_read_side():
    cell = sm.lookup("infrastructure-service-provider", "deploy")
    assert cell["coordination_role"] == "primary"


def test_audit_action_has_no_downstream_consumer():
    # Every stakeholder participates in the audit action; the
    # downstream-consumer role applies only on the propose column.
    audit_roles = {
        sm.MATRIX[s]["audit"]["coordination_role"] for s in sm.STAKEHOLDERS
    }
    assert "downstream-consumer" not in audit_roles


def test_pq_status_values_are_valid():
    valid = {"deployed", "pq-pending", "pq-research"}
    for s in sm.STAKEHOLDERS:
        for a in sm.ACTIONS:
            assert sm.MATRIX[s][a]["pq_status"] in valid


def test_coordination_role_values_are_valid():
    valid = {"primary", "co-owner", "downstream-consumer"}
    for s in sm.STAKEHOLDERS:
        for a in sm.ACTIONS:
            assert sm.MATRIX[s][a]["coordination_role"] in valid


def test_rationale_is_non_empty_for_all_cells():
    for s in sm.STAKEHOLDERS:
        for a in sm.ACTIONS:
            cell = sm.MATRIX[s][a]
            assert isinstance(cell["rationale"], str)
            assert len(cell["rationale"]) > 0


def test_work_stream_owner_is_non_empty_for_all_cells():
    for s in sm.STAKEHOLDERS:
        for a in sm.ACTIONS:
            cell = sm.MATRIX[s][a]
            assert isinstance(cell["work_stream_owner"], str)
            assert len(cell["work_stream_owner"]) > 0


def test_each_stakeholder_has_at_least_one_primary_action():
    # Each stakeholder owns at least one action as primary.
    primaries = sm.primary_actions_per_stakeholder()
    assert set(primaries.keys()) == set(sm.STAKEHOLDERS)
    for stakeholder, actions in primaries.items():
        assert len(actions) >= 1, (
            f"stakeholder {stakeholder!r} should have at least one "
            f"primary action, found 0"
        )


def test_protocol_developer_owns_two_primary_actions():
    # protocol-developer is primary on propose (drafting) and audit
    # (integrating fixes from the external security-audit firm).
    primaries = sm.primary_actions_per_stakeholder()
    assert set(primaries["protocol-developer"]) == {"propose", "audit"}


def test_validator_operator_owns_one_primary_action():
    # validator-operator is primary on the consensus-surface deploy
    # only; downstream-consumer on propose and co-owner on audit.
    primaries = sm.primary_actions_per_stakeholder()
    assert primaries["validator-operator"] == ["deploy"]


def test_infrastructure_service_provider_owns_one_primary_action():
    # infrastructure-service-provider is primary on the read-side
    # deploy only; downstream-consumer on propose and co-owner on
    # audit.
    primaries = sm.primary_actions_per_stakeholder()
    assert primaries["infrastructure-service-provider"] == ["deploy"]


def test_work_stream_owner_is_pinned_per_stakeholder():
    # Each stakeholder carries one owner across all three actions, and
    # the three owners are distinct, so an owner-column permutation
    # cannot satisfy this by two stakeholders sharing a label.
    expected = {
        "protocol-developer": "core-development-team",
        "validator-operator": "validator-coordinator",
        "infrastructure-service-provider": "rpc-provider-and-indexer-team",
    }
    for stakeholder, owner in expected.items():
        for action in sm.ACTIONS:
            cell = sm.lookup(stakeholder, action)
            assert cell["work_stream_owner"] == owner, (
                f"{stakeholder!r} on {action!r} should be owned by {owner!r}, "
                f"got {cell['work_stream_owner']!r}"
            )
    assert len(set(expected.values())) == len(expected)


def test_pq_status_is_pinned_per_stakeholder():
    # This matrix splits on the stakeholder axis rather than the action
    # axis: the protocol-developer and validator-operator rows are
    # deployed in all three columns, and all three infrastructure-
    # service-provider cells are pq-pending.
    expected = {
        "protocol-developer": "deployed",
        "validator-operator": "deployed",
        "infrastructure-service-provider": "pq-pending",
    }
    for stakeholder, status in expected.items():
        for action in sm.ACTIONS:
            cell = sm.lookup(stakeholder, action)
            assert cell["pq_status"] == status, (
                f"{stakeholder!r} on {action!r} should be {status!r}, "
                f"got {cell['pq_status']!r}"
            )
    assert len(sm.cells_with_pq_status("deployed")) == 6
    assert len(sm.cells_with_pq_status("pq-pending")) == 3
    assert sm.cells_with_pq_status("pq-research") == []


def test_rationale_names_its_own_cell_and_is_unique():
    # A per-cell token paired with a uniqueness check, so the token
    # assertion cannot be satisfied by two cells sharing a rationale.
    tokens = {
        ("protocol-developer", "propose"): "drafts",
        ("protocol-developer", "audit"): "security-audit firm",
        ("protocol-developer", "deploy"): "reference-implementation release",
        ("validator-operator", "propose"): "signals support",
        ("validator-operator", "audit"): "testnet",
        ("validator-operator", "deploy"): "consensus client",
        ("infrastructure-service-provider", "propose"): "signals breakage",
        ("infrastructure-service-provider", "audit"): "end-user breakage",
        ("infrastructure-service-provider", "deploy"): "block-explorer renderers",
    }
    seen = set()
    for (stakeholder, action), token in tokens.items():
        rationale = sm.lookup(stakeholder, action)["rationale"]
        assert token in rationale, (
            f"{stakeholder!r} on {action!r} should mention {token!r}, "
            f"got {rationale!r}"
        )
        seen.add(rationale)
    assert len(seen) == 9, "every cell carries a distinct rationale"
