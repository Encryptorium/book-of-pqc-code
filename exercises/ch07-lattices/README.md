# ch07-lattices

Standalone Python package for Chapter 7 of the Encryptorium Book of PQC. Implements a full-rank integer lattice as the set of integer combinations of a basis, computes the determinant, the dual basis $B^{-T}$, and Minkowski's bound on the shortest vector, and detects when two bases generate the same lattice via a unimodular change of basis. The chapter uses the package as its reference implementation; chapter code blocks are simplified pedagogical slices.

## Layout

- `src/lattices/lattice.py` — `Lattice` dataclass wrapping an integer basis matrix
- `src/lattices/determinant.py` — `det(L)` returning $|\det B|$
- `src/lattices/dual.py` — `dual_basis(L)` returning $B^{-T}$ for full-rank square $B$
- `src/lattices/minkowski.py` — `minkowski_bound(L)` returning $\sqrt{n} \cdot \det(L)^{1/n}$
- `src/lattices/unimodular.py` — `is_unimodular(U)` and `change_of_basis(B1, B2)`

## Tests

Run from the repo root:

```
pytest tests/ch07/
```

The test suite covers determinant invariance under unimodular change of basis, the dual-of-dual identity, the Minkowski bound on small lattices, and change-of-basis detection.

## Chapters 8 through 11 reuse this package.
