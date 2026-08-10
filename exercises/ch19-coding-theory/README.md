# ch19-coding-theory

Coding theory foundations for Part IV of the Encryptorium Book of PQC. GF(2)
matrix arithmetic, the [7,4,3] Hamming code, binary Goppa code basics, and
Prange information-set decoding. Standard library only, CPython 3.10+.

```
pytest tests/ch19                      # 24 tests against this package
PQC_IMPL=exercises pytest tests/ch19   # against the stubbed rebuild track
```

## What this package is and is not

This is a teaching package for the concepts Part IV builds on. It is not a
cryptographic implementation and nothing here should be used to protect
anything. Chapter 20 builds Classic McEliece and Chapter 21 builds HQC; this
package supplies the vocabulary those two need.

There is no reference specification to conform to and therefore no known-answer
test. The book's rigor bar requires official NIST vectors for flagship
implementations (ML-KEM from FIPS 203, ML-DSA from FIPS 204, SLH-DSA from
FIPS 205); coding theory primitives have no such document, so correctness here
is pinned by structural properties instead: that `G * H^T` is zero, that every
single-bit error produces the column of `H` at its position, that every Goppa
parity-check column is nonzero, and that Prange recovers the error it was given.

Four deliberate limitations, each of which the chapter states in prose:

- **`goppa.py` is a `t = 1` construction over GF(2^3).** The support is seven
  elements and the parity-check matrix is 3-by-7. A code this small hides
  nothing at all; it exists to show the shape of the trapdoor, not to be one.
  The full construction over GF(2^12) is Chapter 20's.
- **`isd.py` implements Prange only**, the 1962 baseline. Lee-Brickell, Stern,
  MMT, BJMM and May-Ozerov all improve on it and none is implemented here. Cost
  estimates from `isd_cost_estimate` are Prange iteration counts and are not a
  security estimate for any real parameter set; the chapter's table gives the
  asymptotic exponents and the reason concrete parameters come from finite-`n`
  estimators instead.
- **`prange_isd` uses `random.Random`**, which is not a cryptographic generator.
  It is the right choice here because the randomness drives an attack search,
  not a key, and seeding it makes the tests deterministic.
- **`hamming.py` fixes one code**, the [7,4,3] Hamming code, with `H` in the
  systematic form `[A | I_3]`. Its columns run 110, 101, 011, 111, 100, 010,
  001, which is a different ordering from the ascending-binary convention many
  textbooks use. Both are valid; this one is chosen because it pairs directly
  with the systematic generator matrix `G = [I_4 | A^T]`, so `G * H^T = 0`
  holds by construction.

## Layout

| Module | Contents |
|---|---|
| `gf2.py` | Vector and matrix arithmetic over GF(2): addition as XOR, Hamming weight, transpose, identity, matrix-vector and matrix-matrix products |
| `hamming.py` | The [7,4,3] Hamming code: generator and parity-check matrices, encode, syndrome, the syndrome-to-position table, and single-error-correcting decode |
| `goppa.py` | GF(2^3) arithmetic and the binary parity-check matrix of a `t = 1` Goppa code, as a structural example |
| `isd.py` | Prange information-set decoding, plus the closed-form expected-iteration estimate `C(n, k) / C(n - w, k)` computed in the log domain |

`isd_cost_estimate` works in logs on purpose: going through `math.comb` directly
builds integers with hundreds of thousands of digits at Classic McEliece
parameters, where the answer is about 2^142.8.
