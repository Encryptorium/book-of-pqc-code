# ch37-l1-signature-migration

Reference implementation for Chapter 37, *Layer-1 signature migration: Bitcoin
and Ethereum*.

The chapter costs a migration rather than performing one, so this package is
arithmetic rather than cryptography. It holds the four-candidate size table, the
two per-block throughput models that table feeds, and the composite-overhead
arithmetic. Standard library only, no dependencies.

## Modules

| Module | What it holds |
|---|---|
| `l1_migration.byte_budget` | `CANDIDATES`, the four-row size and output-shape table; the per-candidate accessors `signature_bytes`, `public_key_bytes` and `witness_reveals_pk`; `witness_bytes`; the Bitcoin model `transactions_per_btc_block`; the two Ethereum models `transactions_per_eth_block_calldata` and `transactions_per_eth_block_calldata_floor` with their gas helpers `calldata_gas` and `calldata_floor_gas`; and `evaluate`, which assembles all of it for one candidate |
| `l1_migration.throughput_compare` | `rank`, the deterministic per-budget ordering; `relative_throughput`, a candidate's throughput as a fraction of a baseline's |
| `l1_migration.composite_overhead` | `PRIMITIVE_SIZES` and `COMPOSITES`; `overhead` and `overhead_ratio`, the composite-versus-component byte arithmetic |

## Running it

From a clone of the companion repository:

```
pytest tests/ch37
```

`PQC_IMPL=exercises pytest tests/ch37` runs the same suite against the stub tree
in `exercises/ch37-l1-signature-migration`.

## What the chapter prints and what it does not

Chapter 37 prints two blocks, both runnable as files under `chapter-code/ch37`.
Block 1 is a slice of `evaluate`: it computes the same signature, public-key and
witness figures and the same two per-block counts, and returns them as a
four-tuple. Block 2 is a slice of `rank` with the same ordering and the same
alphabetical tie-break.

What the page does not print: the EIP-7623 data-floor model
(`calldata_floor_gas` and `transactions_per_eth_block_calldata_floor`), which
the chapter tabulates but never codes; the `deployment_shape` label that
`evaluate` carries for each candidate; `relative_throughput`; and the whole of
`composite_overhead`, which the chapter states as prose percentages and
Appendix D Exercise 2 works by hand.

## Scope boundary

**This package implements no cryptographic primitive.** Nothing here signs,
verifies, hashes, or touches a curve or a lattice. It is a lookup table and some
division. The executable primitives whose sizes it quotes are in Chapters 11, 12
and 17.

**The Bitcoin post-quantum rows model an output type that does not exist.**
BIP-360 P2MR is a real draft proposal and it defines no post-quantum signature
scheme. The commit-then-reveal witness these figures assume, where the output
script hash-commits to the post-quantum public key and the spend reveals both
key and signature, belongs to a separate soft fork nobody has drafted. The
`witness_reveals_pk` flag is where that assumption lives, and it is an
assumption, not a specification.

**The Ethereum figures are a lower bound on cost and therefore an upper bound on
throughput.** Both models count transaction base gas plus signature calldata and
nothing else. Neither counts the cost of running an ML-DSA or SLH-DSA verifier
in EVM bytecode, which has no precompile and runs to millions of gas per call.
Real per-block post-quantum throughput on Ethereum sits well below
`transactions_per_eth_block_calldata_floor`.

**The sizes are standards figures; the ECDSA row is not.** ML-DSA-65 and
SLH-DSA-128s come from FIPS 204 and FIPS 205 Table 2, and Ed25519 from RFC 8032.
The 64-byte ECDSA figure is the canonical `(r, s)` lower bound rather than
Bitcoin's on-chain encoding, which wraps the same pair in 70 to 72 DER bytes
plus a sighash flag. Comparisons against the ECDSA row are therefore generous to
ECDSA by a few bytes.

**Two anchors are conventions rather than consensus rules.**
`BTC_TX_OVERHEAD_WU` is 380 weight units for a typical 1-in-1-out segwit
transaction: the 94-byte stripped serialization at 4 weight units per
non-witness byte per BIP-141 (376 units) plus roughly 4 units of witness
framing. Real overhead varies with transaction shape.
`ETH_BLOCK_GAS_LIMIT` is 60 million per EIP-7935, which is an Informational
client-default recommendation that any validator may configure away from, not a
consensus-pinned constant like `BTC_BLOCK_WEIGHT_LIMIT`.

**BIP-360's draft version is deliberately not recorded here.** It moves faster
than this package does. The chapter and its bibliography entry carry the version
and the date it was read.
