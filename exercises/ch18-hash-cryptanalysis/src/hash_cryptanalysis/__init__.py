"""Chapter 18: the generic-attack arithmetic behind SLH-DSA's security claims.

This package computes; it does not sign. Chapter 17 builds SLH-DSA itself, and
`solutions/ch17-slh-dsa` is where a working signer lives. What is here is the
analysis the chapter runs *on* that construction, factored so each number the
chapter prints has a function behind it and a test under it.

- `params` holds FIPS 205's six SHA-2 parameter sets as data, plus the WOTS+
  chain count `ell` that every size and target count depends on.
- `multitarget` counts signature components and preimage targets, and turns a
  target population into a bit-security reduction, classically and under Grover.
- `fors_reuse` is the FORS few-time analysis: the exact coverage probability,
  the `q << t` approximation the literature quotes, and the first reuse count
  that crosses a stated threshold.
- `quantum` prices generic preimage and collision search, classical and quantum.
- `countermeasures` prices verify-after-sign and constant-time WOTS+ chaining.

Standard library only.
"""
