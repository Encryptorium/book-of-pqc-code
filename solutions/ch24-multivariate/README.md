# Chapter 24 multivariate: a toy Unbalanced Oil and Vinegar

This package is the working code for Chapter 24 of the Encryptorium Book of
Post-Quantum Cryptography. Chapter 24 is a survey rather than a from-scratch
build, so this package is smaller in ambition than the flagship chapters: it
implements the Oil-Vinegar trapdoor end-to-end at parameters a reader can hold
in their head, and it carries the key-size and attack-cost arithmetic behind
the chapter's four-family comparison table.

It is a toy. It is not UOV, and it must not sign anything.

## Layout

| Module | Contents |
| --- | --- |
| `multivariate.gf` | GF(q) inversion by the Fermat power, and the matrix operations `matmul`, `transpose`, `mat_vec`, `quadratic_eval` |
| `multivariate.linalg` | Gaussian elimination over GF(q): `is_invertible`, `invert_mat`, `solve_linear` |
| `multivariate.uov` | `UOVParams`, key generation, the oil-vinegar collapse, `sign`, `verify` |
| `multivariate.sizes` | Public-key size arithmetic, the Kipnis-Shamir cost model, and `ROUND2_SIZES` |

Standard library only: `random`, `dataclasses`, and `math`. No NumPy.

## Running it

From a clone of the companion repository:

```
pytest tests/ch24
```

43 tests across four files: 12 in `test_gf_linalg.py`, 7 in `test_trapdoor.py`,
9 in `test_uov_roundtrip.py`, and 15 in `test_sizes.py`.

`test_uov_roundtrip.py` includes `test_signature_reproduces_the_chapter_output`,
which asserts that seeding key generation with `random.Random(0)` and signing
with `random.Random(1)` produces the signature `[4, 4, 4, 2, 3]` that the
chapter prints. The chapter's inline listings and this package are the same
code with the same draw order, and that test is what keeps them from drifting.

To grade your own version against the same suite:

```
PQC_IMPL=exercises pytest tests/ch24
```

## What is stubbed in the exercises tree, and what is not

`exercises/ch24-multivariate` stubs six functions. Chapter 24 prints its entire
toy end-to-end, and a function the chapter prints is handed over rather than
stubbed, so the six are the ones the chapter explains but never prints: the
oil-oil block extraction, the `n > 2m` predicate, the two public-key-size
computations, and the two Kipnis-Shamir cost models.

Because so much is handed over, 28 of the 43 tests still pass against the
stubbed tree. `test_gf_linalg.py` and `test_uov_roundtrip.py` pass in full;
`test_trapdoor.py` fails 4 of 7 and `test_sizes.py` fails 11 of 15.

## Divergences from the round-2 UOV specification

Figures below are from version 2.0 of the UOV specification, dated
2025-02-05. They are round-2 figures. NIST IR 8610 (May 2026) advanced UOV to
the third round and anticipates a longer timeline before any multivariate
scheme is standardized, so a third-round tweak could move all of them.

| Axis | uov-Is (round 2) | This toy |
| --- | --- | --- |
| Field | GF(16), an extension field | GF(7), prime, so inversion is `pow(x, q - 2, q)` |
| Variables | `n = 160`, `n_v = 96`, `n_o = m = 64` | `n = 5`, `n_v = 3`, `n_o = m = 2` |
| Unbalance ratio `n / m` | 2.5 | 2.5, but at a search exponent of `q^1` rather than `q^32` |
| Message handling | `t = Hash(message || salt)`, 16-byte salt, one-byte counter | Target vector supplied directly; no hashing, no salt |
| Vinegar derivation | Pseudorandom from message, salt, secret seed and counter | Uniform from a caller-supplied `random.Random` |
| Public key | 412,160 bytes expanded, 66,576 bytes compressed | `m` explicit `n x n` matrices |
| Signature | 96 bytes | A list of `n` field elements |
| Security argument | EUF-CMA for salt-UOV, with the round-2 attack survey behind it | None |

The toy is several orders of magnitude too small to resist any of the attacks
the chapter describes. Its Kipnis-Shamir search exponent is `q^(n - 2m) = 7`,
against `16^32` for uov-Is, so recovering the oil subspace is a matter of
trying seven candidates. There is no key compression, no constant-time
discipline, and no known-answer-test harness: `tests/ch24/` carries no
`test_vectors.py`, and this package makes no byte-for-byte compatibility claim
against the UOV submission.

## Where the recorded sizes come from

`ROUND2_SIZES` in `multivariate.sizes` records public-key and signature sizes
for seven parameter sets, each with the table it was read from: UOV Table 1,
MAYO Table 2.1, SNOVA Table 6. `test_sizes.py` recomputes both UOV expanded-key
entries from `uov_public_key_bytes` and checks them against the recorded
figures, so the chapter's 412,160-byte claim is derived rather than
transcribed. The 278,432-byte uov-Ip figure is recomputed the same way; the
chapter does not quote it.

The recorded MAYO and SNOVA figures are not recomputed. They are transcriptions
from those specifications, and `test_round2_sizes_are_internally_consistent`
checks only that every entry names a source and a NIST level.
