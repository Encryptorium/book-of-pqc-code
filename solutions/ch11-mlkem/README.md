# ch11-mlkem

Standalone Python package for Chapter 11 of the Encryptorium Book of PQC. Implements **ML-KEM** as standardized in [NIST FIPS 203](https://doi.org/10.6028/NIST.FIPS.203). The K-PKE component is Regev public-key encryption over Module-LWE at $(n, q, k) = (256, 3329, k)$ for $k \in \{2, 3, 4\}$, with centered binomial noise and compression. The ML-KEM wrapper applies the Fujisaki-Okamoto transform in its implicit-rejection form to lift K-PKE from IND-CPA to IND-CCA2: a failed re-encryption check returns a pseudorandom key rather than an explicit failure symbol.

## Layout

- `src/mlkem/params.py` — `ParameterSet` enum and the three `MLKEMParams` instances `ML_KEM_512`, `ML_KEM_768`, `ML_KEM_1024`
- `src/mlkem/hashes.py` — the SHA-3 auxiliary functions `H`, `G`, `PRF`, `XOF` per FIPS 203 §4.1
- `src/mlkem/ntt.py` — the specialized partial NTT for $R_{3329}$ with primitive $256$-th root of unity $\zeta = 17$ per FIPS 203 Appendix A
- `src/mlkem/sampling.py` — centered binomial sampling `CBD_eta`, rejection-sampled uniform sampling from an XOF, matrix and vector samplers
- `src/mlkem/compress.py` — `compress` and `decompress` (FIPS 203's $\text{Compress}_d$ and $\text{Decompress}_d$), one-bit message encoding and decoding per FIPS 203 §4.2.1
- `src/mlkem/serialize.py` — `ByteEncode_d` and `ByteDecode_d` for polynomials and compressed polynomials per FIPS 203 §4.2.1
- `src/mlkem/k_pke.py` — `K_PKE.KeyGen`, `K_PKE.Encrypt`, `K_PKE.Decrypt` per FIPS 203 §5
- `src/mlkem/ml_kem.py` — `ml_kem_keygen_internal`, `ml_kem_encaps_internal`, `ml_kem_decaps_internal` per FIPS 203 §6

## Tests

Run from the repo root:

```
pytest tests/ch11/
```

The test suite covers the NTT round-trip, the partial-NTT multiplication identity, centered binomial distribution properties, compression bounds, ByteEncode round-trip, K-PKE correctness across all three parameter sets, ML-KEM round-trip and implicit rejection, and the rigor-bar contract `tests/ch11/test_vectors.py` which compares one NIST ACVP KAT round per parameter set against the package output byte-for-byte.
