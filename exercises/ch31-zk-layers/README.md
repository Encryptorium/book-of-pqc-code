# Chapter 31: the four-layer decomposition

Reference implementation for Chapter 31 of *The Encryptorium Book of
Post-Quantum Cryptography*. Standard library only, Python 3.10 or later.

```
pip install -e .          # optional; the test suite adds src/ to sys.path
pytest tests/ch31         # from the repository root
```

Three modules, one per thing Chapter 31 needs to make concrete.

| Module | Layer | What it holds |
|---|---|---|
| `zk_layers.r1cs` | L1 | The rank-1 constraint format the chapter prints, plus the per-gate cost model behind its constraint counts. |
| `zk_layers.merkle` | L2 | The binary Merkle commitment the chapter prints, with the domain separation the printed block flags as omitted. |
| `zk_layers.layers` | all four | The layer table, the per-system posture table, and the three lookups that read them. |

## What this is not

**None of this is production cryptography, and `zk_layers.layers` is not
cryptography at all.** The package exists so that Chapter 31's claims are
executable rather than only printed, not so that anything here is
deployed.

Divergences from what a real system does, in the order a reader is
likely to trip over them:

- **The R1CS field is `P = 97`.** A deployed SNARK works over a prime of
  around 255 bits, for BLS12-381 the scalar field. Ninety-seven is small
  enough that the toy system's arithmetic can be checked by hand, and far
  too small for anything else. `dot` and `check_r1cs` are the chapter's
  printed block verbatim.
- **`gate_constraints` is a cost model, not a compiler.** It returns how
  many multiplication constraints a gate's standard encoding needs. It
  does not build the constraint rows, and a real circuit compiler will
  beat these counts on some gates through lookup arguments or custom
  gates, which is a PLONKish and AIR facility rather than an R1CS one.
- **The Merkle tree is binary, fixed at SHA-256, and holds the whole
  tree in memory.** Chapter 32 generalizes it in
  `commitment_schemes.merkle` to configurable arity and hash-output
  width, and sizes that width against the quantum collision bounds. This
  module deliberately stays at the shape of L2 rather than its
  parameters. It also recomputes the tree on every opening instead of
  caching the levels, which is fine for four leaves and wrong for a
  production prover.
- **The domain separation here is the minimum that works.** One tag byte
  in front of the hashed value, distinct for leaves and internal nodes.
  A production tree usually also binds the tree height, the leaf index,
  or both, so that a commitment fixes the shape of the tree and not only
  its contents.
- **`zk_layers.layers` is Encryptorium's analytical framing.** The
  four-layer decomposition is this book's, not a standard literature
  taxonomy, and the chapter says so. The posture values are a coarse
  summary of the literature at survey depth; the per-system numbers at
  deployment parameters are Chapter 32's and Chapter 35's work, not this
  table's.
- **`hash_bits_for_pq_collision` inverts a query-model bound.** The
  Brassard-Hoyer-Tapp `2^{n/3}` figure and the
  Chailloux-Naya-Plasencia-Schrottenloher `2^{2n/5}` figure are
  worst-case theoretical targets rather than literal deployment-cost
  estimates, and sizing against them is conservative by construction.
  Chapter 32's `quantum_collision_bits_bht` runs the same bound the
  other way, from a width to the bits it delivers.

## The one thing worth reading the tests for

`tests/ch31/test_layers.py::test_each_system_carries_its_own_l2_and_l4_posture`
and
`tests/ch31/test_r1cs.py::test_each_gate_carries_its_own_cost_and_arity`
each pin every row of a labelled table to its own value. Neither is
redundant with the tests around it. Every posture value in the table
appears more than once, and the gate costs sum to the same total under a
permutation, so a test that checks which values are used, how many there
are, or what they add up to survives swapping two rows and leaves the
table wrong. Both were confirmed to fail against a swapped table before
being relied on.
