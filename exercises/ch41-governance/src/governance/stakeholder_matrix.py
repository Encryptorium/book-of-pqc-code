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
    # EXERCISE: implement this function.
    #
    # Assert the stakeholder and the action separately so a typo names which
    # argument was wrong, index MATRIX by stakeholder then action, and
    # flatten the cell into a dict carrying stakeholder, action,
    # work_stream_owner, coordination_role, pq_status, and rationale. The
    # cell's fields were resolved when the module built the matrix; this
    # function does not re-derive them. Read the table before writing the
    # return, because coordination_role is the load-bearing column: the
    # protocol-developer is primary on propose and audit and co-owner on
    # deploy, while the validator-operator and the
    # infrastructure-service-provider are both downstream-consumer on
    # propose, co-owner on audit, and primary on their own half of deploy.
    #
    # Reference: Chapter 41, 'Decompose the stakeholder set into three groups and pick a per-action work-stream owner'
    #
    # Proved by:
    #   tests/ch41/test_stakeholder_matrix.py
    raise NotImplementedError("exercise: lookup")


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
    # EXERCISE: implement this function.
    #
    # Assert coordination_role against the three-value vocabulary (primary,
    # co-owner, downstream-consumer), then walk STAKEHOLDERS and ACTIONS in
    # declared order, collecting the (stakeholder, action) pairs whose
    # MATRIX cell carries that role. Iterate the two tuples rather than the
    # matrix dict so the result keeps the chapter's table order. This is the
    # query behind the chapter's Block 1: filtering on 'primary' returns
    # exactly four cells, because deploy has two primary owners while
    # propose and audit have one each.
    #
    # Reference: Chapter 41, 'Decompose the stakeholder set into three groups and pick a per-action work-stream owner'
    #
    # Proved by:
    #   tests/ch41/test_stakeholder_matrix.py
    raise NotImplementedError("exercise: cells_with_role")


def cells_with_pq_status(pq_status: str) -> List[Tuple[str, str]]:
    """Return every (stakeholder, action) pair carrying the given PQ-status.

    Useful for the chapter to enumerate, for example, every
    pq-pending cell across all three stakeholders in one pass.
    """
    # EXERCISE: implement this function.
    #
    # The same walk as cells_with_role over the other cell field. Assert
    # pq_status against the three-value vocabulary the module records
    # (deployed, pq-pending, pq-research), then collect the matching
    # (stakeholder, action) pairs across STAKEHOLDERS by ACTIONS in declared
    # order. This matrix splits on the stakeholder axis rather than the
    # action axis: the protocol-developer and validator-operator rows are
    # 'deployed' in all three columns, and all three
    # infrastructure-service-provider cells are 'pq-pending', because RPC
    # providers, indexers, and block explorers had published no post-quantum
    # deployment policy at chain-tip 2026. No cell is 'pq-research'; the
    # value is in the vocabulary so the assert stays aligned with Ch 40's
    # status notation.
    #
    # Reference: Chapter 41, 'Decompose the stakeholder set into three groups and pick a per-action work-stream owner'
    #
    # Proved by:
    #   tests/ch41/test_stakeholder_matrix.py
    raise NotImplementedError("exercise: cells_with_pq_status")


def primary_owners() -> Dict[str, List[str]]:
    """Return the primary owners per action as a list.

    Each action has at least one stakeholder marked ``primary``. The
    deploy action carries two primaries (one on the consensus surface
    and one on the read-side surface); the propose and audit actions
    each carry one primary. The chapter's tradeoffs table reads from
    this map to label the primary-owner column without re-walking
    the full matrix.
    """
    # EXERCISE: implement this function.
    #
    # The chapter's Block 1 output, keyed by action. Walk ACTIONS in order
    # and, for each, collect the stakeholders whose MATRIX cell carries
    # coordination_role 'primary', keeping STAKEHOLDERS order inside each
    # list. Assert each action found at least one, since an action with no
    # primary owner is a broken matrix rather than a valid state. propose
    # and audit each return a single-element list holding
    # protocol-developer; deploy returns two, validator-operator on the
    # consensus surface and infrastructure-service-provider on the read
    # side. That two-owner deploy cell is the chapter's point that the
    # rollout phase has no single owner.
    #
    # Reference: Chapter 41, 'Decompose the stakeholder set into three groups and pick a per-action work-stream owner'
    #
    # Proved by:
    #   tests/ch41/test_stakeholder_matrix.py
    raise NotImplementedError("exercise: primary_owners")


def primary_actions_per_stakeholder() -> Dict[str, List[str]]:
    """Return the primary actions per stakeholder as a list.

    Each stakeholder owns at least one action as primary. The
    protocol-developer owns propose and audit; the validator-operator
    owns the consensus-surface deploy; the infrastructure-service-
    provider owns the read-side-surface deploy.
    """
    # EXERCISE: implement this function.
    #
    # The transpose of primary_owners: walk STAKEHOLDERS in order and
    # collect, per stakeholder, the actions whose cell carries 'primary',
    # keeping ACTIONS order inside each list, and assert each stakeholder
    # found at least one. protocol-developer returns propose and audit; the
    # other two return deploy alone. Build it from MATRIX directly rather
    # than by inverting primary_owners, so the two functions read the same
    # column from opposite ends without one depending on the other.
    #
    # Reference: Chapter 41, 'Decompose the stakeholder set into three groups and pick a per-action work-stream owner'
    #
    # Proved by:
    #   tests/ch41/test_stakeholder_matrix.py
    raise NotImplementedError("exercise: primary_actions_per_stakeholder")
