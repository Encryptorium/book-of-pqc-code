# ch22-isogenies

A toy SIDH key exchange built from scratch over `F_{431^2}`. Field arithmetic in a
quadratic extension, elliptic-curve arithmetic over it, Velu's formulas for
computing an isogeny and pushing points through it, and the two-party exchange
those pieces assemble into. Standard library only, CPython 3.10+.

```
pytest tests/ch22                      # 63 tests against this package
PQC_IMPL=exercises pytest tests/ch22   # against the stubbed rebuild track
```

## What this package is and is not

**This is a broken cryptosystem, on purpose.** SIDH was published in 2011 and
broken in classical polynomial time by Castryck and Decru in July 2022, with
Maino-Martindale and Robert following independently; Robert's variant is
unconditional. The SIKE team's postscript states that SIKE and SIDH are insecure
and must not be used, and NIST IR 8545 did not select SIKE. Chapter 22 builds the
scheme first and then explains the break, because the failure teaches more here
than a survivor would.

That has a consequence for this tree that is worth stating plainly, because it
differs from every other flagship package in the book: **there is no reference
specification to diverge from and no known-answer test to match.** CLAUDE.md §2
rule 3 requires official NIST vectors for flagship implementations. SIDH has no
live standard and no maintained parameter set; the fourth-round SIKE entry was
left in place carrying its own postscript rather than continued, so there is
nothing to be byte-compatible with. `tests/ch22` therefore proves internal
consistency and the mathematics, not compliance.

The distance from anything that was ever deployed:

| | This package | SIKEp434, as submitted |
|---|---|---|
| Prime | `p = 431 = 2^4 * 3^3 - 1` | 434-bit `p = 2^216 * 3^137 - 1` |
| Alice's walk | 4 steps of degree 2 | 216 steps of degree 2 |
| Bob's walk | 3 steps of degree 3 | 137 steps of degree 3 |
| Coordinates | affine, with a field inversion per point addition | Montgomery `x`-only, one inversion per protocol run |
| Interface | raw key exchange | KEM (SIKE), wrapping the same exchange |
| Status | broken, and small enough to break by hand | broken |

Three limitations beyond the parameters, each of which Chapter 22 states in prose:

- **It is not constant-time and makes no attempt to be.** `fp2_inv` calls
  `pow(norm, -1, p)`, whose running time depends on its input, and every point
  addition calls it. `point_add` also branches on whether the two inputs share an
  x-coordinate, which is a data-dependent branch on secret material during a
  chain walk.
- **There is no public-key validation.** A real SIDH implementation must check
  that a received curve is supersingular and that the received points have the
  claimed order, because adaptive-attack countermeasures depend on it. This one
  accepts whatever it is given.
- **It crashes loudly on malformed input, by design.** That is correct behaviour
  for pedagogical code and is not a substitute for validation.

## What the suite proves

`tests/ch22` is 63 tests in five files. What they actually pin down, since a test
count on its own says nothing:

- **`test_fp2_arithmetic.py`** checks the field: commutativity and associativity
  of multiplication, that `i^2 = -1`, that `fp2_sqr` agrees with `fp2_mul`, and
  Fermat's little theorem in the extension. Two error paths are pinned rather
  than assumed: `fp2_inv` raises `ZeroDivisionError` on a zero norm, and
  `fp2_sqrt` returns `None` on a non-square rather than a wrong root.
- **`test_ec_isogeny.py`** checks curve membership including a point over the
  extension, the group laws, and that the generator has order 432.
- **`test_velu.py`** checks kernel enumeration, that kernel points map to the
  identity, that the evaluation map is a homomorphism, that the recovered
  codomain is a valid curve, and that a degree-3 isogeny moves the j-invariant.
- **`test_sidh.py`** checks the four torsion-basis constants rather than trusting
  them: each is on the curve, `P_A` and `Q_A` have order 16, `P_B` and `Q_B` have
  order 27, and independence is established by enumerating all of `<P_A>` and
  `<P_B>` and confirming `Q_A` and `Q_B` are absent. The exchange itself is run
  at six `(alpha, beta)` pairs, one of which is `alpha = 0`.
- **`test_isogeny_graph.py`** checks that a degree-3 isogeny leaves `j = 1728`
  and that the degree-2 isogeny with kernel `<(0,0)>` returns to it, which is the
  extra-automorphism fixed point Figure 22.1 draws.

**One deliberate gap, stated so nobody reads more into the suite than is there.**
`test_3isogeny_graph_bfs` walks only three levels and asserts that at least three
j-invariants are reached. It does **not** establish that the graph at `p = 431`
has 37 vertices, or that it is connected. Those are the chapter's claims, sourced
to the supersingular-count formula and to Pizer, not results this suite computes.
The search was kept shallow because a full traversal in pure Python at these
parameters is slow enough to distort the suite's runtime.

## Layout

```
src/isogenies/fp2.py      arithmetic in F_p[i]/(i^2 + 1)
src/isogenies/curve.py    short Weierstrass curves over F_{p^2}
src/isogenies/velu.py     kernel enumeration, point evaluation, codomain recovery
src/isogenies/sidh.py     torsion bases, chain walk, keygen and shared-secret derivation
```

The chapter prints a self-contained slice of this package, one file per block
under `chapter-code/ch22/`. The slice inlines the field and curve helpers into
each block so that every listing runs standalone; this tree factors them out and
adds the error paths a package needs.
