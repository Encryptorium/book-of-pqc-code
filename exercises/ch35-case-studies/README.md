# ch35-case-studies

Reference implementation for Chapter 35, *Case studies: Zcash, ZKsync, Starknet*.

The chapter is an analysis chapter, so this package is analysis apparatus rather
than a proof system. It holds the arithmetic that places a deployed
zero-knowledge system in the (L2, L4) grid and prices its post-quantum bit
margin. Standard library only, no dependencies.

## Modules

| Module | What it holds |
|---|---|
| `zk_case_studies.margins` | The three decoding radii, the composed FRI soundness budget, the DFMS20 challenge-width rule in exact and approximate form, and the pairing zero-margin result |
| `zk_case_studies.grid` | The L2 and L4 colour tables, the severity order, the dominance rule, and the `classify` entry point |
| `zk_case_studies.systems` | The six deployed configurations the chapter walks, and Stwo's published defaults |

## Running it

From a clone of the companion repository:

```
pytest tests/ch35
```

`PQC_IMPL=exercises pytest tests/ch35` runs the same suite against the stub
tree in `exercises/ch35-case-studies`.

## What the chapter prints and what it does not

Six routines here appear as listings in the chapter: `bit_margin_pairing`,
`shor_pairing_margin`, `stark_classical_margin`, `dfms20_required_cbits`,
`query_miss_bits`, and `classify`, together with the `L2_COLORS` and
`L4_COLORS` tables.

Four more exist because the chapter states them in prose and never prints them.
`decoding_radius` is the three radii of Ch 34 Section 5.1 as one function.
`composed_margin` is the budget with its three terms kept apart rather than
summed away, which is what the prose needs when it asks which term dominates.
`dfms20_exact_cbits` is the exact challenge-width bound the Block 3 comment
describes but does not compute. `posture` is the per-system lookup that the
five-step case-study procedure produces.

## Scope boundary

**This package computes bounds. It does not prove or verify anything.** There is
no prover, no verifier, no commitment, and no transcript here. Chapter 34's
`ch34-starks` package is the executable STARK; this one is the calculator that
reads such a system's parameters and reports where it lands.

**Every margin here is a model, not a security claim.** The composed budget is
the three-term form Ch 34 Section 5.5 derives, which omits terms a production
soundness analysis prices. Two consequences follow, and both are load-bearing.
A number this package returns for a deployed system is what the model says at
those parameters, not what the system's own analysis claims. And where a
published figure and a figure computed here disagree, the disagreement is
evidence about the model, not about the deployment.

**The parameters are illustrative except for one system.** The Boojum and
ethSTARK parameter points in the chapter are reference-like configurations,
because neither project publishes parameters at that granularity. Stwo is the
exception: `STWO_DEFAULTS` carries the triple published in the
`starkware-libs/stwo-cairo` README, and it is the only entry in this package
that is quoted rather than modelled.

**Margins are quoted at the Johnson radius by default.** `composed_margin` takes
a `regime` argument and defaults to `"johnson"`, because that is the radius at
which BCIKS Theorem 1.2 proves the proximity gap. The `"capacity"` regime is
available because deployed pipelines use it, not because it is sound: the
conjectures supporting it were disproved in late 2025. Asking this package for a
capacity-regime number is asking what a deployment claimed, not what is proven.
