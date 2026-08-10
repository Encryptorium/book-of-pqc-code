"""Full 256-point NTT over R_q, q = 8380417 (FIPS 204 §7.5, Algorithms 41-42).

Unlike ML-KEM's partial NTT (which stops at degree-2 factors), ML-DSA's ring
splits completely because q ≡ 1 (mod 2n): the NTT maps a polynomial to 256
independent scalars and multiplication in the NTT domain is plain pointwise.
These tests are self-validating: the round-trip and the multiply-agrees-with-
schoolbook identity pin the transform (including the zeta ordering) without any
external vector.
"""

from __future__ import annotations

import numpy as np
import pytest

from mldsa.ntt import (
    Q,
    N,
    ZETAS,
    ntt,
    ntt_inverse,
    multiply_ntts,
    schoolbook_ring_multiply,
)


def _rand_poly(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, Q, size=N, dtype=np.int64)


def test_constants() -> None:
    assert Q == 8380417 and N == 256
    assert len(ZETAS) == 256
    assert ZETAS[0] == 1
    # Landmark values from FIPS 204 Appendix B (PDF text layer): zetas[k] =
    # zeta^(brv8(k)) mod q. brv8(128)=1 so zetas[128] must be zeta itself.
    assert ZETAS[1] == 4808194
    assert ZETAS[2] == 3765607
    assert ZETAS[8] == 7778734
    assert ZETAS[128] == 1753


def test_zero_maps_to_zero() -> None:
    z = np.zeros(N, dtype=np.int64)
    assert np.array_equal(ntt(z), z)
    assert np.array_equal(ntt_inverse(z), z)


@pytest.mark.parametrize("seed", [1, 2, 7, 42, 999])
def test_round_trip(seed: int) -> None:
    f = _rand_poly(seed)
    assert np.array_equal(ntt_inverse(ntt(f)), f)


def test_does_not_mutate_input() -> None:
    f = _rand_poly(3)
    f_copy = f.copy()
    ntt(f)
    ntt_inverse(f)
    assert np.array_equal(f, f_copy)


@pytest.mark.parametrize("seed", [1, 5, 20, 123])
def test_multiply_agrees_with_schoolbook(seed: int) -> None:
    a = _rand_poly(seed)
    b = _rand_poly(seed + 1000)
    got = ntt_inverse(multiply_ntts(ntt(a), ntt(b)))
    want = schoolbook_ring_multiply(a, b)
    assert np.array_equal(got, want)


def test_multiply_by_one() -> None:
    one = np.zeros(N, dtype=np.int64)
    one[0] = 1
    a = _rand_poly(11)
    got = ntt_inverse(multiply_ntts(ntt(a), ntt(one)))
    assert np.array_equal(got, a)


def test_negacyclic_wrap() -> None:
    # X^255 * X = X^256 = -1 in Z_q[X]/(X^256+1): the top coefficient wraps
    # negated into the constant term.
    x255 = np.zeros(N, dtype=np.int64)
    x255[255] = 1
    x1 = np.zeros(N, dtype=np.int64)
    x1[1] = 1
    got = ntt_inverse(multiply_ntts(ntt(x255), ntt(x1)))
    want = np.zeros(N, dtype=np.int64)
    want[0] = Q - 1  # -1 mod q
    assert np.array_equal(got, want)
