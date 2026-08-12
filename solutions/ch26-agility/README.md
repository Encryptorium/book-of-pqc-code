# Chapter 26: Crypto agility

The architectural patterns Chapter 26 walks, as runnable code over the same
mock application Chapter 25 inventories. Standard library only, CPython 3.10
or newer.

```
src/agility/
  tokens.py     brittle and agile JWT-like signers          (Block 1)
  algid.py      namespaced algorithm-identifier parsing     (Block 2)
  registry.py   four-state approval registry and policy     (Block 3)
                plus permits() and approved_at()
  posture.py    needs_rehash() and agility_status()
```

Run the suite from the repository root:

```
pytest tests/ch26
```

## What this package is not

**There is no reference specification to be byte-compatible with.** Chapter 26
builds an architectural discipline rather than a cryptographic algorithm, so
this package has no known-answer tests and no vectors, for the same reason
Chapter 25's CBOM generator has none. The only primitives it calls are
`hmac` and `hashlib` from the standard library, and it makes no claim to add
security to either.

**The tokens are JWT-like, not JWS.** RFC 7515 Section 4.1.1 makes the `alg`
Header Parameter mandatory, so `sign_brittle` produces an object a conforming
verifier would reject. That is deliberate: omitting the identifier is what
makes the observability cost visible. `sign_agile` emits `alg` but is still
not a production JWT implementation. RFC 8725 Section 3.1 additionally
requires a caller-specified algorithm set, a check that the header `alg`
matches the operation performed, and a binding from each key record to one
algorithm family. `tokens.py` implements only the first two, and its
single-secret design cannot express the third, which is why an HS/RS
algorithm-confusion attack is out of scope here.

**The registry states are local policy, not NIST status.** The four names
`acceptable`, `deprecated`, `legacy-use` and `disallowed` come from NIST
SP 800-131A Rev. 2, which applies them to (algorithm, key-length) pairs on
dated transitions. It assigns HMAC no status per hash function at all: it
routes through key length, making generation keys of at least 112 bits
acceptable and shorter ones disallowed, while allowing shorter keys for
verification as legacy use. The `state` values in `registry.REGISTRY` are one
organization's policy choices wearing NIST's vocabulary, and reading them as a
transcription of NIST status would be wrong in both directions.

**`permits` is stricter than Block 3's signer is.** `permits("deprecated",
"protect")` returns `True`, because deprecation signals risk rather than
prohibition. Block 3's `sign` refuses `deprecated` anyway. Both are correct:
the state says what is allowed, the signer applies a local policy on top.

## What the suite does not establish

Stated explicitly, because a green suite is easy to over-read.

- **Nothing here is constant-time.** `hmac.compare_digest` is, and the
  surrounding dictionary lookups and string splits are not. A real verifier
  leaks the algorithm identifier through timing regardless, since the
  identifier is public.
- **`approved_at` compares ISO-8601 dates as strings.** That is correct for
  well-formed `YYYY-MM-DD` values and silently wrong for anything else. No
  test feeds it a malformed date, because the chapter's contract is that the
  approved-algorithm list is generated rather than hand-typed.
- **`agility_status` reads two fields and nothing else.** A touchpoint can
  carry both an identifier and a rotation policy while no rotation has ever
  been rehearsed. Appendix D's editorial note for Exercise 1 names that trap;
  no test can catch it, because the distinction is not in the data.
