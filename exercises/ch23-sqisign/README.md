# Chapter 23 SQIsign: pedagogical-only implementation

This package is the working code for Chapter 23 of the Encryptorium Book of
Post-Quantum Cryptography. It is a pedagogical toy: the goal is to let a
reader walk the quaternion-algebra, Deuring-correspondence, and isogeny-graph
machinery end-to-end on a laptop, not to ship a reference-compliant SQIsign.

The test suite at `tests/ch23/` covers round-trip correctness and the
underlying quaternion and Deuring arithmetic. It does not attempt
byte-for-byte compatibility with the NIST additional-signatures SQIsign
submission, and it does not carry a `tests/ch23/test_vectors.py` harness
loading the reference known-answer tests.

## Divergences from the Round-2 SQIsign specification

Figures below are from version 2.0.1 of the specification, dated 2025-07-07,
which the SQIsign project lists as current. No Round-3 specification has been
published.

| Axis | Round-2 SQIsign | This toy |
| --- | --- | --- |
| Characteristic | `p = 5 * 2**248 - 1` at NIST-I, a 251-bit prime | `p = 431` |
| Supersingular graph size | About `p / 12`, near `2**247` vertices | 37 vertices (enumerable) |
| Connecting-isogeny search | Quaternion-side: sample a bounded-norm element of an ideal intersection, then translate | Breadth-first search over the graph itself |
| Ideal-to-isogeny translation | Needs isogenies between abelian surfaces (dimension two) | Not implemented; the toy never leaves dimension one |
| Response representation | Interpolation data: point images as a change-of-basis matrix, plus an auxiliary curve | The BFS path itself, as explicit kernel generators |
| Quaternion order arithmetic | Compressed lattice representation | Basis quadruples with explicit multiplication |
| Randomness schedule | NIST DRBG seed | `hashlib.sha256` over a caller-supplied seed |
| Public key size | 65 bytes at NIST-I (64-byte Montgomery coefficient plus a one-byte basis hint) | `j`-invariant in `F_{p^2}`, 4 bytes at `p = 431` |
| Signature size | 148 bytes at NIST-I | Path length times edge encoding |

The two changes that buy laptop scale are the prime and the search. At
`p = 431` the whole supersingular graph fits in memory, so breadth-first
search finds a connecting isogeny by brute force in `O(p)` time; at a 251-bit
prime the same search is infeasible and the real scheme works on the
quaternion side instead, where the cost is polynomial in `log p`. Closing that
gap would mean a 251-bit finite-field backend, quaternion-lattice sampling,
ideal-to-isogeny translation through dimension two, and the binary format of
specification section 4.6. Those are out of scope for the chapter.

One thing does carry over unchanged: the NIST-I prime is `3 mod 4`, like
`p = 431`, so the presentation of `B_{p,inf}` and the standard maximal order
`O_0` that this package implements is the same one the real scheme uses.

## What `tests/ch23/` covers

- `test_quaternion_arithmetic.py` — multiplication, conjugation, trace and
  norm in `B_{p,inf}`, against hand-computed values, plus associativity,
  non-commutativity, and multiplicativity of the norm.
- `test_maximal_orders.py` — the basis of `O_0`, the membership test, the
  round trip between an element and its `O_0` coordinates, closure of `O_0`
  under multiplication, and the norm of a principal left ideal.
- `test_deuring_correspondence.py` — the four endomorphisms of
  `E_0: y^2 = x^3 + x`, that each maps curve points to curve points, the
  relations `iota^2 = [-1]` and `iota*pi = -pi*iota`, and the action of an
  integer quaternion on a point.
- `test_graph_search.py` — torsion enumeration at `E_0` (three degree-2
  kernels, four degree-3 kernels), BFS path reconstruction, and that walking
  a returned path lands on the target `j`-invariant.
- `test_sqisign_roundtrip.py` — deterministic key generation, signing, and
  verification, including rejection of a wrong message and a wrong key.

Three claims the suite does **not** establish, all of them stated in the
chapter and checked by hand rather than pinned by a test:

- **`pi^2 = [-p]` as an endomorphism identity.** `test_pi_squared_is_identity_on_F_p2_points`
  says so in its own docstring. Both sides act as the identity on
  `F_{p^2}`-rational points, so the test confirms a coincidence; separating
  them needs points of order coprime to `p + 1`, in higher extensions.
- **The 37-vertex count** at `p = 431`. No test enumerates the graph.
- **The diameter-4 claim** at `p = 431`, which the chapter uses three times.
  `test_path_lands_at_target_j` passes `max_depth=4` to one search, which is
  weaker: it shows one path exists within four steps, not that every pair of
  vertices is within four.

## When to reach for this code

- Following Chapter 23 to see how the Deuring correspondence turns curves
  into quaternion orders and back.
- Checking your own derivations against the arithmetic in `quaternion.py`
  and `orders.py`.
- Teaching isogeny cryptography at a scale where the supersingular graph
  is small enough to enumerate by hand.

## When not to reach for this code

- Signing real messages. Use the reference implementation tracked from
  `https://sqisign.org/` for any non-pedagogical use.
- Performance or side-channel analysis of deployed SQIsign. The toy's
  arithmetic matches the reference on neither axis. Note that the reference
  implementations are not constant-time either, which the specification says
  outright in section 1.1.
- Reference-KAT regression. A compliant test module would need the
  251-bit-prime backend and the dimension-two translation described above.
