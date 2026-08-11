# ch21-hqc

The IND-CPA core of HQC, built from scratch over `GF(2)[x]/(x^n - 1)`. Key
generation, encryption, decryption, circulant polynomial arithmetic, fixed-weight
sparse sampling, and a repetition inner code. Standard library only, CPython 3.10+.

```
pytest tests/ch21                      # 35 tests against this package, 9 skipped
PQC_IMPL=exercises pytest tests/ch21   # against the stubbed rebuild track
```

The nine skips are the reference known-answer tests, which activate only when the
official `.rsp` files are vendored; `tests/ch21/vectors/README.md` says where to
get them.

## What this package is and is not

**This is not HQC.** It is the public-key encryption scheme at the centre of HQC,
stripped to the part that makes the construction work, at parameters small enough
to print. The NIST submission is a KEM built on that core, and the gap is not
cosmetic:

| | This package | HQC as specified |
|---|---|---|
| Interface | PKE: encrypt a `k`-bit message | KEM: encapsulate a session key |
| Inner code | repetition, majority-vote decoded | concatenated Reed-Solomon and duplicated Reed-Muller |
| Ring degree | `n = 83` | `n = 17669`, `35851`, `57637` |
| Security goal | IND-CPA | IND-CCA2, via a salted Fujisaki-Okamoto transform |
| Decryption failure rate | a few in a thousand | below `2^-128` by design |

It is a teaching implementation and nothing here should be used to protect
anything. Four limitations in particular, each of which Chapter 21 states in
prose:

- **It is not IND-CCA2 secure.** There is no re-encryption check and no implicit
  rejection, so a chosen-ciphertext attacker recovers the secret. Adding that
  transform is what turns this scheme into the HQC KEM.
- **It is not constant-time and makes no attempt to be.** `poly_mul`'s outer loop
  skips positions where its first argument is zero, so its running time scales
  with that argument's weight. Encryption calls it as `poly_mul(r2, s, n)` and
  `poly_mul(r2, h, n)`, where `r2` is secret encryption randomness of weight
  `w_r`, so the timing carries information the scheme depends on hiding.
- **The parameters are a toy.** `n = 83` with weights of 3 gives a secret support
  space of `C(83,3)^2`, about 2^33 pairs, which is exhaustible. The chapter's
  round-trips fail outright a few times in a thousand, which is the point: the
  decryption failure rate is visible at this size and invisible at the real one.
- **`random.Random` is used throughout**, which is not a cryptographic generator.
  Both randomized entry points, `keygen` and `encrypt`, take an `rng` argument so
  the tests can seed it and the chapter's printed supports can be reproduced. A
  real implementation needs an approved random-bit generator and a constant-time
  fixed-weight sampler.

There is no known-answer test against this package, because it does not implement
the specified scheme and could not match its vectors. `tests/ch21/test_vectors.py`
checks the reference KAT's structure and byte lengths when the files are vendored,
which validates the fixtures rather than the code. Correctness is pinned by
structural properties instead: that `poly_add` and `poly_mul` obey the ring laws
including wraparound modulo `x^n - 1`; that `sample_sparse` produces exactly `w`
ones and is reproducible from a seed; that the repetition code round-trips every
message, survives errors inside its capacity and fails outside it; that `keygen`
produces weight-`w` secrets and an `h` that recomputes as `x + s*y`; that
encryption and decryption round-trip all 16 messages across 20 key seeds at under
5% failure; that `v + u*y` equals `rep_encode(m)` plus exactly `r2*x + r1*y + e`;
and that across 1,000 trials no repetition block picks up more than 12 errors,
against a correction capacity of 8, and across 5,000 trials the failure rate stays
under 10%.

Those last two bounds are deliberately loose. They are set to catch a broken noise
calculation, not to certify a failure rate: at these parameters decryption
genuinely does fail sometimes, and a test that forbade it would be testing the
wrong thing.

## Layout

| Module | Contents |
|---|---|
| `poly_gf2.py` | The ring `GF(2)[x]/(x^n - 1)`: add as componentwise XOR, multiply as circulant convolution, and Hamming weight |
| `sparse.py` | Fixed-weight sampling: `w` positions drawn without replacement from `n` |
| `repetition.py` | The inner code: repeat each message bit `r` times and zero-pad to `n`, then decode by majority vote per block |
| `hqc.py` | The scheme itself: `keygen`, `encrypt`, `decrypt` |

Two things here are easier to get wrong than they look.

**The draw order from `rng` is part of the contract.** `keygen` draws `s`, then
`x`, then `y`; `encrypt` draws `r1`, then `r2`, then `e`. Nothing in the algorithm
requires those orders, but the chapter's printed supports and several tests
reconstruct the same values by replaying a seeded generator, so changing the order
silently invalidates them rather than raising anything.

**`decrypt` takes the public key as well as the secret key.** It needs only `y`
from the secret, but `n` and `r` live in the public key, and this package keeps
the parameters with the key that carries them rather than in module constants.
Decryption itself is two lines: `v + u*y` in the ring, then `rep_decode`. It never
inspects the noise, so a block that picked up more than `(r-1)/2` flips returns a
wrong message rather than an error. That silence is the decryption failure the
noise budget bounds, and it is why HQC needs the Fujisaki-Okamoto transform to
reach IND-CCA2.
