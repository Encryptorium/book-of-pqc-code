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
wrapper, where a system carries one, sits outside this returned inner
profile. It does not sit outside the four-layer model. ZKsync Era's
outer pairing wrapper is documented architecture, not inference:
ZKsync's own Boojum announcement of 17 July 2023 says the STARK proofs
are wrapped with a non-transparent pairing-based SNARK and that it is
that SNARK which Ethereum verifies. What Chapter 35 hedges is the exact
construction the wrapper instantiates, which the announcement leaves
unnamed. The wrapper has its own L1 to L4 decomposition, and its
pairing L2 is the dominant Shor-vulnerable acceptance surface, so a
caller reading the inner profile alone must not conclude the system
carries no Shor-broken cell.

**The Starknet anchor records the root, and Starknet has two surfaces.**
The `Starknet-ethSTARK` entry in `SYSTEM_ANCHORS` records the ethSTARK
and Stone configuration. Stwo took over leaf proving on mainnet in late
October 2025, but it did not replace the recursion root: SHARP still
proves the root with Stone, which the Starknet documentation says is
deliberate, to avoid changing the deployed on-chain verifiers, and it
is that Stone proof the Solidity verifier on Ethereum reads. So the
entry's L1 and L2 cells describe the root and not the leaves, which run
an AIR over the Mersenne-31 prime field under Circle FRI. Its `L4` of
`SHA-256` is the book's own pedagogical transcript, not any deployed
Starknet channel: the published Solidity verifier draws its channel
randomness with Keccak-256. StarkWare announced on 31 March 2026 that
the L1 verifier will be changed to verify an S-two circuit proof; on
7 September 2026 no public record of that change shipping was found, so
it is pending rather than shipped. Chapter 40's Starknet walkthrough
states all of this.

## Running the tests

From a clone of the companion repository:

```
pytest tests/ch40
```

The suite defaults to this tree. To grade a rebuild against it instead,
set `PQC_IMPL` to `exercises` and the same command runs against the stub
package, where every function the chapter teaches raises
`NotImplementedError` until you write it.
