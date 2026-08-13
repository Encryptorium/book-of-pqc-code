# ch39-consensus-staking

Reference implementation for Chapter 39, *Consensus and staking signatures*.

The chapter picks a consensus signature rather than computing one, so this
package is byte arithmetic and status tables rather than cryptography. It holds
the per-validator-set byte budget across the five-candidate set, the threshold
scheme by candidate support matrix, and the Mosca-window rotation-cadence model
specialized to the consensus surface. Standard library only, no dependencies.

## Modules

| Module | What it holds |
|---|---|
| `consensus_staking.aggregation_overhead` | `CANDIDATES`, the five-row size and status table, plus the `ETH_VALIDATORS_2026` and `BLS_AGGREGATE_SIG_BYTES` anchors; `participation_bitmap_bytes` and `bls_aggregate_total_bytes`; `pq_total_bytes`, the three-branch per-set total; `aggregation_ratio`; `evaluate`, the per-candidate envelope; `per_set_bytes_against_baseline`, the whole table against the BLS baseline |
| `consensus_staking.threshold_compare` | `PRIMITIVES` and `THRESHOLD_ROLES`; `MATRIX`, the 5 by 3 support table built cell by cell by `_cell`; `lookup` for one cell; `deployment_summary`, the deterministic flattening; `production_ready_at`, the filter that returns BLS alone |
| `consensus_staking.consensus_mosca` | `STRAND_CONSENSUS_X` and `STRAND_CONSENSUS_Y`, the (2, 1) Strand anchor, and `CADENCE_NAMES`; `breach_years`; `cadence_options`; `recommend_cadence`; `evaluate`, which runs the recommendation at the Strand anchor |

## Running it

From a clone of the companion repository:

```
pytest tests/ch39
```

`PQC_IMPL=exercises pytest tests/ch39` runs the same suite against the stub tree
in `exercises/ch39-consensus-staking`.

## What the chapter prints and what it does not

Chapter 39 prints three blocks, all runnable as files under `chapter-code/ch39`.
Block 1 is a slice of `pq_total_bytes` and `per_set_bytes_against_baseline`
folded into one `per_set_bytes` function over a trimmed `CANDIDATES` literal that
carries only `sig_bytes` and `aggregates`. Block 2 is a slice of `MATRIX` with
each cell flattened to its status string alone. Block 3 is `breach_years` plus a
`recommend` that returns the two-tuple `recommend_cadence` computes and then
buries inside a larger dict.

What the page does not print: `participation_bitmap_bytes` and
`aggregation_ratio`; the `pk_bytes`, `deployment_status` and `notes` fields on
every `CANDIDATES` row; `evaluate` in either module; `lookup`,
`deployment_summary` and `production_ready_at`; the `admits_t_of_n`,
`requires_combine_round` and `rationale` fields on all fifteen matrix cells; and
the full `cadence_options` table with its feasibility, interval and
operational-cost fields.

## Scope boundary

**This package implements no signature scheme.** Nothing here signs, verifies,
aggregates, or generates a key under any of the five candidates it names. There
is no pairing, no lattice arithmetic and no hash tree; the BLS aggregation the
chapter analyzes is a fact about sizes here, not an operation. The executable
primitives are in Chapters 11, 12 and 17.

**The byte budget is a normalized comparison, not an Ethereum block estimate.**
Every per-set figure assumes N validators sign one message and the protocol
carries all N contributions in one payload. Real beacon-chain attestations split
across slots, committees and subnets, so the per-slot figure is a fraction of
these. The model isolates the aggregation effect, which holds at any subset; it
does not predict a block size.

**The deployment statuses are editorial readings of a moving landscape.**
`production`, `fips-final`, `pre-draft`, `research-grade`, `research-early` and
`incompatible` encode where each pairing sat at chain-tip 2026. Nothing here is
benchmarked and nothing tracks a standards body. Each label is pinned by a test
so it cannot drift silently, which makes them checkable rather than correct.

**FN-DSA-512's sizes are the Falcon submission's, not a FIPS 206 figure.** The
666-byte signature and 897-byte public key come from the Falcon specification
v1.2, the round-3 submission, where the parameter table gives public key
bytelength 897 and signature bytelength 666 at ring degree 512. FIPS 206 has
released neither an initial public draft nor a final standard, which is why the
`no-threshold` cell reads `pre-draft` rather than `fips-ipd`. Both figures can
move at finalization, and every FN-DSA number in the chapter moves with them.

**Threshold-ML-DSA is modeled, not implemented.** Its row assumes a deployable
combine protocol exists and asks only what the on-chain payload would cost:
one ML-DSA-65 signature plus the same participation bitmap BLS ships. No such
protocol is chain-deployable at chain-tip 2026, which is what the
`research-grade` status in both tables records. The off-chain combine round is a
flag, not a byte count, because those bytes never reach a block.

**The Mosca model treats the boundary as cleared.** `breach_years` returns
`X + Y - Z` without clamping, so a negative result reports headroom rather than
collapsing every safe case to zero, and `X + Y == Z` returns 0 and counts as
cleared. That follows the strict inequality in Chapter 36.

**`every-N-validator-rotations` is never recommended.** It matches
`every-N-epochs` on feasibility and on interval and loses on operational cost, so
`recommend_cadence` returns it only inside the `options` dict. It is in the model
because the chapter ranks four cadences, not three.
