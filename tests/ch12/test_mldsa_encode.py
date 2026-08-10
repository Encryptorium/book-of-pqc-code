"""Serialization: bit-packing and the pk/sk/sig encoders (FIPS 204 §7.1-7.2).

Every ML-DSA object on the wire is a little-endian bit-packing of length-256
polynomials at a field-specific width. The round-trip tests here pin the packers
without an external vector; the malformed-hint tests pin the HintBitUnpack
rejection logic that the sigVer(invalid) "modified hint" vector exercises. Byte
lengths are checked against the derived params so a wrong width fails loudly.
"""

from __future__ import annotations

import numpy as np
import pytest

from mldsa.params import (
    ML_DSA_Q as Q, ML_DSA_D as D, ML_DSA_44, ML_DSA_65, ML_DSA_87,
)
from mldsa.encode import (
    simple_bit_pack,
    simple_bit_unpack,
    bit_pack,
    bit_unpack,
    hint_bit_pack,
    hint_bit_unpack,
    pk_encode,
    pk_decode,
    sk_encode,
    sk_decode,
    sig_encode,
    sig_decode,
    w1_encode,
)


@pytest.mark.parametrize("b", [1, 3, 15, 43, 1023, 4096, (1 << 19)])
def test_simple_bit_pack_round_trip(b: int) -> None:
    rng = np.random.default_rng(b)
    w = rng.integers(0, b + 1, size=256, dtype=np.int64)
    packed = simple_bit_pack(w, b)
    assert len(packed) == 32 * b.bit_length()
    assert np.array_equal(simple_bit_unpack(packed, b), w)


@pytest.mark.parametrize("a,b", [(2, 2), (4, 4), (4095, 4096), ((1 << 17) - 1, 1 << 17), ((1 << 19) - 1, 1 << 19)])
def test_bit_pack_round_trip(a: int, b: int) -> None:
    rng = np.random.default_rng(a + b)
    w = rng.integers(-a, b + 1, size=256, dtype=np.int64)
    packed = bit_pack(w, a, b)
    assert len(packed) == 32 * (a + b).bit_length()
    assert np.array_equal(bit_unpack(packed, a, b), w)


def test_bit_pack_extreme_values() -> None:
    a, b = 4095, 4096
    w = np.array([-a, b] * 128, dtype=np.int64)
    assert np.array_equal(bit_unpack(bit_pack(w, a, b), a, b), w)


@pytest.mark.parametrize("params", [ML_DSA_44, ML_DSA_65, ML_DSA_87])
def test_hint_pack_round_trip(params) -> None:
    rng = np.random.default_rng(params.k)
    h = np.zeros((params.k, 256), dtype=np.int64)
    # scatter <= omega ones, strictly increasing positions within each poly
    budget = params.omega
    for i in range(params.k):
        if budget <= 0:
            break
        cnt = min(int(rng.integers(0, 4)), budget)
        pos = sorted(rng.choice(256, size=cnt, replace=False).tolist())
        for p in pos:
            h[i][p] = 1
        budget -= cnt
    y = hint_bit_pack(params, h)
    assert len(y) == params.omega + params.k
    recovered = hint_bit_unpack(params, y)
    assert recovered is not None
    assert np.array_equal(recovered, h)


def test_hint_unpack_rejects_nonzero_padding() -> None:
    p = ML_DSA_44
    h = np.zeros((p.k, 256), dtype=np.int64)
    h[0][5] = 1
    y = bytearray(hint_bit_pack(p, h))
    # index after packing is 1; corrupt an unused position slot (must be 0).
    y[10] = 200
    assert hint_bit_unpack(p, bytes(y)) is None


def test_hint_unpack_rejects_non_increasing() -> None:
    p = ML_DSA_44
    y = bytearray(p.omega + p.k)
    # poly 0 claims two positions but they are not strictly increasing.
    y[0] = 40
    y[1] = 40
    y[p.omega + 0] = 2
    for i in range(1, p.k):
        y[p.omega + i] = 2
    assert hint_bit_unpack(p, bytes(y)) is None


def test_hint_unpack_rejects_bad_end_marker() -> None:
    p = ML_DSA_44
    y = bytearray(p.omega + p.k)
    y[p.omega + 0] = p.omega + 1  # end index exceeds omega
    assert hint_bit_unpack(p, bytes(y)) is None


@pytest.mark.parametrize("params", [ML_DSA_44, ML_DSA_65, ML_DSA_87])
def test_pk_round_trip(params) -> None:
    rng = np.random.default_rng(1)
    t1_hi = (1 << params.t1_bits()) - 1
    rho = bytes(rng.integers(0, 256, size=32, dtype=np.int64).tolist())
    t1 = rng.integers(0, t1_hi + 1, size=(params.k, 256), dtype=np.int64)
    pk = pk_encode(params, rho, t1)
    assert len(pk) == params.pk_len()
    rho2, t1_2 = pk_decode(params, pk)
    assert rho2 == rho
    assert np.array_equal(t1_2, t1)


@pytest.mark.parametrize("params", [ML_DSA_44, ML_DSA_65, ML_DSA_87])
def test_sk_round_trip(params) -> None:
    rng = np.random.default_rng(2)
    rho = bytes(rng.integers(0, 256, size=32, dtype=np.int64).tolist())
    K = bytes(rng.integers(0, 256, size=32, dtype=np.int64).tolist())
    tr = bytes(rng.integers(0, 256, size=64, dtype=np.int64).tolist())
    eta = params.eta
    s1 = rng.integers(-eta, eta + 1, size=(params.l, 256), dtype=np.int64)
    s2 = rng.integers(-eta, eta + 1, size=(params.k, 256), dtype=np.int64)
    t0_bound = 1 << (D - 1)
    t0 = rng.integers(-t0_bound + 1, t0_bound + 1, size=(params.k, 256), dtype=np.int64)
    sk = sk_encode(params, rho, K, tr, s1, s2, t0)
    assert len(sk) == params.sk_len()
    rho2, K2, tr2, s1_2, s2_2, t0_2 = sk_decode(params, sk)
    assert (rho2, K2, tr2) == (rho, K, tr)
    assert np.array_equal(s1_2, s1)
    assert np.array_equal(s2_2, s2)
    assert np.array_equal(t0_2, t0)


@pytest.mark.parametrize("params", [ML_DSA_44, ML_DSA_65, ML_DSA_87])
def test_sig_round_trip(params) -> None:
    rng = np.random.default_rng(3)
    c_tilde = bytes(rng.integers(0, 256, size=params.c_tilde_len(), dtype=np.int64).tolist())
    g1 = params.gamma_1
    z = rng.integers(-(g1 - 1), g1 + 1, size=(params.l, 256), dtype=np.int64)
    h = np.zeros((params.k, 256), dtype=np.int64)
    h[0][7] = 1
    if params.k > 1:
        h[1][200] = 1
    sig = sig_encode(params, c_tilde, z, h)
    assert len(sig) == params.sig_len()
    c2, z2, h2 = sig_decode(params, sig)
    assert c2 == c_tilde
    assert np.array_equal(z2, z)
    assert h2 is not None and np.array_equal(h2, h)


@pytest.mark.parametrize("params", [ML_DSA_44, ML_DSA_65, ML_DSA_87])
def test_w1_encode_length_and_values(params) -> None:
    rng = np.random.default_rng(4)
    hi = (Q - 1) // (2 * params.gamma_2) - 1
    w1 = rng.integers(0, hi + 1, size=(params.k, 256), dtype=np.int64)
    packed = w1_encode(params, w1)
    assert len(packed) == 32 * params.w1_bits() * params.k
    # each poly's slice unpacks back
    stride = 32 * params.w1_bits()
    for i in range(params.k):
        chunk = packed[i * stride:(i + 1) * stride]
        assert np.array_equal(simple_bit_unpack(chunk, hi), w1[i])
