"""Tests for the FO re-encryption check and implicit rejection.

When a ciphertext has been tampered with after encapsulation, the
re-encryption inside ML-KEM.Decaps will not match and the routine
must return the pseudorandom rejection value J(z || c) rather than
the would-be decryption. These tests verify both branches.
"""

import numpy as np
import pytest

from mlkem import ML_KEM_512, ML_KEM_768, ML_KEM_1024
from mlkem.hashes import J
from mlkem.ml_kem import (
    ml_kem_keygen_internal,
    ml_kem_encaps_internal,
    ml_kem_decaps_internal,
)


ALL_PARAMS = [ML_KEM_512, ML_KEM_768, ML_KEM_1024]


def _flip_byte(data: bytes, index: int) -> bytes:
    ba = bytearray(data)
    ba[index] ^= 0xFF
    return bytes(ba)


class TestImplicitRejection:
    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_tampered_ciphertext_returns_J_of_z_c(self, params) -> None:
        d = b"\x20" * 32
        z = b"\x21" * 32
        ek, dk = ml_kem_keygen_internal(params, d, z)
        m = b"\x22" * 32
        _K_encaps, c = ml_kem_encaps_internal(params, ek, m)

        c_bad = _flip_byte(c, 0)
        K_decaps = ml_kem_decaps_internal(params, dk, c_bad)
        # Must equal the deterministic J(z || c_bad) rejection value.
        assert K_decaps == J(z + c_bad)

    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_tampered_ciphertext_not_original_K(self, params) -> None:
        d = b"\x23" * 32
        z = b"\x24" * 32
        ek, dk = ml_kem_keygen_internal(params, d, z)
        m = b"\x25" * 32
        K_encaps, c = ml_kem_encaps_internal(params, ek, m)

        c_bad = _flip_byte(c, 0)
        K_decaps = ml_kem_decaps_internal(params, dk, c_bad)
        assert K_decaps != K_encaps

    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_flipping_different_bytes_gives_different_rejection_K(
        self, params
    ) -> None:
        d = b"\x26" * 32
        z = b"\x27" * 32
        ek, dk = ml_kem_keygen_internal(params, d, z)
        m = b"\x28" * 32
        _K_encaps, c = ml_kem_encaps_internal(params, ek, m)

        K_a = ml_kem_decaps_internal(params, dk, _flip_byte(c, 0))
        K_b = ml_kem_decaps_internal(params, dk, _flip_byte(c, 1))
        assert K_a != K_b

    @pytest.mark.parametrize("params", ALL_PARAMS, ids=lambda p: p.name)
    def test_rejection_depends_on_z(self, params) -> None:
        """Two keys with the same d but different z should reject a
        tampered ciphertext to different pseudorandom values."""
        d = b"\x29" * 32
        z_a = b"\xaa" * 32
        z_b = b"\xbb" * 32
        ek_a, dk_a = ml_kem_keygen_internal(params, d, z_a)
        ek_b, dk_b = ml_kem_keygen_internal(params, d, z_b)
        # K-PKE parts are identical because d matches, so ek matches too.
        assert ek_a == ek_b
        _K, c = ml_kem_encaps_internal(params, ek_a, b"\x00" * 32)
        c_bad = _flip_byte(c, 5)
        k_a = ml_kem_decaps_internal(params, dk_a, c_bad)
        k_b = ml_kem_decaps_internal(params, dk_b, c_bad)
        assert k_a != k_b
