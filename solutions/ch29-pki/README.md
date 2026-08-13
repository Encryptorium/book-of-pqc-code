# Chapter 29: PKI and code signing

The three deployment surfaces Chapter 29 walks, as runnable code. Standard
library only, CPython 3.10 or newer, plus the Chapter 27 and Chapter 15
packages this one imports.

```
src/pki_migration/
  chain_analyzer.py  OID classification and chain posture       (Block 1)
  jwks_verifier.py   composite JWK build, kid lookup, JWT verify (Block 2)
  xmss_index.py      crash-safe XMSS leaf counter               (Block 3)
```

Run the suite from the repository root:

```
pytest tests/ch29
```

## What this package is not

**There is no reference specification to be byte-compatible with.** Chapter 29
builds deployment tooling rather than a cryptographic algorithm, so this
package has no known-answer tests and no vectors, for the same reason Chapter
25's CBOM generator and Chapter 26's agility registry have none. What it does
have is three sets of borrowed cryptography, and each one diverges from the
real thing in a way worth naming.

**The ML-DSA underneath the composite signature is a stub.**
`jwks_verifier` calls `composite_sig_verify` from
`solutions/ch27-hybrid`, whose ML-DSA-65 component is
`hybrid.mldsa_stub`: byte-size-correct against FIPS 204 Table 2 (1952-byte
public keys, 3309-byte signatures), deterministic, and binding, but not
ML-DSA. A green `tests/ch29` run says the JWKS plumbing is right and says
nothing about lattice cryptography. The real from-scratch ML-DSA-65, matching
the NIST ACVP vectors byte for byte, is `solutions/ch12-mldsa`.

**The `kty` and `alg` values are deployment-owned, not registered.** RFC 9964
(May 2026) gives single ML-DSA a finalized JOSE serialization (the AKP JWK key
type, with `ML-DSA-44`, `ML-DSA-65` and `ML-DSA-87`), but composite
ML-DSA + Ed25519 is still draft-level in JOSE:
`draft-ietf-jose-pq-composite-sigs` registers `ML-DSA-65-Ed25519` in its
Section 7.1.5 and sits at revision -03. `OKP-COMPOSITE` and
`Ed25519+ML-DSA-65` are therefore illustrative, and no JOSE library will
interoperate with them.

**The composite key's member split follows LAMPS, not the `alg` string.**
`build_composite_jwk` publishes `mldsa_pk` as the leading 1952 bytes and
`ed_pk` as the trailing 32, because
`draft-ietf-lamps-pq-composite-sigs-19` Section 4.1 serializes the composite
public key as `mldsaPK || tradPK`. The `alg` value reads Ed25519-first for
operator legibility; the bytes do not follow it. Splitting at the wrong offset
still round-trips through `verify_composite_jwt`, so
`test_jwk_members_hold_what_their_names_say` compares `ed_pk` against
`ed25519_keygen`'s own output rather than checking another round trip.

**`chain_analyzer` parses no certificates.** Input is a sequence of `CertRef`
tuples carrying subject, issuer and a `signatureAlgorithm` OID string. It
reads no DER, verifies no signature, checks no validity date, and never
inspects `SubjectPublicKeyInfo`. A CA whose own signing key is classical under
a composite signature on its certificate is exactly the case the chapter warns
about, and this analyzer cannot see it. Chapter 29's prose says so; the code
does not enforce it.

**`xmss_index` is a counter, not an XMSS implementation.** The signing itself
is Chapter 15's `xmss_sign`. The durability this package adds is a JSON file,
an `os.replace` over a same-directory temporary, an `fsync` of the file and of
its parent directory, and a POSIX `LOCK_EX` held across the whole
read-check-increment-persist sequence. SP 800-208 Section 8.1 validates key
and signature generation only inside a hardware cryptographic module at FIPS
140 Level 3 physical security or higher, so nothing here is a conforming
implementation of the standard it cites.

## What the suite does not establish

Stated explicitly, because a green suite is easy to over-read.

- **Nothing here is constant-time**, and the composite verify path inherits
  whatever timing behaviour the Chapter 27 stub has.
- **Nothing in the suite tests concurrency.** `test_xmss_durable_counter.py`
  runs twelve single-process tests and starts no second process or thread, so
  the `LOCK_EX` that the module exists for is executed but never contended.
  The serialization argument in the module docstring is an argument, not a
  test result.
- **POSIX advisory locks do not cross host boundaries reliably.** `flock` is
  not guaranteed to serialize signers over every network or distributed
  filesystem. Any deployment that spans hosts needs a different mechanism.
- **The counter's crash-safety is argued, not tested to power loss.** The
  suite proves a reserved leaf is persisted before signing runs and that a
  restart resumes at the next index. It cannot prove the `fsync` pair survives
  a real power cut, which is the failure SP 800-208 Section 9.1 describes.
- **`analyze_chain` reports posture, not remediation.** It returns a depth and
  a per-certificate class tuple. Naming the offending certificate needs the
  subject and issuer fields, which Appendix D's Exercise 1 solution uses and
  the classifier itself does not.
