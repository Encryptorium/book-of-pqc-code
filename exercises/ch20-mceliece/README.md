# ch20-mceliece

McEliece's 1978 public-key encryption scheme, built from scratch over
GF(2^m) with Patterson decoding. Key generation, encryption, decryption,
generalized binary Goppa codes, and the GF(2^m) polynomial arithmetic
Patterson needs. Standard library only, CPython 3.10+.

```
pytest tests/ch20                      # 37 tests against this package
PQC_IMPL=exercises pytest tests/ch20   # against the stubbed rebuild track
```

## What this package is and is not

**This is not Classic McEliece.** It is the original 1978 construction: a
message multiplied by a disguised generator matrix `G_pub = S * G * P`, plus a
weight-`t` error vector. Classic McEliece, the NIST Round-4 submission, is the
Niederreiter dual of that scheme, wrapped in a CCA-secure KEM transform. The
differences are not cosmetic:

| | This package | Classic McEliece |
|---|---|---|
| Interface | PKE: encrypt a `k`-bit message | KEM: encapsulate a session key |
| Public key | `G_pub`, a `k`-by-`n` generator matrix | `T`, the `mt`-by-`k` block of a systematic parity-check matrix |
| Ciphertext | `n` bits, a noisy codeword | `mt` bits, a syndrome |
| Message | the plaintext, carried in the codeword | a weight-`t` error vector, hashed to a session key |
| Security goal | OW-CPA at best | IND-CCA2, via reencryption and implicit rejection |

It is a teaching implementation and nothing here should be used to protect
anything. Four limitations in particular, each of which Chapter 20 states in
prose:

- **It is not constant-time and makes no attempt to be.** Patterson's
  root-finding branches on the error positions, `gf2m_inv` is a linear search,
  and `random_invertible_matrix` rejection-samples. Any of these leaks the
  private key to an attacker who can time decryption.
- **It is not IND-CCA2 secure.** There is no reencryption check, no implicit
  rejection, and no plaintext confirmation, so a chosen-ciphertext attacker
  recovers the message. Adding the transform is what turns McEliece into
  Classic McEliece.
- **The parameters are a toy.** The chapter runs GF(2^4) with `t = 2`, giving a
  `[16, 8, >= 5]` code. Classic McEliece's smallest set is `n = 3488`,
  `t = 64` over GF(2^12). At GF(2^4) the whole message space is 256 messages
  and the whole error space is 120 vectors, so it hides nothing.
- **`random.Random` is used throughout**, which is not a cryptographic
  generator. Both randomized entry points, `keygen` and `encrypt`, take an `rng`
  argument so the tests can seed it and the chapter's printed output can be
  reproduced. A real implementation
  would need `secrets` and a constant-time fixed-weight sampler.

There is no known-answer test, because there is no reference specification this
scheme conforms to. The book's rigor bar requires official NIST vectors for
flagship implementations (ML-KEM from FIPS 203, ML-DSA from FIPS 204, SLH-DSA
from FIPS 205). Classic McEliece was not selected for standardization and this
package does not implement it in any case, so correctness is pinned by
structural properties instead: that `G * H^T` is zero over the permuted column
ordering, that the Goppa polynomial is irreducible and no support element is a
root of it, that squaring `poly_sqrtmod`'s output returns the input for all 256
residues of a degree-2 quotient ring, that Patterson corrects every weight-2
error pattern at the toy parameters, and that keygen, encrypt and decrypt
round-trip across 20 key seeds with 10 random messages each.

## Layout

| Module | Contents |
|---|---|
| `gf2.py` | Arithmetic over GF(2): vector add, weight, transpose, identity, matrix products, Gaussian elimination to systematic form, generator from parity-check, matrix inverse, and the random invertible and permutation matrices that make up the disguise |
| `gf2m.py` | GF(2^m) elements as bit-pattern integers, and polynomials over GF(2^m) as coefficient lists: multiply, invert, evaluate by Horner, polynomial multiply, reduce, extended GCD, inverse modulo `g`, square root modulo `g`, and an irreducibility test |
| `goppa.py` | The generalized binary Goppa code: find an irreducible degree-`t` Goppa polynomial, take the full support, and build the `(mt)`-by-`n` binary parity-check matrix |
| `patterson.py` | Patterson's 1975 algorithm in the chapter's five steps: syndrome polynomial, key transform, square root, partial GCD for the error locator, and root-finding |
| `mceliece.py` | The scheme itself: `keygen`, `encrypt`, `decrypt` |

The square root in `poly_sqrtmod` is computed by `m*t - 1` successive squarings
rather than by materializing the exponent. When `g` is irreducible of degree `t`
the quotient ring GF(2^m)[x]/g(x) is isomorphic to GF(2^(m*t)), so the square
root of `f` is `f^(2^(m*t - 1))`; at Classic McEliece sizes that exponent has
over 200 digits and there is no reason to build it.

`decrypt` reorders the support with `col_perm` before calling Patterson. This is
the easiest thing in the package to get wrong, because getting it wrong produces
a clean-looking wrong plaintext rather than an exception:
`gauss_systematic` permutes columns to reach systematic form, so the support has
to be permuted the same way before it lines up with the decoded coordinates.
