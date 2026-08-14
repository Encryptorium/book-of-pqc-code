"""Cross-stakeholder activation-window arithmetic.

The chapter compares two named coordination cycles on the on-chain
L1 surface — a Bitcoin-style soft-fork / BIP process and an
Ethereum-style All Core Devs hard-fork process:

- ``bitcoin-bip-cycle``: the Bitcoin Improvement Proposal cycle. A
  proposal lands on the bitcoin-dev mailing list, and a BIP editor
  merges it into the bitcoin/bips repository at Draft status once
  it passes the editorial checks in BIP 3. It advances to Complete
  when its authors have concluded all planned work and recommend
  adoption, which for a Specification BIP requires a working
  reference implementation and test vectors, and reaches Deployed
  on evidence of active use. Activation happens on the chain
  through one of several deployment mechanisms (BIP 9 versionbits,
  BIP 8, soft-fork-specific signaling). The activation window is
  dominated by the proposal review and the economic-actor lead
  time. BIP 3 replaced BIP 2 in 2025 and collapsed the older
  Final and Active statuses into Deployed; the editors run an
  administrative gate and do not judge whether a proposal is
  likely to be adopted.
- ``ethereum-acd-cycle``: the Ethereum All Core Devs cycle. A
  proposal lands as an EIP, surfaces on the eth-magicians forum,
  appears on the AllCoreDevs biweekly call agenda, accumulates
  rough consensus across the consensus-client and execution-client
  teams, and activates at a named hard-fork epoch. The activation
  window is dominated by the AllCoreDevs review, the client-team
  release lead time, and the validator-set update cycle.

The figures in this module are illustrative anchors at chain-tip
2026, not precise schedule numbers. Any production hard fork
measures against its own coordination history; the chapter's
arithmetic shows the shape of the comparison rather than the
exact week count.

Quantity vocabulary used throughout (defined precisely to avoid
the per-cycle collision the Ch 39 R1 review caught at the
consensus surface):

- ``bip_proposal_review_weeks``: weeks between the bitcoin-dev
  draft and the editorial merge of the numbered BIP at Draft
  status.
- ``bip_economic_actor_lead_weeks``: the lead window before
  activation, giving mining pools, exchanges, custodians,
  and wallet vendors time to stage code.
- ``acd_proposal_review_weeks``: weeks between EIP draft and
  AllCoreDevs forum-call agenda inclusion, accumulating the
  cross-client rough consensus.
- ``acd_client_team_release_weeks``: weeks between AllCoreDevs
  scheduling the EIP for a named upgrade and that upgrade's
  activation epoch, giving the consensus-client and
  execution-client teams time to ship release builds. The EIP is
  not Final across this window: All Core Devs track inclusion
  separately from EIP document status, and an EIP is marked
  Included only after the upgrade activates.
- ``consensus_participant_update_weeks``: weeks the rule-
  enforcement set takes to roll over once the activation block or
  hard-fork epoch lands. On Ethereum this is the validator-set
  rotation (per the Ch 39 R1 per-epoch vs per-slot framing); on
  Bitcoin this is full-node, miner, and mining-pool readiness
  against the activation height.
- ``infrastructure_lead_weeks``: weeks RPC providers, indexers,
  and block explorers need to update their API surfaces and
  schemas around the activation. Sits in parallel with the
  client-team release lead time.

Each cycle's activation-window length is the sum of the
proposal-review weeks, the economic-actor or client-team lead
weeks, and the consensus-participant update weeks; the
infrastructure-lead weeks run in parallel and do not stack onto
the critical path. Cycle-name suffixes on every reported quantity
make this explicit at every call site.
"""

from typing import Dict, List, TypedDict


# Bitcoin BIP-cycle activation-window components, illustrative
# anchors at chain-tip 2026. The proposal-review window absorbs
# bitcoin-dev mailing-list discussion plus formal BIP-repository
# acceptance. The economic-actor lead time is dominated by mining
# pools, exchanges, custodians, and wallet vendors staging release
# builds against the activation height.
BIP_PROPOSAL_REVIEW_WEEKS = 16
BIP_ECONOMIC_ACTOR_LEAD_WEEKS = 26

# Ethereum All Core Devs cycle activation-window components,
# illustrative anchors at chain-tip 2026. The biweekly cadence
# constant is the AllCoreDevs meeting frequency. The proposal-
# review window absorbs cross-client rough consensus across the
# AllCoreDevs forum.
ACD_BIWEEKLY_CADENCE_WEEKS = 2
ACD_PROPOSAL_REVIEW_WEEKS = 12
ACD_CLIENT_TEAM_RELEASE_WEEKS = 8

# Consensus-participant update window. Chain-neutral name for the
# rule-enforcement-set rollover that follows the activation block
# or hard-fork epoch. On Ethereum this is the per-epoch validator-
# set rotation per the Ch 39 framing (with the per-slot subdivision
# folded in). On Bitcoin this is full-node, miner, and mining-pool
# readiness against the activation height; the miner-signaling
# lead time is captured separately under the economic-actor lead
# window above.
CONSENSUS_PARTICIPANT_UPDATE_WEEKS = 4

# Infrastructure-service-provider lead window. Runs in parallel
# with the client-team release lead time on the critical path.
# The chapter names this constant separately so the cross-cycle
# comparison reports it without folding it into the activation-
# window total.
INFRASTRUCTURE_LEAD_WEEKS = 8


CYCLES = (
    "bitcoin-bip-cycle",
    "ethereum-acd-cycle",
)


class CycleEnvelope(TypedDict):
    cycle: str
    proposal_review_weeks: int
    economic_or_client_lead_weeks: int
    consensus_participant_update_weeks: int
    infrastructure_lead_weeks: int
    activation_window_weeks: int
    rationale: str


def activation_window_weeks(cycle: str) -> int:
    """Total activation-window length in weeks for the named cycle.

    The activation window sums the proposal-review weeks, the
    economic-actor or client-team lead weeks, and the consensus-
    participant update weeks. The infrastructure-lead weeks run in
    parallel and are not added to the critical path.
    """
    # EXERCISE: implement this function.
    #
    # Assert the cycle is known, then sum the three critical-path components
    # for it. The Bitcoin BIP cycle is the 16-week proposal review plus the
    # 26-week economic-actor lead plus the 4-week consensus-participant
    # update, giving 46. The Ethereum AllCoreDevs cycle is the 12-week
    # proposal review plus the 8-week client-team release lead plus the same
    # 4-week update, giving 24. INFRASTRUCTURE_LEAD_WEEKS is deliberately
    # absent from both sums: RPC, indexer, and explorer readiness runs in
    # parallel with the release lead time and does not stack onto the
    # critical path. ACD_BIWEEKLY_CADENCE_WEEKS is the meeting frequency and
    # is not a window either.
    #
    # Reference: Chapter 41, 'Quantify the cross-stakeholder activation window'
    #
    # Proved by:
    #   tests/ch41/test_fork_choreography.py
    raise NotImplementedError("exercise: activation_window_weeks")


def evaluate(cycle: str) -> CycleEnvelope:
    """Combined per-cycle envelope at chain-tip 2026.

    Returns a seven-field envelope: the cycle name, the four week
    components (proposal review, economic-actor or client-team lead,
    consensus-participant update, and infrastructure lead off the
    critical path), the activation-window total, and a one-line
    rationale. The chapter's inline Block 2 prints the two totals,
    their year conversions, and the infrastructure-lead constant.
    """
    # EXERCISE: implement this function.
    #
    # Assemble the seven-field envelope the chapter's Block 2 prints: cycle,
    # proposal_review_weeks, economic_or_client_lead_weeks,
    # consensus_participant_update_weeks, infrastructure_lead_weeks,
    # activation_window_weeks, and rationale. Branch on the cycle to pick
    # which pair of constants fills the first two week fields, take the
    # shared update and infrastructure constants unchanged, and delegate the
    # total to activation_window_weeks rather than re-summing it. Give each
    # cycle its own rationale naming what dominates it: economic-actor lead
    # time for mining pools, exchanges, and custodians on Bitcoin,
    # cross-client release lead time on Ethereum. Every week field stays an
    # int.
    #
    # Reference: Chapter 41, 'Quantify the cross-stakeholder activation window'
    #
    # Proved by:
    #   tests/ch41/test_fork_choreography.py
    raise NotImplementedError("exercise: evaluate")


def compare_cycles() -> List[CycleEnvelope]:
    """Flatten the per-cycle envelopes for a chapter table."""
    return [evaluate(c) for c in CYCLES]


def cycle_difference_weeks() -> int:
    """Bitcoin minus Ethereum activation-window difference in weeks.

    Positive value means Bitcoin's activation window is longer.
    The economic-actor lead time on Bitcoin dominates the
    difference at chain-tip 2026.
    """
    return activation_window_weeks("bitcoin-bip-cycle") - activation_window_weeks(
        "ethereum-acd-cycle"
    )


def to_years(weeks: int) -> float:
    """Convert a weeks count to years for cross-Mosca comparison.

    Returns weeks divided by 52. Useful when the chapter compares
    an activation-window length in weeks against a Mosca-window
    breach in years.
    """
    # EXERCISE: implement this function.
    #
    # Divide by 52.0 after asserting the week count is non-negative. Keeping
    # the divisor a float matters: the chapter reports 46 weeks as 0.885
    # years and 24 weeks as 0.462, and integer division would flatten both
    # to zero. This is the conversion that puts an activation window
    # measured in weeks onto the same axis as a Mosca safe window measured
    # in years, which is how the chapter shows a 46-week Bitcoin cycle fits
    # inside the three-year narrow-scenario window.
    #
    # Reference: Chapter 41, 'Quantify the cross-stakeholder activation window'
    #
    # Proved by:
    #   tests/ch41/test_fork_choreography.py
    raise NotImplementedError("exercise: to_years")
