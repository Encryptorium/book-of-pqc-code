"""Rounding and hint algebra (FIPS 204 §7.4, Algorithms 35-40).

These six operations are what separate ML-DSA from a plain Fiat-Shamir lattice
signature: Power2Round splits the public key so the low bits can be dropped,
Decompose/HighBits/LowBits define the commitment, and MakeHint/UseHint let the
verifier reconstruct the high bits the signer could not send. The correctness
lemma UseHint(MakeHint(z, r), r) = HighBits(r + z) for ||z||_inf <= gamma2 is the
crux; if it fails, no signature ever verifies. Every test here is a self-checking
algebraic identity, no external vector required.
"""

from __future__ import annotations

import numpy as np
import pytest

from mldsa.params import ML_DSA_Q as Q, ML_DSA_D as D, ML_DSA_44, ML_DSA_65
from mldsa.rounding import (
    mod_pm,
    power2round,
    decompose,
    high_bits,
    low_bits,
    make_hint,
    use_hint,
    power2round_poly,
    decompose_poly,
    high_bits_poly,
    low_bits_poly,
    make_hint_poly,
    use_hint_poly,
)

G2_44 = ML_DSA_44.gamma_2   # (q-1)/88
G2_65 = ML_DSA_65.gamma_2   # (q-1)/32


def test_mod_pm_range() -> None:
    # r mod± alpha lies in (-alpha/2, alpha/2] for even alpha.
    alpha = 2 * G2_44
    for r in (0, 1, alpha // 2, alpha // 2 + 1, alpha - 1, Q - 1, 12345):
        m = mod_pm(r, alpha)
        assert -alpha // 2 < m <= alpha // 2
        assert (m - r) % alpha == 0


@pytest.mark.parametrize("r", [0, 1, 2**12, 2**13, Q - 1, 4190208, 8380416, 7777777])
def test_power2round_reconstructs(r: int) -> None:
    r1, r0 = power2round(r)
    assert -(1 << (D - 1)) < r0 <= (1 << (D - 1))
    assert (r1 * (1 << D) + r0) % Q == r % Q


@pytest.mark.parametrize("gamma2", [G2_44, G2_65])
@pytest.mark.parametrize("r", [0, 1, Q - 1, 95232, 261888, 4190208, 8380416, 123456, 7654321])
def test_decompose_reconstructs(r: int, gamma2: int) -> None:
    r1, r0 = decompose(r, gamma2)
    assert -gamma2 < r0 <= gamma2
    assert (r1 * (2 * gamma2) + r0) % Q == r % Q
    assert high_bits(r, gamma2) == r1
    assert low_bits(r, gamma2) == r0


@pytest.mark.parametrize("gamma2,hi_max", [(G2_44, 43), (G2_65, 15)])
def test_high_bits_range(gamma2: int, hi_max: int) -> None:
    seen = set()
    rng = np.random.default_rng(0)
    for r in rng.integers(0, Q, size=20000, dtype=np.int64):
        seen.add(high_bits(int(r), gamma2))
    assert min(seen) == 0
    assert max(seen) == hi_max
    assert seen <= set(range(hi_max + 1))


@pytest.mark.parametrize("gamma2", [G2_44, G2_65])
def test_hint_correctness_lemma(gamma2: int) -> None:
    # UseHint(MakeHint(z, r), r) == HighBits(r + z) whenever ||z||_inf <= gamma2.
    # Here r plays the role of the verifier's w'Approx; UseHint takes r, not r+z.
    rng = np.random.default_rng(7)
    for _ in range(5000):
        r = int(rng.integers(0, Q))
        z = int(rng.integers(-gamma2, gamma2 + 1))
        h = make_hint(z, r, gamma2)
        assert h in (0, 1)
        assert use_hint(h, r, gamma2) == high_bits((r + z) % Q, gamma2)


@pytest.mark.parametrize("gamma2", [G2_44, G2_65])
def test_make_hint_flag_matches_highbit_change(gamma2: int) -> None:
    rng = np.random.default_rng(11)
    for _ in range(3000):
        r = int(rng.integers(0, Q))
        z = int(rng.integers(-gamma2, gamma2 + 1))
        expect = 0 if high_bits(r, gamma2) == high_bits((r + z) % Q, gamma2) else 1
        assert make_hint(z, r, gamma2) == expect


def test_use_hint_no_hint_is_identity_on_highbits() -> None:
    rng = np.random.default_rng(3)
    for _ in range(1000):
        r = int(rng.integers(0, Q))
        assert use_hint(0, r, G2_65) == high_bits(r, G2_65)


# --- Vectorized (polynomial) wrappers must agree with the scalar core. ---

def test_poly_wrappers_agree_with_scalars() -> None:
    rng = np.random.default_rng(5)
    poly = rng.integers(0, Q, size=256, dtype=np.int64)
    p1, p0 = power2round_poly(poly)
    for i in range(256):
        assert (int(p1[i]), int(p0[i])) == power2round(int(poly[i]))

    w1, w0 = decompose_poly(poly, G2_65)
    assert np.array_equal(w1, high_bits_poly(poly, G2_65))
    assert np.array_equal(w0, low_bits_poly(poly, G2_65))
    for i in range(256):
        assert (int(w1[i]), int(w0[i])) == decompose(int(poly[i]), G2_65)

    zpoly = rng.integers(-G2_65, G2_65 + 1, size=256, dtype=np.int64)
    hpoly = make_hint_poly(zpoly, poly, G2_65)
    recovered = use_hint_poly(hpoly, poly, G2_65)  # UseHint takes r (= w'Approx)
    assert np.array_equal(recovered, high_bits_poly((poly + zpoly) % Q, G2_65))
