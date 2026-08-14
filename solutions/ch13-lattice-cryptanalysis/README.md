# ch13-lattice-cryptanalysis

Standalone Python package for Chapter 13 of the Encryptorium Book of PQC. Implements the core-SVP cost model that the NIST Post-Quantum Cryptography project has used since the NewHope submission (Alkim, Ducas, Pöppelmann, Schwabe 2016) to calibrate lattice-based key-exchange parameters. The package reimplements equation 9 of the CRYSTALS-Kyber Round 3 submission (Avanzi et al. 2021, Section 5.1.2 "Primal attack") together with the Chen 2013 root-Hermite-factor model for BKZ output and the sieving exponents $2^{0.292 \beta}$ classical (Becker, Ducas, Gama, Laarhoven 2016) and $2^{0.265 \beta}$ quantum (Laarhoven, Mosca, van de Pol 2015).

The package does NOT implement BKZ or LLL. BKZ is treated as an oracle with cost $2^{0.292 \beta}$. The only thing the package computes is the smallest block size $\beta$ for which the primal-attack success condition is met, and the corresponding classical and quantum bit costs.

## Layout

- `src/cryptanalysis/core_svp.py` — sieving cost exponents, `classical_bits`, `quantum_bits`, and the Chen 2013 root-Hermite-factor `delta_beta` function
- `src/cryptanalysis/primal.py` — the unique-SVP primal-attack success condition from equation 9 of the Kyber Round 3 submission and the `find_beta` optimizer over $(m, \beta)$
- `src/cryptanalysis/dual.py` — the dual-distinguisher advantage as a Gaussian tail in $\|w\| \cdot \sigma / q$, used in Chapter 13's dual-distinguisher derivation
- `src/cryptanalysis/estimator.py` — the entry point that takes `(k, n, q, eta_1)` for an ML-KEM parameter set and returns the primal-attack $\beta$ and the classical and quantum core-SVP bit costs

## Tests

Run from the repo root:

```
pytest tests/ch13/
```

The suite covers four things: that `classical_bits` and `quantum_bits` are monotonic in $\beta$ and agree with the closed-form exponents at known block sizes; that the primal-attack success condition solver reproduces the Kyber Round 3 Table 4 block sizes for ML-KEM-{512, 768, 1024} within 5 block sizes; that the dual-distinguisher advantage is a well-behaved decreasing function of $\beta$ and returns the right sign; and that the full three-row estimator table matches the published core-SVP classical and quantum bit counts within 3 bits per row.

## Scope and non-scope

The package reproduces the Table 4 core-SVP numbers (Section 5.1.4 of the Kyber Round 3 submission). It does NOT reproduce the refined classical estimates in Section 5.2 (which account for dimensions-for-free, progressive BKZ with simulated sieving, and the Albrecht-Ducas-Laarhoven 2020 "leaky-LWE-estimator" model). The refined estimates give a different block size and different bit counts; those are out of scope for a pedagogical reimplementation.

The small gap between this package's Kyber-1024 $\beta$ (874) and the published value (878) is a basis-shape difference, not a $\delta(\beta)$ difference: the Kyber team's security script computes $\delta(\beta)$ from the same closed form this package does. Equation 9 lays one geometric-series line across the whole basis, while the script builds the $q$-ary shape the embedding actually has (a flat block at $\log q$, the slope only in the middle, a flat block at $0$) and matches the volume. The gap is 4 block sizes, which translates to roughly 1 bit of classical core-SVP cost, and is inside the $\pm 5$ tolerance the tests enforce.
