# ch34-starks

Chapter 34 standalone package: a pedagogical end-to-end FRI-based STARK
over `F_97` with the length-8 Fibonacci trace as the running example.

## Modules

- `arithmetization.py`: AIR (Algebraic Intermediate Representation).
  `TransitionConstraint`, `BoundaryConstraint`, `AIR`, `fibonacci_air`,
  `evaluate_air`, `interpolate_trace`.
- `lde.py`: low-degree extension and the field arithmetic it needs.
  `mod_inv`, `eval_poly`, `trace_domain`, `lde_domain`,
  `extend_polynomial`, `vanishing_polynomial`. There is no composition
  polynomial here; Chapter 34 Section 4.5 explains why the toy drops it.
- `fri_full.py`: FRI proximity with per-round Fiat-Shamir challenges,
  grinding, and Merkle commitments. `FRIProof`, `commit_codeword`,
  `fri_prove`, `fri_verify`.
- `transcript.py`: Fiat-Shamir transcript built on SHA-256.
  `Transcript`.
- `prover.py`: end-to-end prover. `STARKProof`, `stark_prove`.
- `verifier.py`: end-to-end verifier. `stark_verify`.

## Running example

Length-8 Fibonacci trace `(1, 1, 2, 3, 5, 8, 13, 21)` over `F_97`.
Blowup factor 4 gives LDE domain size 32 (2^5, the largest power-of-two
subgroup of `F_97^*`). The AIR has one transition constraint
`trace[i+2] - trace[i+1] - trace[i] == 0` and two boundary constraints
`trace[0] == 1`, `trace[1] == 1`.

## Scope boundary

Three things this package is not, none of which the module names give away.

**It is not zero-knowledge.** The prover sends the trace in the clear
alongside the FRI proof. A production STARK hides the trace behind a
composition polynomial, a random linear combination of the constraint
quotients that FRI also proves low-degree, and this package has no
composition polynomial at all. Chapter 34 Section 4.5 explains what that
buys and what it costs; the soundness argument still closes, via a
consistency check binding the sent trace to the committed codeword, but
the "ZK" in zk-STARK is absent by construction.

**It implements nothing standardised**, so there is no specification to be
byte-compatible with and no known-answer tests to match. FRI, AIR and the
Fiat-Shamir transcript here follow the chapter's own conventions.

**Its parameters are vacuous, deliberately.** `F_97` is far too small to
support the BCIKS proximity-gap error term at any useful proximity
parameter, which needs a field at least quadratic in the domain size.
What the package demonstrates is the mechanics of arithmetization,
low-degree extension, folding, transcript binding and grinding. It is not
a security parameter set and no bit-level claim should be read off it.
Chapter 34 Section 5.2 states this in full.

## Tests

See `tests/ch34/` for the pytest suite. Run from the repo root:

```
pytest tests/ch34/
```

## Discipline

- Standard library only. No third-party dependencies.
- Eager validation: `raise ValueError` on malformed input; no
  try/except; no boolean short-circuits around `raise`.
- Chapter 34 inline code blocks re-declare the same helpers stdlib-only.
