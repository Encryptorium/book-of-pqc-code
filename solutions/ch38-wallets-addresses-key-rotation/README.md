# ch38-wallets-addresses-key-rotation

Reference implementation for Chapter 38, *Wallets, addresses, and key rotation*.

The chapter decides a wallet's shape rather than operating one, so this package
is tables and arithmetic rather than cryptography. It holds the custody-shape by
primitive fit matrix, the BIP-32 property-survival map with a byte-level path
walker, and the Mosca-window rotation-cadence model. Standard library only, no
dependencies.

## Modules

| Module | What it holds |
|---|---|
| `wallet_rotation.custody_fit` | `CUSTODY_SHAPES` and `PRIMITIVES`; `MATRIX`, the 6 by 4 fit table built row by row by `_row`; `lookup` for one cell; the `candidates_for_shape` and `shapes_for_primitive` views; `evaluate`, which flattens the whole matrix in a deterministic order |
| `wallet_rotation.derivation_tree` | `PROPERTIES`, the per-primitive survival map, and `HARDENED_OFFSET`; `parse_path`; the accessors `properties` and `watch_only_supported`; `derive_step` and `derive`, the byte-level path walk; `evaluate`, the per-primitive report |
| `wallet_rotation.mosca_wallet` | `STRAND_WALLET_X` and `STRAND_WALLET_Y`, the (10, 4) Strand anchor, and `CADENCE_NAMES`; `breach_years`; `cadence_options`; `recommend_cadence`; `evaluate`, which runs the recommendation at the Strand anchor |

## Running it

From a clone of the companion repository:

```
pytest tests/ch38
```

`PQC_IMPL=exercises pytest tests/ch38` runs the same suite against the stub tree
in `exercises/ch38-wallets-addresses-key-rotation`.

## What the chapter prints and what it does not

Chapter 38 prints three blocks, all runnable as files under `chapter-code/ch38`.
Block 1 is a slice of the fit matrix that recomputes each cell's label from
per-shape flags instead of reading `MATRIX`. Block 2 is a slice of `derive_step`
and the path walk in `derive`, printing the per-step `supported` flag. Block 3 is
a slice of `breach_years` and `recommend_cadence`, minus the options table.

What the page does not print: the full `cadence_options` table with its
feasibility, interval and operational-cost fields; `candidates_for_shape`,
`shapes_for_primitive` and both `evaluate` functions; `parse_path`; the
`rationale` strings every row carries; and `watch_only_supported`, whose
conclusion the chapter states in prose.

## Scope boundary

**This package implements no signature scheme.** Nothing here signs, verifies, or
generates a key under any of the six candidates it names. `derive_step` runs real
HMAC-SHA-512, and that is the only cryptographic operation in the package. The
executable primitives whose derivation properties it tabulates are in Chapters
11, 12 and 17.

**Non-hardened derivation is a placeholder, not an implementation.** Real BIP-32
non-hardened derivation hashes the serialized parent public key and then offsets
the parent public key on the primitive's group. `derive_step` substitutes the
parent secret as opaque bytes so the walk can continue past a non-hardened step
without per-primitive public-key arithmetic. The bytes it returns in that branch
are **not** valid BIP-32 child keys. The derivation decision the chapter actually
makes lives in `PROPERTIES` and in the per-step `supported` flag, not in those
bytes.

**The fit labels are editorial judgments, not measurements.** `legacy`, `fit`,
`marginal` and `unfit` encode the chapter's reading of state-management
tolerance and signature-size economics. No cell is benchmarked. The `marginal`
label on the two stateful schemes at `single-device-hot` rests on what NIST
SP 800-208 effectively assumes about one-time-signature state discipline, which
is a judgment about consumer hardware rather than a rule the document states.

**The signature sizes are standards figures; the byte-budget conclusions are
not.** The 3309-byte ML-DSA-65 and 7856-byte SLH-DSA-128s figures come from
FIPS 204 and FIPS 205 Table 2, and the 3373-byte composite figure is the
3309 + 64 lower bound. Whether those sizes make a cell `fit` or `marginal` is
the chapter's call.

**The Mosca model treats the boundary as cleared.** `breach_years` returns
`X + Y - Z` without clamping, so a negative result reports headroom rather than
collapsing every safe case to zero, and `X + Y == Z` returns 0 and counts as
cleared. That follows the strict inequality in Chapter 36; a different reading of
the boundary changes the recommendation at exactly one point.

**`every-N-transactions` is never recommended.** It matches `every-N-years` on
feasibility and loses on operational cost, so `recommend_cadence` returns it only
inside the `options` dict. It is in the model because the chapter ranks four
cadences, not three.
