# ch06-signature-attacks

Chapter 6 of *The Encryptorium Book of Post-Quantum Cryptography*.

Two textbook signature schemes, the attack that breaks each one, and the
repair for the first:

- `signature_attacks.rsa_forgery` — textbook RSA signing on the chapter's
  64-bit modulus, the multiplicative forgery that follows from raw
  exponentiation being a group homomorphism, and the full-domain-hash
  (FDH) construction that removes the message-level homomorphism the
  attacker used.
- `signature_attacks.nonce_reuse` — ECDSA on the order-11 subgroup of
  `(Z/23Z)^*`, the closed-form recovery of the private key from two
  signatures produced under the same nonce, and the public-key check that
  tells a real reuse from a coincidence.

## Five things the chapter is careful about, and so is this package

**The package is self-contained, and deliberately does not import Chapter
4.** Chapter 4 already builds textbook RSA and ECDSA on secp256k1, and its
`sign` even takes the nonce as an explicit argument, so reusing it here
would be the obvious move. The reason not to is the `exercises/` tree:
`exercises/manifests/ch04.json` stubs `classical.ecdsa_secp256k1:sign` and
`classical.rsa:sign`, so a reader working through Chapter 6's stubs would
watch Chapter 6's suite fail for a Chapter 4 reason. The duplication is
four lines of modular arithmetic; the confusion would not be worth saving
them. Chapter 5's package is self-contained for the same reason.

**FDH here is pedagogical, and the chapter says so.** `full_domain_hash`
is SHA-256 of the message's big-endian encoding reduced modulo `n`.
Reducing a 256-bit digest modulo a 64-bit `n` is uniform enough on `Z/nZ`
to stand in for a full-domain hash at this size, with a bias around
`2^-192`. That argument does not survive a real modulus: a 3072-bit
FDH-RSA needs a construction that actually fills the domain, and deployed
RSA signatures use a standardized encoding such as RSA-PSS rather than
literal hash-and-exponentiate.

**What FDH removes is the message-level homomorphism, not the
homomorphism.** RSA exponentiation is still multiplicative, so the
attacker can still form `sigma_1 sigma_2 mod n`, and
`test_fdh_exponentiation_is_still_multiplicative` pins that the product's
`e`-th power is exactly `H(m1) H(m2) mod n`. What the product is not is a
signature on a message the attacker can name: it verifies only against an
`m*` with `H(m*) = H(m1) H(m2) mod n`, and producing one means inverting
the random oracle at a chosen point.

**The toy signer rejects `r = 0` and `s = 0`, because FIPS 186-5 does.**
It raises for both, which matches neither branch of the standard exactly:
FIPS 186-5 sends a *randomized* signer back to draw a fresh nonce and
makes a *deterministic* signer output failure, since re-deriving `k` from
the same key and message would reproduce the same `r` and `s`. The toy's
nonces are chosen by hand, so it is neither kind of signer and raising is
the honest response. This is the standard's rejection rule made visible,
not input validation; Chapter 4's ECDSA signer raises on the same two
conditions. Adding those two checks is what caught a defect in Appendix D: the block
worked for Exercise 2 used to produce `s2 = 0`, a signature no conforming
signer emits, so the attack was demonstrated on a pair that could not
occur. The block now uses `d = 4` and `k = 8` in the chapter's own group,
and `tests/ch06/test_nonce_reuse.py` pins both the new arithmetic and the
fact that the superseded constants raise.

**A shared `r` is a signal, not a proof, so the recovery comes in two
parts.** `r_from_nonce` is not injective. Real ECDSA always sends `k` and
`n - k` to the same `r`, because `kG` and `-(kG)` share an x-coordinate,
and rarely sends more than two: reducing the x-coordinate modulo `n` can
fold two distinct curve coordinates onto one `r`, which on secp256k1
happens at `r = 2` and leaves four candidate nonces.
`test_secp256k1_has_four_nonces_at_r_equals_two` pins that. This toy
reduces the group element instead of an x-coordinate and has its own
collisions, including `k = 6` and `k = 9`, one of which is the chapter's
own nonce. `recover_from_two_signatures` is the bare algebra and
will return a confident wrong answer when two different nonces happened to
collide. `recover_and_check` runs it and then recomputes the public key
from the recovered `d`, returning `None` when it does not match. The tests
pin both directions, and pin that the negated-nonce case is still fatal
with one sign flipped.

## Running the tests

From the repository root:

```
pytest tests/ch06/
```

That runs the suite against `solutions/`, which is the default: 45 tests,
all passing.

**If you are working in the `exercises/` tree, that command does not test
your work.** `tests/ch06/conftest.py` reads the `PQC_IMPL` environment
variable and defaults it to `solutions`, so a plain `pytest tests/ch06/`
reports 45 passed against the reference implementation even when every
function you are meant to write still raises `NotImplementedError`. To run
the tests against the stubs:

```
PQC_IMPL=exercises pytest tests/ch06/
```

```powershell
$env:PQC_IMPL = "exercises"; pytest tests/ch06/
```

On the untouched scaffold that reports 40 failures, every one of them a
`NotImplementedError`, and 5 passes. Three of the 5 pin the two toy
groups' declared parameters: that `p q` is 64 bits wide, that 4 has order
11 modulo 23, and that 11 is prime. The fourth pins that Appendix D's
Exercise 2 uses a different private key and nonce from the chapter's, as
that exercise asks. The fifth pins the secp256k1 fact behind the chapter's
caution aside, that four nonces share `r = 2` on the real curve. All five
read module constants and the standard library only, so no stub can reach
them. Turning the 40 green is the exercise.

No package install is needed; `tests/ch06/conftest.py` puts the package on
`sys.path`.

## What this is not

This is toy code. The RSA modulus is 64 bits and factors in well under a
second. The ECDSA group has eleven elements, so its private key can be
found by trying all of them, and the attack this package demonstrates is
only interesting because it also works unchanged on secp256k1. There is no
padding, no encoding, no constant-time arithmetic, no side-channel
hardening, and no input validation beyond the two zero checks the standard
requires of a signer. `full_domain_hash` is not a full-domain hash at any
size that matters. Inputs are assumed to satisfy the domains the chapter
states, and behavior outside them is unspecified. Do not use any of it for
anything that matters.
