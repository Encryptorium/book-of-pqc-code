"""Tests for the toy SIDH key exchange (isogenies.sidh)."""

import pytest

from isogenies.fp2 import fp2_eq
from isogenies.curve import is_on_curve, point_order, scalar_mul, point_add
from isogenies.sidh import (
    A0,
    B0,
    E_A,
    E_B,
    L_A,
    L_B,
    P,
    PA,
    PB,
    QA,
    QB,
    derive_alice,
    derive_bob,
    keygen_alice,
    keygen_bob,
    sidh_exchange,
    sidh_params,
)


class TestTorsionBases:
    def test_PA_on_curve(self):
        assert is_on_curve(PA, A0, B0, P)

    def test_QA_on_curve(self):
        assert is_on_curve(QA, A0, B0, P)

    def test_PB_on_curve(self):
        assert is_on_curve(PB, A0, B0, P)

    def test_QB_on_curve(self):
        assert is_on_curve(QB, A0, B0, P)

    def test_PA_order(self):
        assert point_order(PA, A0, P, L_A ** E_A + 1) == L_A ** E_A

    def test_QA_order(self):
        assert point_order(QA, A0, P, L_A ** E_A + 1) == L_A ** E_A

    def test_PB_order(self):
        assert point_order(PB, A0, P, L_B ** E_B + 1) == L_B ** E_B

    def test_QB_order(self):
        assert point_order(QB, A0, P, L_B ** E_B + 1) == L_B ** E_B

    def test_PA_QA_independent(self):
        """Q_A is not in <P_A>."""
        pa_set = set()
        for k in range(L_A ** E_A):
            pt = scalar_mul(k, PA, A0, P)
            if pt is not None:
                pa_set.add((pt[0], pt[1]))
        assert QA is not None
        assert (QA[0], QA[1]) not in pa_set

    def test_PB_QB_independent(self):
        """Q_B is not in <P_B>."""
        pb_set = set()
        for k in range(L_B ** E_B):
            pt = scalar_mul(k, PB, A0, P)
            if pt is not None:
                pb_set.add((pt[0], pt[1]))
        assert QB is not None
        assert (QB[0], QB[1]) not in pb_set


class TestSIDHExchange:
    @pytest.mark.parametrize(
        "alpha, beta",
        [(3, 5), (1, 2), (7, 13), (0, 1), (15, 26), (10, 20)],
    )
    def test_shared_secret_agreement(self, alpha, beta):
        j_alice, j_bob = sidh_exchange(alpha, beta)
        assert fp2_eq(j_alice, j_bob, P)

    def test_different_keys_different_secrets(self):
        j1_a, j1_b = sidh_exchange(1, 1)
        j2_a, j2_b = sidh_exchange(2, 2)
        # Different keys should (almost certainly) produce different secrets
        assert not fp2_eq(j1_a, j2_a, P)

    def test_keygen_alice_produces_valid_curve(self):
        a_A, b_A, phiA_PB, phiA_QB = keygen_alice(3)
        assert phiA_PB is not None, "phiA(PB) should not be O"
        assert phiA_QB is not None, "phiA(QB) should not be O"
        assert is_on_curve(phiA_PB, a_A, b_A, P)
        assert is_on_curve(phiA_QB, a_A, b_A, P)

    def test_keygen_bob_produces_valid_curve(self):
        a_B, b_B, phiB_PA, phiB_QA = keygen_bob(5)
        assert phiB_PA is not None, "phiB(PA) should not be O"
        assert phiB_QA is not None, "phiB(QA) should not be O"
        assert is_on_curve(phiB_PA, a_B, b_B, P)
        assert is_on_curve(phiB_QA, a_B, b_B, P)

    def test_params_dict(self):
        params = sidh_params()
        assert params["p"] == 431
        assert params["e_A"] == 4
        assert params["e_B"] == 3
