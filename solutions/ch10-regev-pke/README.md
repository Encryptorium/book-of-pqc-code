# ch10-regev-pke

Standalone Python package for Chapter 10 of the Encryptorium Book of PQC. Implements Regev's public-key encryption scheme over flat LWE with a small discrete parameter tuple: the `RegevParams` dataclass with the noise-budget headroom exposed as a method, `keygen` producing $(A, b = A s + e)$ in $\mathbb{Z}_q^{m \times n} \times \mathbb{Z}_q^m$, `encrypt` producing a ciphertext $(c_1, c_2) = (A^\top r, b^\top r + \lfloor q/2 \rfloor \mu)$ for a random $r \in \{0, 1\}^m$ and a message bit $\mu \in \{0, 1\}$, and `decrypt` rounding $(c_2 - c_1^\top s) \bmod q$ to the nearer of $0$ or $\lfloor q/2 \rfloor$ by the integer expression $\lfloor (2 v + \lfloor q/2 \rfloor) / q \rfloor \bmod 2$.

## Layout

- `src/regev_pke/params.py` — `RegevParams` dataclass with structural asserts and a `noise_budget_headroom` reporter
- `src/regev_pke/keygen.py` — `keygen(params, rng)` returning `((A, b), s)`
- `src/regev_pke/encrypt.py` — `encrypt(params, public_key, bit, rng)` returning `(c1, c2)`
- `src/regev_pke/decrypt.py` — `decrypt(params, secret_key, ciphertext)` returning the recovered bit

## Tests

Run from the repo root:

```
pytest tests/ch10/
```

The test suite covers parameter validation, key generation shape and the $b = A s + e$ identity, encrypt-decrypt round-trip across many seeds for both message bits, noise-budget tightness (feasible parameters decode every seed correctly; infeasible parameters fail on a measurable fraction of seeds), and the IND-CPA sanity check that the same bit under the same public key produces different ciphertexts under fresh randomness.

## Chapter 11

Chapter 11 rebuilds these ideas rather than importing them. It ships its own package (`mlkem`) with its own parameter type and samplers, because the objects change: ML-KEM's secret is a vector of ring elements rather than a vector in $\mathbb{Z}_q^n$, and its parameters are fixed by FIPS 203. What carries over is the shape, `keygen` then `encrypt` then `decrypt` with the secret cancelling on the decryption side, plus the Fujisaki-Okamoto transform that turns the IND-CPA scheme into an IND-CCA2 KEM. Nothing outside `tests/ch10/` imports `regev_pke`.
