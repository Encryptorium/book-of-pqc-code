# ch09-ring-lwe

Standalone Python package for Chapter 9 of the Encryptorium Book of PQC. Implements Ring-LWE and Module-LWE over the polynomial ring $R_q = \mathbb{Z}_q[x]/(x^n + 1)$ with $n$ a power of two: the `RingParams` and `ModuleParams` dataclasses, schoolbook negacyclic multiplication in $R_q$, the negacyclic number theoretic transform at any prime $q$ with $2n \mid q - 1$, and sampling routines for Ring-LWE and Module-LWE instances.

## Layout

- `src/ring_lwe/params.py` — `RingParams` and `ModuleParams` dataclasses with strict `__post_init__` asserts
- `src/ring_lwe/ring.py` — `ring_add` and `ring_mul_naive` (schoolbook negacyclic convolution)
- `src/ring_lwe/ntt.py` — `ntt_forward`, `ntt_inverse`, `ring_mul_ntt` (direct-definition NTT and the forward-pointwise-inverse multiplication path)
- `src/ring_lwe/sample.py` — `sample_ring_secret`, `sample_ring_error`, `sample_ring_uniform`, `sample_ring_lwe`, `sample_module_lwe`

## Tests

Run from the repo root:

```
pytest tests/ch09/
```

The test suite covers parameter validation, hand-computable negacyclic wraparound, NTT round-trip identity at $(n, q, \psi) = (4, 17, 2)$ and $(8, 17, 3)$, agreement between `ring_mul_ntt` and `ring_mul_naive`, Ring-LWE sample shapes and the defining identity $b = a \cdot s + e$, and the sample-for-sample collapse of Module-LWE at rank $k = 1$ to Ring-LWE under identical seeds.

## What reuses this package

Nothing outside `tests/ch09/` imports `ring_lwe`. Chapters 10 and 11 rebuild
these ideas rather than import them: Chapter 10 ships `regev_pke` and works over
flat LWE, and Chapter 11 ships `mlkem` with its own partial NTT for
$R_{3329} = \mathbb{Z}_{3329}[x]/(x^{256}+1)$ per FIPS 203. The inline numpy
blocks in Chapter 9 are a simplified slice of the functions here.
