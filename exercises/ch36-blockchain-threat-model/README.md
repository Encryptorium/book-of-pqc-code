# ch36-blockchain-threat-model

Reference implementation for Chapter 36, *Quantum threat model for blockchains*.

The chapter is a threat-model chapter, so this package is bookkeeping rather
than cryptography. It holds the lookup that assigns a deployed blockchain
primitive to a quantum-vulnerability class, and the arithmetic that turns
Mosca's three parameters into an exposure window. Standard library only, no
dependencies.

## Modules

| Module | What it holds |
|---|---|
| `blockchain_threat.surface_taxonomy` | `PRIMITIVE_CLASSIFICATION`, the sixteen-entry primitive-to-class table; `classify` for one asset record; `classify_all` for a list, preserving input order |
| `blockchain_threat.mosca_window` | `evaluate`, the exposure window `max(x + y - z, 0)` with its input contract |

## Running it

From a clone of the companion repository:

```
pytest tests/ch36
```

`PQC_IMPL=exercises pytest tests/ch36` runs the same suite against the stub tree
in `exercises/ch36-blockchain-threat-model`.

## What the chapter prints and what it does not

Chapter 36 prints two blocks, both of them runnable as files under
`chapter-code/ch36`. Block 1 prints `classify` with the same body this package
carries, plus a seven-entry slice of `PRIMITIVE_CLASSIFICATION` and the
five-record Strand asset list. Block 2 prints the window arithmetic under the
name `mosca_window`.

Two things here are not on the page. `classify_all` is the list walk the chapter
names and describes in the paragraph above Block 1 but never prints, which is
why the exercise tree stubs it. `evaluate` is the printed `mosca_window` with
its input contract added: the printed body asserts non-negativity only, while
this one also rejects non-integers and rejects `bool`, because Python's `bool`
subclasses `int` and `True` would otherwise pass silently as one year.

## Scope boundary

**This package implements no cryptographic primitive.** There is no signature,
no hash, no key, and no curve arithmetic anywhere in it. It is a dictionary
lookup and a subtraction. Nothing here computes, verifies, or attacks anything;
Chapters 11, 12 and 17 hold the executable primitives this table only names.

**A class is a routing decision, not a security level.** `shor-vulnerable` says
a polynomial-time quantum break exists against the underlying assumption, so the
surface needs a primitive swap. `hash-quantum-degraded` says the effective
security level falls but no polynomial-time break follows, so the surface is a
parameter-bump candidate. `post-quantum-standardized` says a final standard
exists, and nothing more: it is the migration target, not a claim that the
scheme is unconditionally secure. Ranking two primitives inside one class is
outside what this table can support.

**The third class tracks a standard's status on a date, and status moves.**
FN-DSA (Falcon) is deliberately absent for that reason. FIPS 206 was under
development at chain-tip 2026 with no Initial Public Draft released, so no final
parameter set existed to classify, and an asset record naming `FN-DSA-512`
therefore crashes on the unknown-primitive assertion rather than being labelled
standardized. Adding it back is a one-line edit once FIPS 206 is final; the
crash is the reminder to make that edit deliberately.

**The Strand numbers are a fixture, not a measurement.** The per-surface `X` and
`Y` values the tests pin come from the chapter's running example on a fictional
chain, and the transaction surface's `X` of 50 years is a stand-in for an
archival horizon the chapter describes as effectively unbounded. They are there
so the arithmetic has something to chew on and so a later chapter cannot quietly
reassign them, not because any of them was measured on a deployed chain.
