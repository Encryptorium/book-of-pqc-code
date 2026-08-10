"""Rejection samplers and the challenge sampler (FIPS 204 §7.3, Algorithms 29-34).

ML-DSA derives all of its structured randomness by rejection sampling a SHAKE
stream: A from SHAKE128 (ExpandA), the secret s1/s2 from SHAKE256 (ExpandS), the
per-attempt mask y from SHAKE256 (ExpandMask), and the sparse challenge c from
SHAKE256 (SampleInBall). These tests pin the shapes, coefficient bounds, and
determinism; the byte-exact stream consumption is pinned downstream by the ACVP
keyGen vector (A, s1, s2) and sigGen vector (y, c).
"""

from __future__ import annotations

import numpy as np
import pytest

from mldsa.params import ML_DSA_Q as Q, ML_DSA_44, ML_DSA_65, ML_DSA_87
from mldsa.sampling import (
    coeff_from_three_bytes,
    coeff_from_half_byte,
    sample_in_ball,
    rej_ntt_poly,
    expand_a,
    rej_bounded_poly,
    expand_s,
    expand_mask,
)


def test_coeff_from_three_bytes() -> None:
    assert coeff_from_three_bytes(1, 0, 0) == 1
    assert coeff_from_three_bytes(0, 0, 0) == 0
    # top bit of b2 is masked off before the range check
    assert coeff_from_three_bytes(0, 0, 0x80) == 0
    # 0x7FFFFF = 8388607 >= q -> rejected
    assert coeff_from_three_bytes(0xFF, 0xFF, 0xFF) is None
    # q-1 accepted, q rejected
    assert coeff_from_three_bytes((Q - 1) & 0xFF, ((Q - 1) >> 8) & 0xFF, ((Q - 1) >> 16) & 0xFF) == Q - 1
    assert coeff_from_three_bytes(Q & 0xFF, (Q >> 8) & 0xFF, (Q >> 16) & 0xFF) is None


def test_coeff_from_half_byte_eta2() -> None:
    vals = [coeff_from_half_byte(b, 2) for b in range(16)]
    for b in range(15):
        assert vals[b] == 2 - (b % 5)
        assert -2 <= vals[b] <= 2
    assert vals[15] is None


def test_coeff_from_half_byte_eta4() -> None:
    for b in range(9):
        assert coeff_from_half_byte(b, 4) == 4 - b
        assert -4 <= coeff_from_half_byte(b, 4) <= 4
    for b in range(9, 16):
        assert coeff_from_half_byte(b, 4) is None


@pytest.mark.parametrize("params", [ML_DSA_44, ML_DSA_65, ML_DSA_87])
def test_sample_in_ball(params) -> None:
    rho = bytes(range(params.c_tilde_len()))
    c = sample_in_ball(params, rho)
    assert c.shape == (256,)
    nonzero = c[c != 0]
    assert len(nonzero) == params.tau           # exactly tau nonzero coefficients
    assert set(int(x) for x in nonzero) <= {1, -1}  # all +-1
    assert int(np.sum(np.abs(c))) == params.tau  # infinity/one-norm is tau
    assert np.array_equal(sample_in_ball(params, rho), c)  # deterministic
    assert not np.array_equal(sample_in_ball(params, bytes([1]) + rho[1:]), c)


def test_rej_ntt_poly_range_and_determinism() -> None:
    seed = bytes(range(34))
    a = rej_ntt_poly(seed)
    assert a.shape == (256,)
    assert np.all(a >= 0) and np.all(a < Q)
    assert np.array_equal(rej_ntt_poly(seed), a)


@pytest.mark.parametrize("params", [ML_DSA_44, ML_DSA_65])
def test_expand_a(params) -> None:
    rho = bytes(range(32))
    A = expand_a(params, rho)
    assert A.shape == (params.k, params.l, 256)
    assert np.all(A >= 0) and np.all(A < Q)
    # index bytes are (s, r): A[r][s] must depend on both, and swapping differs
    if params.k != params.l or True:
        assert not np.array_equal(A[0][1], A[1][0])
    assert np.array_equal(expand_a(params, rho), A)


@pytest.mark.parametrize("params", [ML_DSA_44, ML_DSA_65])
def test_expand_s_bounds(params) -> None:
    rho_prime = bytes(range(64))
    s1, s2 = expand_s(params, rho_prime)
    assert s1.shape == (params.l, 256) and s2.shape == (params.k, 256)
    assert np.all(np.abs(s1) <= params.eta) and np.all(np.abs(s2) <= params.eta)
    assert np.array_equal(expand_s(params, rho_prime)[0], s1)


@pytest.mark.parametrize("params", [ML_DSA_44, ML_DSA_65])
def test_expand_mask_bounds(params) -> None:
    rho2 = bytes(range(64))
    kappa = params.l  # arbitrary multiple used mid-signing
    y = expand_mask(params, rho2, kappa)
    assert y.shape == (params.l, 256)
    g1 = params.gamma_1
    # coefficients lie in (-gamma1, gamma1]
    assert np.all(y > -g1) and np.all(y <= g1)
    assert np.array_equal(expand_mask(params, rho2, kappa), y)
    # a different offset gives a different mask
    assert not np.array_equal(expand_mask(params, rho2, kappa + params.l), y)
