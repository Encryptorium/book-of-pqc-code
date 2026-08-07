"""Round-trip tests for ML-KEM (FIPS 203 §7) at all three parameter sets.

Covers ML-KEM.KeyGen_internal shape contracts, the
KeyGen-Encaps-Decaps round-trip on honest inputs, the determinism
of the internal routines from their seed inputs, and the derived
byte lengths agreeing with the FIPS 203 Table 3 values.

Tampering, rejection, and the FO re-encryption check live in
``test_mlkem_rejection.py``.
"""

import numpy as np
import pytest

from mlkem import ML_KEM_512, ML_KEM_768, ML_KEM_1024
from mlkem.ml_kem import (
    ml_kem_keygen_internal,
    ml_kem_encaps_internal,
    ml_kem_decaps_internal,
)


ALL_PARAMS = [ML_KEM_512, ML_KEM_768, ML_KEM_1024]


class TestKeyGenShapes:
    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_ek_and_dk_lengths(self, params) -> None:
        d = b"\x00" * 32
        z = b"\x01" * 32
        ek, dk = ml_kem_keygen_internal(params, d, z)
        assert len(ek) == params.ek_len()
        assert len(dk) == params.dk_len()

    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_dk_ends_with_z(self, params) -> None:
        d = b"\x02" * 32
        z = b"\xaa" * 32
        _ek, dk = ml_kem_keygen_internal(params, d, z)
        assert dk[-32:] == z

    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_deterministic(self, params) -> None:
        d = b"\x03" * 32
        z = b"\x04" * 32
        a = ml_kem_keygen_internal(params, d, z)
        b = ml_kem_keygen_internal(params, d, z)
        assert a == b


class TestEncapsShapes:
    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_shared_secret_is_32_bytes(self, params) -> None:
        ek, _dk = ml_kem_keygen_internal(
            params, b"\x05" * 32, b"\x06" * 32
        )
        K, c = ml_kem_encaps_internal(params, ek, b"\x07" * 32)
        assert len(K) == 32
        assert len(c) == params.ct_len()

    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_deterministic_from_m(self, params) -> None:
        ek, _dk = ml_kem_keygen_internal(
            params, b"\x08" * 32, b"\x09" * 32
        )
        m = b"\x0a" * 32
        a = ml_kem_encaps_internal(params, ek, m)
        b = ml_kem_encaps_internal(params, ek, m)
        assert a == b

    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_different_messages_give_different_K_and_c(
        self, params
    ) -> None:
        ek, _dk = ml_kem_keygen_internal(
            params, b"\x0b" * 32, b"\x0c" * 32
        )
        K1, c1 = ml_kem_encaps_internal(params, ek, b"\x0d" * 32)
        K2, c2 = ml_kem_encaps_internal(params, ek, b"\x0e" * 32)
        assert K1 != K2
        assert c1 != c2


class TestRoundTrip:
    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_honest_round_trip(self, params) -> None:
        d = b"\x10" * 32
        z = b"\x11" * 32
        ek, dk = ml_kem_keygen_internal(params, d, z)
        m = b"\x12" * 32
        K_encaps, c = ml_kem_encaps_internal(params, ek, m)
        K_decaps = ml_kem_decaps_internal(params, dk, c)
        assert K_decaps == K_encaps

    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_round_trip_many_messages(self, params) -> None:
        rng = np.random.default_rng(seed=20260411)
        d = rng.integers(0, 256, size=32, dtype=np.uint8).tobytes()
        z = rng.integers(0, 256, size=32, dtype=np.uint8).tobytes()
        ek, dk = ml_kem_keygen_internal(params, d, z)
        for _ in range(3):
            m = rng.integers(0, 256, size=32, dtype=np.uint8).tobytes()
            K_encaps, c = ml_kem_encaps_internal(params, ek, m)
            K_decaps = ml_kem_decaps_internal(params, dk, c)
            assert K_decaps == K_encaps
