"""Tests for the toy ECDSA in ``classical.ecdsa_secp256k1``."""

import random

from classical import ecdsa_secp256k1 as ecdsa
from classical.curve import G, N, is_on_curve, scalar_mul


def test_generator_is_on_curve():
    assert is_on_curve(G)


def test_group_order_kills_generator():
    # N * G == identity.
    assert scalar_mul(N, G).is_infinity


def test_keygen_public_point_on_curve():
    sk, pk = ecdsa.keygen(rng=random.Random(0))
    assert 1 <= sk.d < N
    assert is_on_curve(pk.Q)
    # And Q == d * G.
    expected = scalar_mul(sk.d, G)
    assert pk.Q == expected


def test_sign_verify_round_trip():
    sk, pk = ecdsa.keygen(rng=random.Random(1))
    msg = b"book of pqc chapter 4"
    k = 0x1234567890ABCDEF  # fixed toy nonce; never do this in real code
    sig = ecdsa.sign(sk, msg, k)
    assert ecdsa.verify(pk, msg, sig) is True


def test_verify_rejects_modified_message():
    sk, pk = ecdsa.keygen(rng=random.Random(2))
    msg = b"original message"
    k = 0xFEDCBA0987654321
    sig = ecdsa.sign(sk, msg, k)
    assert ecdsa.verify(pk, b"tampered message", sig) is False


def test_verify_rejects_wrong_key():
    sk1, _ = ecdsa.keygen(rng=random.Random(3))
    _, pk2 = ecdsa.keygen(rng=random.Random(4))
    msg = b"signed under sk1"
    k = 0xABCDEF0123456789
    sig = ecdsa.sign(sk1, msg, k)
    assert ecdsa.verify(pk2, msg, sig) is False


def test_verify_rejects_out_of_range_signature():
    _, pk = ecdsa.keygen(rng=random.Random(5))
    msg = b"anything"
    assert ecdsa.verify(pk, msg, (0, 1)) is False
    assert ecdsa.verify(pk, msg, (1, 0)) is False
    assert ecdsa.verify(pk, msg, (N, 1)) is False
    assert ecdsa.verify(pk, msg, (1, N)) is False
