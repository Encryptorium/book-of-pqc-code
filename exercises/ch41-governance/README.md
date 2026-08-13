# ch41-governance

Reference implementation for Chapter 41, "Governance, hard forks, and
migration case studies".

The package models an operator coordinating a post-quantum signature
change across the stakeholder groups that have to agree to it. Three
modules, one per part of the chapter's playbook that produces a number
or a role assignment.

## Modules

`governance.stakeholder_matrix` holds the three-by-three decision
matrix. `STAKEHOLDERS` names the protocol developer, the validator
operator, and the infrastructure service provider; `ACTIONS` names
propose, audit, and deploy. `MATRIX` carries the nine cells, each
recording a `work_stream_owner`, a `coordination_role`, a `pq_status`,
and a one-line rationale. `lookup` flattens one cell into a dict,
`decomposition_summary` flattens all nine in declared order, and
`cells_with_role` and `cells_with_pq_status` run the reverse queries.
`primary_owners` and `primary_actions_per_stakeholder` read the same
column from opposite ends: the first is keyed by action and is what the
chapter's Block 1 prints, the second is keyed by stakeholder.

`governance.fork_choreography` holds the activation-window arithmetic
for the two cycles in `CYCLES`. `activation_window_weeks` sums the three
critical-path components for a named cycle, `evaluate` assembles the
seven-field envelope, `compare_cycles` flattens both,
`cycle_difference_weeks` subtracts one from the other, and `to_years`
puts a week count on the same axis as a Mosca window measured in years.

`governance.governance_mosca` specializes Mosca's inequality to the
governance surface. `breach_years` returns `X + Y - Z`,
`cadence_options` builds the four `CADENCE_NAMES` records with their
feasibility, rotation interval, and operational cost, `recommend_cadence`
picks the cheapest feasible one, and `evaluate` threads the Strand
anchor through it. `evaluate_named_scenario` runs one of the three names
in `SCENARIO_Z_VALUES`.

## Scope boundaries

Five things this package deliberately does not claim.

**The week constants are illustrative model parameters, not measured
protocol constants.** `BIP_PROPOSAL_REVIEW_WEEKS`,
`BIP_ECONOMIC_ACTOR_LEAD_WEEKS`, `ACD_PROPOSAL_REVIEW_WEEKS`,
`ACD_CLIENT_TEAM_RELEASE_WEEKS`, `CONSENSUS_PARTICIPANT_UPDATE_WEEKS`,
and `INFRASTRUCTURE_LEAD_WEEKS` are pedagogical anchors at chain-tip
2026, chosen so the shape of the cross-cycle comparison is right. No
Bitcoin soft fork and no Ethereum hard fork was measured to produce
them, and the chapter and both figures say so in the same words. A
production hard fork measures against its own coordination history.

**The three stakeholders are this chapter's own taxonomy.** Ch 26
introduces six architectural areas a migration organizes around; Ch 30
runs them as work streams with an owner, a cadence, and a deliverable
each. Neither names a protocol developer, a validator operator, or an
infrastructure service provider, because on a public chain the owners
are not internal teams. The owner / cadence / deliverable framing is
Ch 30's; the membership is this chapter's.

**The infrastructure-lead window is modelled as off the critical path,
and a real upgrade can contradict that.** `activation_window_weeks`
deliberately omits `INFRASTRUCTURE_LEAD_WEEKS` from both sums, which
encodes the planning assumption that RPC, indexer, and explorer
readiness runs in parallel with the client-team release lead time. When
an upgrade lands without coordinated infrastructure readiness, that
readiness becomes the binding constraint and the model understates the
window. The chapter says so; the arithmetic cannot.

**`pq-research` is in the `pq_status` vocabulary and no cell carries
it.** `cells_with_pq_status` accepts it and returns an empty list. The
value is retained so the module's status vocabulary matches the notation
Chapter 40 uses, not because the matrix has a research-grade cell.

**`per-vote-cycle` is never the recommendation.** It is always feasible
and always `prohibitive`, so `recommend_cadence` returns it inside the
options dict as the zero-overhead lower bound and never as the pick. A
caller that wants it has to override the recommendation deliberately.

## Running the tests

From a clone of the companion repository:

```
pytest tests/ch41
```

The suite defaults to this tree. To grade a rebuild against it instead,
set `PQC_IMPL` to `exercises` and the same command runs against the stub
package, where every function the chapter teaches raises
`NotImplementedError` until you write it.
