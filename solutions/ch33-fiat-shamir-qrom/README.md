# fiat-shamir-qrom (Chapter 33)

Classical pedagogical scaffolding for the Fiat-Shamir transform analyzed
in the quantum random oracle model. The package is stdlib only and runs
on Python 3.10 or later.

## Scope boundary (important)

This package does NOT simulate a quantum adversary. The quantum random
oracle model admits queries in superposition; classical Python cannot
faithfully reproduce that computational model. What this package does
is the next-best pedagogical vehicle: classical scaffolding for the
measure-and-reprogram reduction, which exposes the programming and
reprogramming discipline the technique exploits and makes the mechanics
of Fiat-Shamir compilation concrete. The reduction the technique
actually constructs is not classical. DFMS Theorem 2 builds a two-stage
*quantum* algorithm that runs the adversary, measures one of its q + 1
query registers, and resumes the adversary against the reprogrammed
oracle. The two classical runs here exhibit the algebraic invariant that
reduction turns on; they are not the reduction.

The quantum content lives in the chapter's prose (the measure-and-
reprogram lemma, the compressed-oracle alternative, the DFMS19 and
DFMS20 reduction losses). This package supports the prose by making
the classical side of those reductions runnable.

## Modules

| Module | What it models | What it does NOT model |
|---|---|---|
| `rom_simulator` | Classical random oracle with lazy sampling and explicit reprogramming discipline (cannot reprogram an already-queried input) | QROM queries in superposition; the measurement of a query register and the probability relation DFMS Theorem 2 proves from it |
| `fiat_shamir` | Schnorr three-move sigma protocol over the (p=2027, n=1013) toy group reused from Ch 32 `toy_kzg`, plus its Fiat-Shamir compilation via the ROM | Any real-world group; production Fiat-Shamir hash input formatting |
| `measure_and_reprogram` | Classical scaffolding of the DFMS19 measure-and-reprogram reduction: pick a random adversary query, record the input, reprogram the oracle at that input, re-run and confirm consistency | The quantum measurement that the real MR technique performs on a query register in superposition |

## Design invariant: no reprogramming after query

The `rom_simulator.RandomOracle.reprogram(x, value)` method raises
`ValueError` if `x` has already been queried. This is a local API
choice, and it is not a QROM restriction. Measure-and-reprogram
reprograms one of the adversary's own queries and lets the adversary
keep running against the changed oracle; nothing in DFMS19 or DFMS20
requires the reprogrammed point to be unqueried, and Chapter 33 says an
adversary that queried it classically on both sides sees the change with
probability 1 - 1/|Y|. What the theorem controls is success probability,
by a factor of (2q + 1)^2, not whether the change is noticed. The
restriction here keeps the classical simulator's lazy-sampling table
consistent within a single run, so a test can state one invariant about
the two runs.

## Running

From `solutions/ch33-fiat-shamir-qrom/`:

```
python3 -m pip install -e .
pytest ../../tests/ch33/
```

All tests must pass green; Chapter 33's rigor bar requires it.
