"""Tests for ML-KEM parameter sets (FIPS 203 §8).

Covers the three standardized instances and the derived byte-length
computations exposed on the MLKEMParams dataclass. Values cross-check
against FIPS 203 Table 2 and the byte-length formulae in §6 and §7.
"""

import pytest

from mlkem import ML_KEM_512, ML_KEM_768, ML_KEM_1024, ParameterSet
from mlkem.params import params_for, MLKEMParams, ML_KEM_N, ML_KEM_Q


class TestSharedRing:
    def test_n_is_256(self) -> None:
        assert ML_KEM_N == 256
        for p in (ML_KEM_512, ML_KEM_768, ML_KEM_1024):
            assert p.n == 256

    def test_q_is_3329(self) -> None:
        assert ML_KEM_Q == 3329
        for p in (ML_KEM_512, ML_KEM_768, ML_KEM_1024):
            assert p.q == 3329


class TestParameterSets:
    def test_ml_kem_512(self) -> None:
        assert ML_KEM_512.name == "ML-KEM-512"
        assert ML_KEM_512.k == 2
        assert ML_KEM_512.eta_1 == 3
        assert ML_KEM_512.eta_2 == 2
        assert ML_KEM_512.d_u == 10
        assert ML_KEM_512.d_v == 4
        assert ML_KEM_512.nist_category == 1

    def test_ml_kem_768(self) -> None:
        assert ML_KEM_768.name == "ML-KEM-768"
        assert ML_KEM_768.k == 3
        assert ML_KEM_768.eta_1 == 2
        assert ML_KEM_768.eta_2 == 2
        assert ML_KEM_768.d_u == 10
        assert ML_KEM_768.d_v == 4
        assert ML_KEM_768.nist_category == 3

    def test_ml_kem_1024(self) -> None:
        assert ML_KEM_1024.name == "ML-KEM-1024"
        assert ML_KEM_1024.k == 4
        assert ML_KEM_1024.eta_1 == 2
        assert ML_KEM_1024.eta_2 == 2
        assert ML_KEM_1024.d_u == 11
        assert ML_KEM_1024.d_v == 5
        assert ML_KEM_1024.nist_category == 5

    def test_enum_dispatch(self) -> None:
        assert params_for(ParameterSet.ML_KEM_512) is ML_KEM_512
        assert params_for(ParameterSet.ML_KEM_768) is ML_KEM_768
        assert params_for(ParameterSet.ML_KEM_1024) is ML_KEM_1024


class TestDerivedLengths:
    # Canonical byte lengths from FIPS 203 Table 3.
    EK_LENGTHS = {2: 800, 3: 1184, 4: 1568}
    DK_LENGTHS = {2: 1632, 3: 2400, 4: 3168}
    CT_LENGTHS = {2: 768, 3: 1088, 4: 1568}

    @pytest.mark.parametrize(
        "params",
        [ML_KEM_512, ML_KEM_768, ML_KEM_1024],
        ids=lambda p: p.name,
    )
    def test_ek_length(self, params: MLKEMParams) -> None:
        assert params.ek_len() == self.EK_LENGTHS[params.k]

    @pytest.mark.parametrize(
        "params",
        [ML_KEM_512, ML_KEM_768, ML_KEM_1024],
        ids=lambda p: p.name,
    )
    def test_dk_length(self, params: MLKEMParams) -> None:
        assert params.dk_len() == self.DK_LENGTHS[params.k]

    @pytest.mark.parametrize(
        "params",
        [ML_KEM_512, ML_KEM_768, ML_KEM_1024],
        ids=lambda p: p.name,
    )
    def test_ciphertext_length(self, params: MLKEMParams) -> None:
        assert params.ct_len() == self.CT_LENGTHS[params.k]

    def test_shared_secret_length_is_32(self) -> None:
        for p in (ML_KEM_512, ML_KEM_768, ML_KEM_1024):
            assert p.shared_secret_len() == 32


class TestStructuralAsserts:
    def test_bad_k_rejected(self) -> None:
        with pytest.raises(AssertionError, match="k must be in"):
            MLKEMParams(
                name="bad",
                k=5,
                eta_1=2,
                eta_2=2,
                d_u=10,
                d_v=4,
                nist_category=1,
            )

    def test_bad_eta_1_rejected(self) -> None:
        with pytest.raises(AssertionError, match="eta_1 must be in"):
            MLKEMParams(
                name="bad",
                k=3,
                eta_1=4,
                eta_2=2,
                d_u=10,
                d_v=4,
                nist_category=3,
            )

    def test_bad_nist_category_rejected(self) -> None:
        with pytest.raises(AssertionError, match="nist_category"):
            MLKEMParams(
                name="bad",
                k=3,
                eta_1=2,
                eta_2=2,
                d_u=10,
                d_v=4,
                nist_category=2,
            )
