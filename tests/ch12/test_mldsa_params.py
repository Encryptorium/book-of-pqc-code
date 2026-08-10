"""ML-DSA parameter-set contract (FIPS 204 Table 1 + the derived byte lengths).

Every field is cross-checked against FIPS 204's standardized parameter table,
and the derived key/signature byte lengths are checked against the published
sizes (Table 2) that the vendored ACVP vectors also exhibit. A mismatch here is
the earliest, cheapest place to catch a wrong constant before it corrupts every
downstream module.
"""

from __future__ import annotations

import pytest

from mldsa.params import (
    ML_DSA_Q,
    ML_DSA_N,
    ML_DSA_D,
    ML_DSA_ZETA,
    MLDSAParams,
    ParameterSet,
    ML_DSA_44,
    ML_DSA_65,
    ML_DSA_87,
    params_for,
)


def test_shared_ring_constants() -> None:
    assert ML_DSA_Q == 8380417
    assert ML_DSA_N == 256
    assert ML_DSA_D == 13
    assert ML_DSA_ZETA == 1753
    # q is prime and q ≡ 1 (mod 2n): the full 256-point NTT exists.
    assert ML_DSA_Q % (2 * ML_DSA_N) == 1


# FIPS 204 Table 1 (algorithm parameters) and Table 2 (sizes in bytes).
EXPECTED = {
    "ML-DSA-44": dict(
        k=4, l=4, eta=2, tau=39, gamma_1=1 << 17, gamma_2=(8380417 - 1) // 88,
        omega=80, lam=128, nist_category=2, beta=39 * 2,
        c_tilde=32, pk=1312, sk=2560, sig=2420,
    ),
    "ML-DSA-65": dict(
        k=6, l=5, eta=4, tau=49, gamma_1=1 << 19, gamma_2=(8380417 - 1) // 32,
        omega=55, lam=192, nist_category=3, beta=49 * 4,
        c_tilde=48, pk=1952, sk=4032, sig=3309,
    ),
    "ML-DSA-87": dict(
        k=8, l=7, eta=2, tau=60, gamma_1=1 << 19, gamma_2=(8380417 - 1) // 32,
        omega=75, lam=256, nist_category=5, beta=60 * 2,
        c_tilde=64, pk=2592, sk=4896, sig=4627,
    ),
}

ALL = {"ML-DSA-44": ML_DSA_44, "ML-DSA-65": ML_DSA_65, "ML-DSA-87": ML_DSA_87}


@pytest.mark.parametrize("name", list(EXPECTED.keys()))
def test_parameter_fields(name: str) -> None:
    p = ALL[name]
    e = EXPECTED[name]
    assert p.name == name
    assert p.k == e["k"]
    assert p.l == e["l"]
    assert p.eta == e["eta"]
    assert p.tau == e["tau"]
    assert p.gamma_1 == e["gamma_1"]
    assert p.gamma_2 == e["gamma_2"]
    assert p.omega == e["omega"]
    assert p.lam == e["lam"]
    assert p.nist_category == e["nist_category"]
    assert p.beta == e["beta"]


@pytest.mark.parametrize("name", list(EXPECTED.keys()))
def test_derived_byte_lengths(name: str) -> None:
    p = ALL[name]
    e = EXPECTED[name]
    assert p.c_tilde_len() == e["c_tilde"]
    assert p.pk_len() == e["pk"]
    assert p.sk_len() == e["sk"]
    assert p.sig_len() == e["sig"]


@pytest.mark.parametrize("name", list(EXPECTED.keys()))
def test_bit_width_helpers(name: str) -> None:
    p = ALL[name]
    # BitPack(s, eta, eta) uses bitlen(2*eta): 3 bits for eta=2, 4 bits for eta=4.
    assert p.eta_bits() == (3 if p.eta == 2 else 4)
    # BitPack(z, gamma1-1, gamma1) uses bitlen(2*gamma1-1): 18 for 2^17, 20 for 2^19.
    assert p.gamma1_bits() == (18 if p.gamma_1 == (1 << 17) else 20)
    # w1Encode: SimpleBitPack(w1, (q-1)/(2*gamma2) - 1). This is the classic
    # off-by-one bug surface: 6 bits for ML-DSA-44, 4 bits for 65/87.
    assert p.w1_bits() == (6 if name == "ML-DSA-44" else 4)


def test_params_for_dispatch() -> None:
    assert params_for(ParameterSet.ML_DSA_44) is ML_DSA_44
    assert params_for(ParameterSet.ML_DSA_65) is ML_DSA_65
    assert params_for(ParameterSet.ML_DSA_87) is ML_DSA_87


def test_frozen_and_validated() -> None:
    with pytest.raises(Exception):
        ML_DSA_44.k = 5  # frozen dataclass
    with pytest.raises(AssertionError):
        MLDSAParams(
            name="bad", k=4, l=4, eta=3, tau=39, gamma_1=1 << 17,
            gamma_2=(8380417 - 1) // 88, omega=80, lam=128, nist_category=2,
        )
