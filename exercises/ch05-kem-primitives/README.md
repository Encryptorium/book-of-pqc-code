# ch05-kem-primitives

Chapter 5 of *The Encryptorium Book of Post-Quantum Cryptography*.

This package ships two toy constructions, one per primitive the chapter
builds, plus an attack module:

- `kem_primitives.dh` — toy Diffie-Hellman key agreement in
  `(Z/pZ)^*` on the chapter's `p = 23`, `g = 5`, plus the
  multiplicative-order routine that decides whether a candidate base
  generates the whole group rather than a proper subgroup.
- `kem_primitives.rsa_kem` — the toy RSA-KEM: `encap` samples a random
  `K` in `[1, n-1]` and encrypts it as `K^e mod n`, `decap` runs raw RSA
  decryption to recover it. The modulus is two 32-bit primes, so `n` is
  64 bits wide.
- `kem_primitives.attacks` — the mauling attack that shows the toy KEM is
  not IND-CCA2-secure, and the exact fraction of `K` in `[1, n-1]` that
  are not coprime to `n`.

## Three things the chapter is careful about, and so is this package

**Decapsulation correctness is exact, and does not need coprimality.**
Textbook RSA recovers the original residue mod `pq` for *every* input in
`[1, n-1]`, not only those coprime to `n`: Fermat's little theorem gives
`K^ed = K` mod `p` and mod `q` separately (trivially when `p` divides
`K`), and the Chinese remainder theorem lifts that to mod `pq`. Euler's
theorem alone covers only the coprime case. `tests/ch05/test_rsa_kem.py`
pins this on inputs that share a factor with `n`.

**The `1/p + 1/q` bound is load-bearing nowhere.** `recover` multiplies by
`r^-1 mod n`, so the blinding factor has to be invertible, but that is `r`
and not `K`, and the attacker chooses `r` rather than sampling it. So the
non-coprime fraction of `K` bounds neither correctness (exact) nor anything
about the attack. `coprime_failure_bound` exists because Exercise 3 asks
for the count, not because anything depends on it.

The choice of `r` does carry a condition, and it is not the one the
fraction describes. Beyond invertibility, the CCA game forbids querying the
challenge ciphertext, so the attack needs `c' != c`; an invertible `r != 1`
can still fail that, and `attacks.py` documents the `K = p` counterexample.
`r = 2` satisfies both conditions for every `K` in `[1, n-1]`, under any valid two-prime
RSA key rather than just this one: `e` is invertible mod `(p-1)(q-1)`, so
`gcd(e, p-1) = gcd(e, q-1) = 1`, which rules out `2^e = 1` modulo either
prime.

**No Fujisaki-Okamoto transform is implemented here.** The chapter states
the FO theorem and hands its instantiation to Chapter 11. The reason not to
demonstrate it on this package's RSA is that textbook RSA does not satisfy
the theorem's premise: FO takes a *randomized* IND-CPA-secure scheme, and
textbook RSA is deterministic and so not IND-CPA-secure at all. There is
nothing here for the transform to be applied to.

A related point is worth keeping straight, because it is easy to overstate.
Textbook RSA also has no encryption coins to derandomize, so the mauled
`c' = c·r^e` is a legitimate encryption of `rK` and *does* survive a
re-encryption check. That does not mean the attack would succeed: hashing
the recovered preimage is what removes the useful multiplicative
relationship, since a hash of `rK` says nothing about a hash of `K`.
Appendix D Exercise 2 works this through. The re-encryption check is the
part that needs a randomized scheme, not the part that carries the whole
security argument.

## Running the tests

From the repository root:

```
pytest tests/ch05/
```

That runs the suite against `solutions/`, which is the default.

**If you are working in the `exercises/` tree, that command does not test
your work.** `tests/ch05/conftest.py` reads the `PQC_IMPL` environment
variable and defaults it to `solutions`, so a plain `pytest tests/ch05/`
reports 40 passed against the reference implementation even when every
function you are meant to write still raises `NotImplementedError`. To
run the tests against the stubs:

```
PQC_IMPL=exercises pytest tests/ch05/
```

```powershell
$env:PQC_IMPL = "exercises"; pytest tests/ch05/
```

On the untouched scaffold that reports 38 failures, all of them
`NotImplementedError`, and 2 passes. The 2 are Appendix D's Exercise 1
arithmetic, which asserts `pow(5, 1031, 2063) == 2062` and the divisor
eliminations behind it using only the standard library, so no stub can
reach them. Turning the 38 green is the exercise.

No package install is needed; `tests/ch05/conftest.py` puts the package
on `sys.path`.

## What this is not

This is toy code. There is no padding, no key-derivation function on the
Diffie-Hellman output, no re-encryption check on the KEM, no rejection
branch, no constant-time arithmetic, and no input validation. The
Diffie-Hellman prime is 23, which a reader can break by hand. The KEM's
64-bit modulus factors in well under a second. `random.Random` is seeded
for reproducibility and is not cryptographically secure; real
encapsulation uses `secrets.SystemRandom` and feeds the output through a
KDF. Inputs are assumed to satisfy the domains the chapter states, and
behavior outside them is unspecified. Do not use any of it for anything
that matters.
