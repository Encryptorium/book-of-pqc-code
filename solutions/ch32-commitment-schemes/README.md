# commitment-schemes (Chapter 32)

Toy implementations of the four commitment-scheme families analyzed at L2
of the four-layer decomposition introduced in Chapter 31 of *The
Encryptorium Book of Post-Quantum Cryptography*. The package is stdlib
only and runs on Python 3.10 or later.

## Modules

| Module | Family | Binding assumption | Scope |
|---|---|---|---|
| `toy_kzg` | Pairing-based polynomial commitment | d-SDH (reduced here to discrete log) | SRS setup, commit, honest opening via quotient polynomial, simulated Shor trapdoor recovery, post-Shor opening forgery. Does not build pairings. |
| `merkle` | Hash-based | Collision resistance of the hash | q-ary Merkle tree with configurable output width, commit/open/verify round trip, BHT and CNPS quantum-collision-bit helpers. |
| `fri` | Hash-based (information-theoretic proximity) | Collision resistance of the hash plus the proximity gap | Reed-Solomon codeword, folding rounds, query-based consistency check. Interactive only; no Fiat-Shamir compilation. |
| `lattice_pcs` | Lattice-based | Module-SIS | Public-matrix setup, commit with small error for hiding, verify, SIS-binding witness extraction from two openings. Vector commitment only; does not implement an evaluation protocol. |

## Scope boundaries

- **Not production code.** The moduli are small enough for pedagogical
  inspection. The `toy_kzg` module does not build pairings; the `fri`
  module is interactive; the `lattice_pcs` module does not implement an
  evaluation protocol. Chapter 32 states these boundaries explicitly.
- **Intended companions.** Chapter 34 covers STARKs and production-depth
  FRI. The 2024-2026 lattice PCS frontier (Greyhound, Jindo, Hachi) is
  cited in Chapter 32 but not reimplemented here.

## Running

From `solutions/ch32-commitment-schemes/`:

```
python3 -m pip install -e .
pytest ../../tests/ch32/
```

All tests must pass green; Chapter 32's rigor bar requires it.
