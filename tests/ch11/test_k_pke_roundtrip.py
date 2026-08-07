"""Round-trip tests for K-PKE at all three ML-KEM parameter sets.

Covers K-PKE.KeyGen output shape, K-PKE.Encrypt / K-PKE.Decrypt
round-trip on random 32-byte messages and fresh coin seeds, and the
shape constraints on ek_PKE, dk_PKE, and ciphertext bytes.

K-PKE is IND-CPA; the ML-KEM wrapper in Chapter 11 lifts it to
IND-CCA2 via the FO transform. These tests only check correctness,
not security.
"""

import numpy as np
import pytest

from mlkem import ML_KEM_512, ML_KEM_768, ML_KEM_1024
from mlkem.k_pke import k_pke_keygen, k_pke_encrypt, k_pke_decrypt


ALL_PARAMS = [ML_KEM_512, ML_KEM_768, ML_KEM_1024]


class TestKeyGenShapes:
    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_ek_and_dk_lengths(self, params) -> None:
        d = b"\x00" * 32
        ek, dk = k_pke_keygen(params, d)
        assert len(ek) == params.ek_len()
        assert len(dk) == params.dk_pke_len()

    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_deterministic(self, params) -> None:
        d = b"\x42" * 32
        a = k_pke_keygen(params, d)
        b = k_pke_keygen(params, d)
        assert a == b

    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_different_seeds_give_different_keys(self, params) -> None:
        ek_a, dk_a = k_pke_keygen(params, b"\x00" * 32)
        ek_b, dk_b = k_pke_keygen(params, b"\x01" * 32)
        assert ek_a != ek_b
        assert dk_a != dk_b


class TestEncryptShapes:
    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_ciphertext_length(self, params) -> None:
        ek, _ = k_pke_keygen(params, b"\x00" * 32)
        c = k_pke_encrypt(params, ek, b"\x00" * 32, b"\x01" * 32)
        assert len(c) == params.ct_len()


class TestRoundTrip:
    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_round_trip_zero_message(self, params) -> None:
        d = b"\x05" * 32
        ek, dk = k_pke_keygen(params, d)
        m = b"\x00" * 32
        r = b"\x06" * 32
        c = k_pke_encrypt(params, ek, m, r)
        m_out = k_pke_decrypt(params, dk, c)
        assert m_out == m

    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_round_trip_all_ones(self, params) -> None:
        d = b"\x07" * 32
        ek, dk = k_pke_keygen(params, d)
        m = b"\xff" * 32
        r = b"\x08" * 32
        c = k_pke_encrypt(params, ek, m, r)
        m_out = k_pke_decrypt(params, dk, c)
        assert m_out == m

    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_round_trip_many_random_messages(self, params) -> None:
        rng = np.random.default_rng(seed=20260411)
        d = rng.integers(0, 256, size=32, dtype=np.uint8).tobytes()
        ek, dk = k_pke_keygen(params, d)
        for _ in range(5):
            m = rng.integers(0, 256, size=32, dtype=np.uint8).tobytes()
            r = rng.integers(0, 256, size=32, dtype=np.uint8).tobytes()
            c = k_pke_encrypt(params, ek, m, r)
            m_out = k_pke_decrypt(params, dk, c)
            assert m_out == m

    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_different_coins_give_different_ciphertexts(
        self, params
    ) -> None:
        ek, _ = k_pke_keygen(params, b"\x09" * 32)
        m = b"\x0a" * 32
        c1 = k_pke_encrypt(params, ek, m, b"\x0b" * 32)
        c2 = k_pke_encrypt(params, ek, m, b"\x0c" * 32)
        assert c1 != c2
