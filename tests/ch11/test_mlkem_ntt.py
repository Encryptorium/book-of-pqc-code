"""Tests for the specialized partial NTT in R_3329 (FIPS 203 §4.3).

Covers the primitive root arithmetic, the bit-reversal helper, the
NTT and inverse-NTT round-trip, and the key identity
``inverse_ntt(multiply_ntts(ntt(f), ntt(g))) == f * g in R_q``
verified against an independent schoolbook multiplication.
"""

import numpy as np
import pytest

from mlkem.ntt import (
    Q,
    N,
    ZETA,
    INV_128,
    ZETAS_NTT,
    ZETAS_MUL,
    _bit_rev_7,
    ntt,
    inverse_ntt,
    multiply_ntts,
    schoolbook_ring_multiply,
    _base_case_multiply,
)


class TestConstants:
    def test_q_and_n(self) -> None:
        assert Q == 3329
        assert N == 256

    def test_zeta_is_17(self) -> None:
        assert ZETA == 17

    def test_zeta_has_order_256(self) -> None:
        # zeta^256 must equal 1 and no smaller power should.
        assert pow(ZETA, 256, Q) == 1
        for d in (1, 2, 4, 8, 16, 32, 64, 128):
            assert pow(ZETA, d, Q) != 1

    def test_zeta_128_is_minus_one(self) -> None:
        # Consequence of zeta having order 256: zeta^128 = -1.
        assert pow(ZETA, 128, Q) == Q - 1

    def test_inv_128_is_3303(self) -> None:
        assert INV_128 == 3303
        assert (128 * INV_128) % Q == 1


class TestBitReversal:
    def test_bit_rev_7_known_values(self) -> None:
        # BitRev_7(1) = 1000000_2 = 64, BitRev_7(2) = 0100000_2 = 32,
        # BitRev_7(64) = 0000001_2 = 1, BitRev_7(127) = 127 (palindrome).
        assert _bit_rev_7(0) == 0
        assert _bit_rev_7(1) == 64
        assert _bit_rev_7(2) == 32
        assert _bit_rev_7(4) == 16
        assert _bit_rev_7(64) == 1
        assert _bit_rev_7(127) == 127

    def test_bit_rev_7_is_involution(self) -> None:
        for i in range(128):
            assert _bit_rev_7(_bit_rev_7(i)) == i


class TestZetaTables:
    def test_zetas_ntt_has_128_entries(self) -> None:
        assert len(ZETAS_NTT) == 128

    def test_zetas_ntt_entry_0_is_1(self) -> None:
        # ζ^{BitRev_7(0)} = ζ^0 = 1. Entry is unused by algorithms but
        # kept for index alignment.
        assert ZETAS_NTT[0] == 1

    def test_zetas_ntt_entry_1_is_1729(self) -> None:
        # FIPS 203 Appendix A: ζ^{BitRev_7(1)} = ζ^64 = 17^64 mod 3329.
        # The standard tabulates this as 1729.
        assert ZETAS_NTT[1] == 1729

    def test_zetas_mul_128_entries(self) -> None:
        assert len(ZETAS_MUL) == 128

    def test_zetas_mul_entry_0_is_zeta(self) -> None:
        # ζ^(2 * BitRev_7(0) + 1) = ζ^1 = 17.
        assert ZETAS_MUL[0] == 17


class TestNTTRoundTrip:
    def test_round_trip_zero(self) -> None:
        f = np.zeros(N, dtype=np.int64)
        assert np.array_equal(inverse_ntt(ntt(f)), f)

    def test_round_trip_unit(self) -> None:
        # f = 1 (constant polynomial).
        f = np.zeros(N, dtype=np.int64)
        f[0] = 1
        assert np.array_equal(inverse_ntt(ntt(f)), f)

    def test_round_trip_x(self) -> None:
        # f = x.
        f = np.zeros(N, dtype=np.int64)
        f[1] = 1
        assert np.array_equal(inverse_ntt(ntt(f)), f)

    def test_round_trip_random(self) -> None:
        rng = np.random.default_rng(seed=20260411)
        for _ in range(10):
            f = rng.integers(0, Q, size=N, dtype=np.int64)
            assert np.array_equal(inverse_ntt(ntt(f)), f)

    def test_ntt_does_not_mutate_input(self) -> None:
        rng = np.random.default_rng(seed=20260411)
        f = rng.integers(0, Q, size=N, dtype=np.int64)
        original = f.copy()
        _ = ntt(f)
        assert np.array_equal(f, original)


class TestMultiplyNTTs:
    def test_one_times_one(self) -> None:
        # f = g = 1 in R_q, so f * g = 1.
        one = np.zeros(N, dtype=np.int64)
        one[0] = 1
        h = inverse_ntt(multiply_ntts(ntt(one), ntt(one)))
        assert np.array_equal(h, one)

    def test_x_times_x(self) -> None:
        # f = g = x, so f * g = x^2.
        x = np.zeros(N, dtype=np.int64)
        x[1] = 1
        expected = np.zeros(N, dtype=np.int64)
        expected[2] = 1
        h = inverse_ntt(multiply_ntts(ntt(x), ntt(x)))
        assert np.array_equal(h, expected)

    def test_negacyclic_wrap(self) -> None:
        # f = x^255, g = x, so f * g = x^256 = -1 in R_q.
        f = np.zeros(N, dtype=np.int64)
        f[255] = 1
        g = np.zeros(N, dtype=np.int64)
        g[1] = 1
        expected = np.zeros(N, dtype=np.int64)
        expected[0] = Q - 1  # -1 mod q
        h = inverse_ntt(multiply_ntts(ntt(f), ntt(g)))
        assert np.array_equal(h, expected)

    @pytest.mark.parametrize("seed", [0, 1, 2, 7, 20260411])
    def test_ntt_product_matches_schoolbook(self, seed: int) -> None:
        rng = np.random.default_rng(seed=seed)
        f = rng.integers(0, Q, size=N, dtype=np.int64)
        g = rng.integers(0, Q, size=N, dtype=np.int64)
        h_ntt = inverse_ntt(multiply_ntts(ntt(f), ntt(g)))
        h_school = schoolbook_ring_multiply(f, g)
        assert np.array_equal(h_ntt, h_school)


class TestBaseCaseMultiply:
    def test_zero_times_zero(self) -> None:
        assert _base_case_multiply(0, 0, 0, 0, 1) == (0, 0)

    def test_constant_product(self) -> None:
        # (3 + 0 X) * (5 + 0 X) = 15 mod q in every slot.
        c0, c1 = _base_case_multiply(3, 0, 5, 0, 1234)
        assert c0 == 15
        assert c1 == 0

    def test_x_times_x_gives_gamma(self) -> None:
        # (0 + 1 X) * (0 + 1 X) mod (X^2 - gamma) = gamma.
        c0, c1 = _base_case_multiply(0, 1, 0, 1, 17)
        assert c0 == 17
        assert c1 == 0
