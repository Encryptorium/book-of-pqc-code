# ch12-mldsa

From-scratch ML-DSA (FIPS 204), the Module-Lattice-Based Digital Signature
Algorithm. Security rests on Module-LWE and Module-SIS over the ring
R_q = Z_q[X]/(X^256 + 1) with q = 8380417. Signatures are Fiat-Shamir *with
aborts*: the signer samples a masking vector, forms a commitment, derives a sparse
challenge, and restarts whenever the response would leak the secret. All three
standardized parameter sets are implemented and matched against the NIST ACVP
vectors byte-for-byte.

## Layout

| Module | FIPS 204 | Contents |
|---|---|---|
| `params.py` | §4, Table 1-2 | The `MLDSAParams` frozen dataclass and the `ML_DSA_44/65/87` sets; derived byte lengths and packing bit widths. |
| `ntt.py` | §7.5, Alg 41-42 | The full 256-point NTT/inverse at zeta = 1753 and pointwise `multiply_ntts`. |
| `rounding.py` | §7.4, Alg 35-40 | Power2Round, Decompose, HighBits, LowBits, MakeHint, UseHint (scalar + polynomial). |
| `hashes.py` | §3.7, §6-7 | SHAKE128/256 wrappers and the H-based derivations (seed split, tr, mu, rho'', c-tilde). |
| `sampling.py` | §7.3 + §7.1 Alg 14-15 | ExpandA, ExpandS, ExpandMask, SampleInBall, and the rejection predicates. |
| `encode.py` | §7.1-7.2, Alg 16-28 | SimpleBitPack/BitPack, the pk/sk/sig encoders and decoders, HintBitPack (with malformed-hint rejection), w1Encode. |
| `ml_dsa.py` | Alg 2-3, 6-8 | KeyGen/Sign/Verify (internal, explicit-seed/rnd) and the external context wrappers. |

The exposed operations are the *internal* variants that ACVP drives (all seeds and
`rnd` supplied by the caller) plus the external `ml_dsa_sign` / `ml_dsa_verify`
context wrappers. Deterministic signing corresponds to `rnd = bytes(32)`.

## Tests

```
pytest tests/ch12/
```

Coverage: parameter table and derived lengths; NTT round-trip and
multiply-vs-schoolbook (with PDF-pinned zeta landmarks); the rounding/hint algebra
including the correctness lemma `UseHint(MakeHint(z, r), r) = HighBits(r + z)`;
SHAKE known answers; the rejection samplers' bounds and determinism; bit-pack
round-trips and the three HintBitUnpack rejection conditions; KeyGen/Sign/Verify
correctness with the abort loop provably firing; and `test_vectors.py`, the NIST
ACVP byte-for-byte KAT (keyGen + deterministic sigGen + sigVer valid + sigVer
invalid) for all three parameter sets. The vectors are vendored under
`tests/ch12/vectors/` with the source ACVP-Server commit pinned in each file.

This is pedagogical reference code: it crashes loudly on bad input and is not
constant-time.
