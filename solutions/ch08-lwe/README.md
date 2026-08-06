# ch08-lwe

Standalone Python package for Chapter 8 of the Encryptorium Book of PQC. Implements the learning with errors (LWE) problem over $\mathbb{Z}_q$ with a small discrete parameter tuple: the `LWEParams` dataclass, sampling routines for the secret, the error, and both search and decisional LWE instances, noise-free Gaussian elimination over $\mathbb{Z}_q$ by modular inverse, and the q-ary lattice $\Lambda_q^\perp(A) = \{x \in \mathbb{Z}^m : A^\top x \equiv 0 \pmod q\}$, which is the object behind the dual distinguishing attack. Search LWE reduces to bounded-distance decoding on the primal companion $\Lambda_q(A) = A \mathbb{Z}^n + q \mathbb{Z}^m$; this package builds a basis for $\Lambda_q^\perp(A)$ only.

## Layout

- `src/lwe/params.py` — `LWEParams` dataclass with strict `__post_init__` asserts
- `src/lwe/sample.py` — `sample_secret`, `sample_error`, `sample_lwe`, `sample_uniform`
- `src/lwe/solve.py` — `gaussian_eliminate_mod_q` (noise-free recovery over $\mathbb{Z}_q$)
- `src/lwe/qary.py` — `qary_lattice_basis` returning an integer basis of $\Lambda_q^\perp(A)$

## Tests

Run from the repo root:

```
pytest tests/ch08/
```

The test suite covers parameter validation, sample shapes and types, noise-free recovery, noise breaking recovery, and the q-ary lattice orthogonality and determinant identities.

## Relationship to later chapters

Chapters 9, 10 and 11 rebuild these ideas rather than import them. Each ships its own package (`ring_lwe`, `regev_pke`, `mlkem`) with its own parameter type and samplers, because the objects change: Ring-LWE and Module-LWE sample polynomials instead of vectors, and ML-KEM fixes its parameters to FIPS 203. Nothing outside `tests/ch08/` imports `lwe`.
