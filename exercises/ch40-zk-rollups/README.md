# ch40-zk-rollups

Reference implementation for Chapter 40, "Quantum threats to ZK rollups".

The package models an operator's decision about migrating a ZK rollup
verifier contract on Ethereum L1 to a post-quantum-friendlier
construction. Three modules, one per decision the chapter's playbook
makes.

## Modules

`zk_rollups.verifier_layers` holds the layer-by-candidate decision
matrix. `LAYERS` names the four layers of the Ch 31 decomposition and
`CANDIDATES_BY_LAYER` gives each layer's candidate set, fourteen cells
in total. `lookup` returns one cell flattened into a dict carrying the
layer, the candidate, its `pq_status`, its `deployment_status`, and a
one-line rationale. `candidates_with_status` runs the reverse query,
collecting every cell that carries a given status, and
`deployment_summary` flattens the whole matrix in declared order.
`system_profile` reads one of the two entries in `SYSTEM_ANCHORS` and
resolves its four cells.

`zk_rollups.gas_budget` holds the per-proof gas arithmetic across the
three configurations in `CONFIGURATIONS`. `per_proof_gas`,
`per_batch_gas`, `per_effective_proof_gas`, `proofs_per_block_max`,
`factor_vs_legacy`, and `per_rollup_cycle_gas` each compute one
quantity; `evaluate` assembles them into an eight-field envelope and
`compare_configurations` flattens all three.

`zk_rollups.verifier_mosca` specializes Mosca's inequality to the
on-chain-verifier surface. `breach_years` returns `X + Y - Z`,
`cadence_options` builds the four `CADENCE_NAMES` records with their
feasibility and cost, `recommend_cadence` picks the cheapest feasible
one, and `evaluate` threads the Strand anchor through it.
`evaluate_named_scenario` runs one of the three names in
`SCENARIO_Z_VALUES`.

## Scope boundaries

Four things this package deliberately does not claim.

**The gas figures are illustrative anchors, not benchmarks.**
`LEGACY_SHA256_STARK_GAS_PER_PROOF`, `WIDER_HASH_STARK_GAS_PER_PROOF`,
and `RECURSIVE_STARK_OUTER_GAS_PER_PROOF` are pedagogical figures at
chain-tip 2026, chosen so the shape of the comparison is right. They are
not measured against any deployed verifier, and the chapter says so in
the same words. A production operator measures its own contract.

**`ETH_BLOCK_GAS_LIMIT` is a client-default recommendation, not a
consensus constant.** The 60,000,000 figure tracks EIP-7935, which is
Informational, so mainnet's observed limit can differ at any time. Every
per-block figure in the package moves with it. The constant is shared
with the Chapter 37 package so the two chapters cannot drift.

**`system_profile` records the inner verifier only.** Its `inner_only`
flag is set to `True` and its `outer_wrapper_note` says why: an outer
wrapper, if a system carries one, sits outside the four-layer model. The
ZKsync outer pairing wrapper is engineering inference from public
sources rather than a primary-specification claim, the same hedge
Chapter 35 attaches to the same statement. A caller reading the profile
alone must not conclude the system carries no Shor-broken cell.

**The Starknet anchor is the older Stone framing.** The
`Starknet-ethSTARK` entry in `SYSTEM_ANCHORS` records the ethSTARK and
Stone verifier that ran through 2025. Stwo replaced Stone on mainnet in
late October 2025, so the L1, L2, and L4 cells for Starknet should be
checked against the current specification rather than inherited from
this entry.

## Running the tests

From a clone of the companion repository:

```
pytest tests/ch40
```

The suite defaults to this tree. To grade a rebuild against it instead,
set `PQC_IMPL` to `exercises` and the same command runs against the stub
package, where every function the chapter teaches raises
`NotImplementedError` until you write it.
