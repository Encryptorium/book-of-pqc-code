"""End-to-end KeyGen/Sign/Verify correctness (FIPS 204 Algorithms 2-3, 6-8).

These are honest-input correctness tests, independent of the ACVP KAT: a freshly
generated key signs and verifies its own messages, tampering is rejected, signing
is deterministic under a fixed rnd, and the Fiat-Shamir-with-aborts loop provably
runs more than one iteration on some inputs (the whole reason ML-DSA is a
*rejection-sampling* signature). The byte-for-byte standards conformance is in
test_vectors.py.
"""

from __future__ import annotations

import pytest

from mldsa.params import ML_DSA_44, ML_DSA_65, ML_DSA_87
from mldsa.ml_dsa import (
    ml_dsa_keygen_internal,
    ml_dsa_sign_internal,
    ml_dsa_verify_internal,
    ml_dsa_sign,
    ml_dsa_verify,
    _sign_internal_traced,
)

ALL = [ML_DSA_44, ML_DSA_65, ML_DSA_87]
DET = bytes(32)  # deterministic rnd = 0^32


@pytest.mark.parametrize("params", ALL)
def test_keygen_shapes(params) -> None:
    xi = bytes(range(32))
    pk, sk = ml_dsa_keygen_internal(params, xi)
    assert len(pk) == params.pk_len()
    assert len(sk) == params.sk_len()
    # deterministic in the seed
    assert ml_dsa_keygen_internal(params, xi) == (pk, sk)
    assert ml_dsa_keygen_internal(params, bytes([1]) + xi[1:]) != (pk, sk)


@pytest.mark.parametrize("params", ALL)
def test_sign_verify_roundtrip(params) -> None:
    xi = bytes([7]) * 32
    pk, sk = ml_dsa_keygen_internal(params, xi)
    m_prime = b"encryptorium book of pqc, chapter 12"
    sig = ml_dsa_sign_internal(params, sk, m_prime, DET)
    assert len(sig) == params.sig_len()
    assert ml_dsa_verify_internal(params, pk, m_prime, sig) is True


@pytest.mark.parametrize("params", ALL)
def test_deterministic_signing(params) -> None:
    xi = bytes([9]) * 32
    _, sk = ml_dsa_keygen_internal(params, xi)
    m_prime = b"same input, same signature"
    a = ml_dsa_sign_internal(params, sk, m_prime, DET)
    b = ml_dsa_sign_internal(params, sk, m_prime, DET)
    assert a == b


@pytest.mark.parametrize("params", ALL)
def test_tampered_signature_rejected(params) -> None:
    xi = bytes([3]) * 32
    pk, sk = ml_dsa_keygen_internal(params, xi)
    m_prime = b"authentic message"
    sig = bytearray(ml_dsa_sign_internal(params, sk, m_prime, DET))
    # flip a byte in the middle of z
    sig[params.c_tilde_len() + 50] ^= 0x01
    assert ml_dsa_verify_internal(params, pk, m_prime, bytes(sig)) is False


@pytest.mark.parametrize("params", ALL)
def test_wrong_message_rejected(params) -> None:
    xi = bytes([4]) * 32
    pk, sk = ml_dsa_keygen_internal(params, xi)
    sig = ml_dsa_sign_internal(params, sk, b"message A", DET)
    assert ml_dsa_verify_internal(params, pk, b"message B", sig) is False


@pytest.mark.parametrize("params", ALL)
def test_wrong_key_rejected(params) -> None:
    pk_a, sk_a = ml_dsa_keygen_internal(params, bytes([1]) * 32)
    pk_b, _ = ml_dsa_keygen_internal(params, bytes([2]) * 32)
    sig = ml_dsa_sign_internal(params, sk_a, b"m", DET)
    assert ml_dsa_verify_internal(params, pk_a, b"m", sig) is True
    assert ml_dsa_verify_internal(params, pk_b, b"m", sig) is False


def test_rejection_loop_triggers() -> None:
    # The abort loop should need more than one attempt on at least some inputs;
    # kappa advances by l per attempt, so a >1-iteration sign has kappa >= 2l.
    params = ML_DSA_65
    pk, sk = ml_dsa_keygen_internal(params, bytes([5]) * 32)
    iters = []
    for i in range(40):
        m = f"message number {i}".encode()
        sig, n = _sign_internal_traced(params, sk, m, DET)
        assert ml_dsa_verify_internal(params, pk, m, sig) is True
        iters.append(n)
    assert max(iters) > 1, f"expected some multi-iteration signs, got {iters}"
    assert min(iters) >= 1


@pytest.mark.parametrize("params", [ML_DSA_44, ML_DSA_87])
def test_external_context_wrapper_roundtrip(params) -> None:
    xi = bytes([6]) * 32
    pk, sk = ml_dsa_keygen_internal(params, xi)
    M = b"deployment-facing API message"
    ctx = b"my-application-context"
    sig = ml_dsa_sign(params, sk, M, ctx, DET)
    assert ml_dsa_verify(params, pk, M, sig, ctx) is True
    # wrong context must fail
    assert ml_dsa_verify(params, pk, M, sig, b"other-context") is False
    # empty context round-trips too
    sig0 = ml_dsa_sign(params, sk, M, b"", DET)
    assert ml_dsa_verify(params, pk, M, sig0, b"") is True
