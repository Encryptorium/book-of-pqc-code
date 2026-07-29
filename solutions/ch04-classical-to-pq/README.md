# ch04-classical-to-pq

Chapter 4 of *The Encryptorium Book of Post-Quantum Cryptography*.

This package ships two deliberately insecure pedagogical schemes and one
attack-side routine:

- `classical.rsa` — textbook RSA (no padding): keygen, encrypt, decrypt,
  sign, verify on toy moduli built from two 32-bit primes, which come out
  63 or 64 bits wide.
- `classical.curve` + `classical.ecdsa_secp256k1` — ECDSA on `secp256k1`
  with an explicit reader-supplied nonce.
- `classical.shor_postprocess` — the classical post-processing step of
  Shor's algorithm: given a verified period `r` of `a` modulo `N`, try the
  two `gcd` candidates and either recover a non-trivial factor of `N` or
  signal that the outer Shor loop must retry with a fresh base.

The quantum period-finding step is **not** simulated here. Small
instances can be simulated classically, but generic state-vector
simulation costs memory exponential in the qubit count, so it does not
reach cryptographic scale; a pedagogical run would still want a
simulator such as Qiskit or Cirq, and pulling one in would break the
Appendix C clean Python install contract. The chapter prose states the
period-finding complexity and cites Shor 1994 and Nielsen-Chuang 2010.

## Running the tests

From the repository root:

```
pytest tests/ch04/
```

That runs the suite against `solutions/`, which is the default.

**If you are working in the `exercises/` tree, that command does not test
your work.** `tests/ch04/conftest.py` reads the `PQC_IMPL` environment
variable and defaults it to `solutions`, so a plain `pytest tests/ch04/`
reports 17 passed against the reference implementation even when every
function you are meant to write still raises `NotImplementedError`. To
run the tests against the stubs:

```
PQC_IMPL=exercises pytest tests/ch04/
```

```powershell
$env:PQC_IMPL = "exercises"; pytest tests/ch04/
```

On the untouched scaffold that reports 17 failures, all of them
`NotImplementedError`. Turning those 17 green is the exercise.

No package install is needed; `tests/ch04/conftest.py` puts the package
on `sys.path`.

## What this is not

This is toy code. There is no padding, no message hashing for RSA
signing, no random nonces for ECDSA, no constant-time arithmetic, no
side-channel protection, and no input validation. Inputs are assumed to
satisfy the domains the chapter states, and behavior outside them is
unspecified: it is not reliably a loud failure. `encrypt` on a message at
or above the modulus quietly returns a reduced residue rather than
complaining, and `keygen(bits=2)` never returns, because a one-bit prime
candidate can only ever be 1. Do not use any of it for anything that
matters.
