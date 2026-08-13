# ch30-migration-program

Operator tooling for Chapter 30, "Running a PQ migration program". Three
independent helpers that a program lead runs against a migration in flight:

- `risk_rollup.migration_urgency` ranks Ch 25 CBOM touchpoints by quantum
  migration urgency, weighting each touchpoint's PQRA readiness gap by its
  quantum status and its exposure.
- `phase_gate.check` tests a gate record against a named phase's exit criteria
  and reports what is missing, in the order a runbook should walk it.
- `milestone_tracker.report` turns a dated milestone list into a percentage
  complete and a list of slipped milestones.

## Running it

From a clone of the companion repository:

```
pytest tests/ch30
```

The suite runs against this tree by default. `PQC_IMPL=exercises pytest
tests/ch30` runs the same suite against `exercises/ch30-migration-program`,
where the three functions above are stubs, and grades your implementations.

The package is standard library only (`collections.abc`, `dataclasses`,
`datetime`) and needs no install: the suite's `conftest.py` puts `src/` on
`sys.path`. Appendix C covers the environment.

## What this package is not

**It is not cryptography, and nothing here is a cryptographic control.** The
package computes weighted sums, set differences, and date comparisons. A green
suite says the arithmetic and the input guards are right. It says nothing
whatever about the post-quantum security of anything the program migrates; that
lives in Chapters 11, 12, 17 and the deployment chapters that precede this one.

**The per-touchpoint use of the PQRA is an adaptation, not the PQRA's own
scope.** The published Encryptorium Post-Quantum Readiness Assessment v1.0
scores an *organization* against seven weighted domains and rolls the result
into one dashboard score with four risk tiers. This package applies the same
seven domains and the same weights to *each touchpoint*, so that a CBOM can be
ranked within one organization. The rubric supports the domains and the
weights; it does not define this use of them.

**The two multipliers are the chapter's, not the rubric's.** `QUANTUM_MULT`
(vulnerable 3, grover-only 1, quantum-safe 0) and `EXPOSURE_MULT` (public 2,
internal 1) are Chapter 30's construction on top of the PQRA. The assessment
framework defines no quantum-status or exposure multiplier; it mentions
exposure only in prose.

**The package computes no PQRA risk tier.** The rubric's Critical / High /
Moderate / Low categories are not implemented here at all. `migration_urgency`
returns a raw score with no banding, and no test asserts a tier.

**The four phase names and their exit criteria are the chapter's.** The phase
*dates* are anchored to the NCSC 2025 timeline and the CNSA 2.0 documents,
which set milestones. Neither sets gate criteria, and neither names these four
phases. `PHASE_EXIT_CRITERIA` is a worked example a program would replace with
its own.

**`milestone_tracker` is deliberately phase-agnostic.** It does not know which
milestones belong to which phase, and it does not prioritise: it preserves
input order in the slipped tuple. Coupling milestones to phases is a policy
choice the chapter leaves to the program.

## What the suite does not establish

33 tests, all pure functions over in-memory data.

- **No persistence, concurrency, or I/O is exercised, because the package does
  none.** There is no file handle, no lock, no database, and no second process
  or thread anywhere in the package or its tests. A real program tracker
  outlives a process; this one does not try to.
- **The readiness scores in the running example are illustrative.** Nothing
  establishes that a real `password_hashing` touchpoint scores 3 on migration
  readiness. The scores are chosen to produce the ordering the chapter
  discusses.
- **The rankings are asserted as orderings, not as values**, except where a
  test pins a specific number (`test_maximum_priority_is_24`, and the
  quantum-safe entries at 0.0). A change that moves every score by a constant
  factor would pass most of the ordering tests.
- **One thing the suite now does establish, and did not until 2026-08-13.**
  `test_each_domain_carries_its_own_pqra_weight` pins each domain to its own
  PQRA weight. Before it, `DEFAULT_PQRA_WEIGHTS` was checked only for summing
  to 1.0 and for covering every domain, and both of those survive a
  permutation. Swapping the `inventory` and `standards_compliance` weights was
  confirmed to pass all 32 then-existing tests while making the package
  disagree with the rubric it implements and moving real scores.
