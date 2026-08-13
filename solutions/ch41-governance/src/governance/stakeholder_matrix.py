"""Three-stakeholder by three-action decomposition for a hard-fork choreography.

Ch 30 runs a migration as work streams, each with an owner, a
cadence, and a deliverable, over the six architectural areas Ch 26
introduces. On a public chain the owners are not internal teams,
so the post-quantum hard-fork rollout in this chapter names its
own three, each carrying a per-action coordination cadence:

- ``protocol-developer``: the core-development team that drafts the
  consensus-rule change. Owns the propose action; owns the audit
  action as primary, integrating fixes from the external security-
  audit firm into the proposal; collaborates on the deploy action
  with the validator coordinator.
- ``validator-operator``: the staking operator that runs the
  consensus client. Owns the deploy action on the consensus surface;
  co-owns the audit action with the testing-infrastructure team;
  takes a downstream consumer role on the propose action.
- ``infrastructure-service-provider``: the RPC provider, indexer,
  block-explorer operator, or wallet vendor that fronts the chain
  for end users. Owns the deploy action on the read-side surface;
  co-owns the audit action through end-user breakage testing; takes
  a downstream consumer role on the propose action.

Three actions, named to match the Ch 40 verifier-contract
choreography but generalized to any L1 hard fork:

- ``propose``: a written change proposal (a BIP for Bitcoin, an
  EIP for Ethereum, a governance forum thread for an L2 bridge).
- ``audit``: external review of the proposal and a reference
  implementation. Bug bounty programs sit here. The phase that the
  Ch 40 verifier-contract review subsection generalizes.
- ``deploy``: rolling out the activation. For protocol developers
  this is reference-implementation release; for validator operators
  this is consensus-client upgrade and validator-set update; for
  infrastructure providers this is RPC API and indexer schema swap.

Each cell of the three-by-three matrix records:

- ``work_stream_owner``: a label naming who owns this cell. Cells
  where two stakeholders co-own carry a primary owner with a
  co-owner annotation in the rationale.
- ``coordination_role``: one of ``primary``, ``co-owner``,
  ``downstream-consumer``, naming how this stakeholder relates to
  this action. The matrix encodes the responsibility-assignment
  framing without a separate RACI reduction.
- ``rationale``: a one-line description of what this stakeholder
  does in this action.

The chain-cycle quantification (BIP cycle versus All-Core-Devs
cycle, validator-set update cycle, infrastructure-lead cycle)
sits in ``fork_choreography``; this module records only the
stakeholder-by-action role assignment.

PQ-status notation matches Ch 40 conventions: ``deployed``
labels chain-tip 2026 deployed work-stream owners; ``pq-pending``
labels work-stream owners still ramping post-quantum capability
(for example, RPC providers that have not yet published a
post-quantum deployment policy at chain-tip 2026); ``pq-research``
labels research-grade owners (for example, threshold-ML-DSA
governance committees that exist only in published proposals).
"""

from typing import Dict, List, Tuple, TypedDict


class StakeholderCell(TypedDict):
    work_stream_owner: str
    coordination_role: str
    pq_status: str
    rationale: str


STAKEHOLDERS: Tuple[str, ...] = (
    "protocol-developer",
    "validator-operator",
    "infrastructure-service-provider",
)

ACTIONS: Tuple[str, ...] = (
    "propose",
    "audit",
    "deploy",
)


def _cell(
    work_stream_owner: str,
    coordination_role: str,
    pq_status: str,
    rationale: str,
) -> StakeholderCell:
    return {
        "work_stream_owner": work_stream_owner,
        "coordination_role": coordination_role,
        "pq_status": pq_status,
        "rationale": rationale,
    }


# Stakeholder x action decision matrix. Each cell records the
# work-stream owner, the coordination role
# (primary / co-owner / downstream-consumer), the chain-tip 2026
# PQ-status, and a one-line rationale.
MATRIX: Dict[str, Dict[str, StakeholderCell]] = {
    "protocol-developer": {
        "propose": _cell(
            "core-development-team",
            "primary",
            "deployed",
            "drafts the BIP or EIP and shepherds it through the public review",
        ),
        "audit": _cell(
            "core-development-team",
            "primary",
            "deployed",
            "merges fixes from the external security-audit firm into the proposal",
        ),
        "deploy": _cell(
            "core-development-team",
            "co-owner",
            "deployed",
            "ships the reference-implementation release the validators install",
        ),
    },
    "validator-operator": {
        "propose": _cell(
            "validator-coordinator",
            "downstream-consumer",
            "deployed",
            "reviews the proposal and signals support on a public forum",
        ),
        "audit": _cell(
            "validator-coordinator",
            "co-owner",
            "deployed",
            "runs the proposal against a public testnet with a downstream client",
        ),
        "deploy": _cell(
            "validator-coordinator",
            "primary",
            "deployed",
            "upgrades the consensus client and rotates the validator set",
        ),
    },
    "infrastructure-service-provider": {
        "propose": _cell(
            "rpc-provider-and-indexer-team",
            "downstream-consumer",
            "pq-pending",
            "reviews API surface and signals breakage of indexer schemas",
        ),
        "audit": _cell(
            "rpc-provider-and-indexer-team",
            "co-owner",
            "pq-pending",
            "tests end-user breakage of wallet vendors, block explorers, indexers",
        ),
        "deploy": _cell(
            "rpc-provider-and-indexer-team",
            "primary",
            "pq-pending",
            "swaps RPC API responses, indexer schemas, and block-explorer renderers",
        ),
    },
}


def lookup(stakeholder: str, action: str) -> Dict[str, object]:
    """Return the per-cell decision for a (stakeholder, action) pair.

    Each cell carries the work-stream owner, the coordination role,
    the chain-tip 2026 PQ-status, and a one-line rationale.
    """
    assert stakeholder in STAKEHOLDERS, f"unknown stakeholder: {stakeholder!r}"
    assert action in ACTIONS, f"unknown action: {action!r}"
    cell = MATRIX[stakeholder][action]
    return {
        "stakeholder": stakeholder,
        "action": action,
        "work_stream_owner": cell["work_stream_owner"],
        "coordination_role": cell["coordination_role"],
        "pq_status": cell["pq_status"],
        "rationale": cell["rationale"],
    }


def decomposition_summary() -> List[Dict[str, object]]:
    """Flatten the full stakeholder x action matrix into a list of cells.

    Order matches STAKEHOLDERS x ACTIONS so a chapter table renders
    deterministically. Useful for the chapter's inline Block 1 print
    and for a test that asserts the deterministic order.
    """
    out: List[Dict[str, object]] = []
    for stakeholder in STAKEHOLDERS:
        for action in ACTIONS:
            out.append(lookup(stakeholder, action))
    return out


def cells_with_role(coordination_role: str) -> List[Tuple[str, str]]:
    """Return every (stakeholder, action) pair carrying the given role.

    Useful for the chapter to enumerate, for example, every primary-
    role cell across all three stakeholders in one pass.
    """
    valid_roles = {"primary", "co-owner", "downstream-consumer"}
    assert coordination_role in valid_roles, (
        f"unknown coordination_role: {coordination_role!r}"
    )
    out: List[Tuple[str, str]] = []
    for stakeholder in STAKEHOLDERS:
        for action in ACTIONS:
            if MATRIX[stakeholder][action]["coordination_role"] == coordination_role:
                out.append((stakeholder, action))
    return out


def cells_with_pq_status(pq_status: str) -> List[Tuple[str, str]]:
    """Return every (stakeholder, action) pair carrying the given PQ-status.

    Useful for the chapter to enumerate, for example, every
    pq-pending cell across all three stakeholders in one pass.
    """
    valid_statuses = {"deployed", "pq-pending", "pq-research"}
    assert pq_status in valid_statuses, f"unknown pq_status: {pq_status!r}"
    out: List[Tuple[str, str]] = []
    for stakeholder in STAKEHOLDERS:
        for action in ACTIONS:
            if MATRIX[stakeholder][action]["pq_status"] == pq_status:
                out.append((stakeholder, action))
    return out


def primary_owners() -> Dict[str, List[str]]:
    """Return the primary owners per action as a list.

    Each action has at least one stakeholder marked ``primary``. The
    deploy action carries two primaries (one on the consensus surface
    and one on the read-side surface); the propose and audit actions
    each carry one primary. The chapter's tradeoffs table reads from
    this map to label the primary-owner column without re-walking
    the full matrix.
    """
    out: Dict[str, List[str]] = {}
    for action in ACTIONS:
        primaries = [
            stakeholder
            for stakeholder in STAKEHOLDERS
            if MATRIX[stakeholder][action]["coordination_role"] == "primary"
        ]
        assert len(primaries) >= 1, (
            f"action {action!r} must have at least one primary owner, "
            f"found 0"
        )
        out[action] = primaries
    return out


def primary_actions_per_stakeholder() -> Dict[str, List[str]]:
    """Return the primary actions per stakeholder as a list.

    Each stakeholder owns at least one action as primary. The
    protocol-developer owns propose and audit; the validator-operator
    owns the consensus-surface deploy; the infrastructure-service-
    provider owns the read-side-surface deploy.
    """
    out: Dict[str, List[str]] = {}
    for stakeholder in STAKEHOLDERS:
        primaries = [
            action
            for action in ACTIONS
            if MATRIX[stakeholder][action]["coordination_role"] == "primary"
        ]
        assert len(primaries) >= 1, (
            f"stakeholder {stakeholder!r} must have at least one primary "
            f"action, found 0"
        )
        out[stakeholder] = primaries
    return out
