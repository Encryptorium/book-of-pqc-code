# fiat-shamir-qrom (Chapter 33)

Classical pedagogical scaffolding for the Fiat-Shamir transform analyzed
in the quantum random oracle model. The package is stdlib only and runs
on Python 3.10 or later.

## Scope boundary (important)

This package does NOT simulate a quantum adversary. The quantum random
oracle model admits queries in superposition; classical Python cannot
faithfully reproduce that computational model. What this package does
is the next-best pedagogical vehicle: it models the classical reduction
that the measure-and-reprogram technique produces from a QROM adversary,
exposes the programming and reprogramming discipline that the technique
exploits, and makes the mechanics of Fiat-Shamir compilation concrete.

The quantum content lives in the chapter's prose (the measure-and-
reprogram lemma, the compressed-oracle alternative, the DFMS19 and
DFMS20 reduction losses). This package supports the prose by making
the classical side of those reductions runnable.

## Modules

| Module | What it models | What it does NOT model |
|---|---|---|
| `rom_simulator` | Classical random oracle with lazy sampling and explicit reprogramming discipline (cannot reprogram an already-queried input) | QROM queries in superposition; the full measure-and-reprogram ideal-vs-real indistinguishability |
| `fiat_shamir` | Schnorr three-move sigma protocol over the (p=2027, n=1013) toy group reused from Ch 32 `toy_kzg`, plus its Fiat-Shamir compilation via the ROM | Any real-world group; production Fiat-Shamir hash input formatting |
| `measure_and_reprogram` | Classical scaffolding of the DFMS19 measure-and-reprogram reduction: pick a random adversary query, record the input, reprogram the oracle at that input, re-run and confirm consistency | The quantum measurement that the real MR technique performs on a query register in superposition |

## Design invariant: no reprogramming after query

The `rom_simulator.RandomOracle.reprogram(x, value)` method raises
`ValueError` if `x` has already been queried. This mirrors the QROM
restriction that a programmed oracle must be programmed before the
adversary queries it; if the adversary has already observed the oracle
response at `x`, reprogramming that point retroactively rewrites the
adversary's view, which the reduction disallows.

## Running

From `solutions/ch33-fiat-shamir-qrom/`:

```
python3 -m pip install -e .
pytest ../../tests/ch33/
```

All tests must pass green; Chapter 33's rigor bar requires it.
