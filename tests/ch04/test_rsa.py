"""Tests for the toy textbook RSA in ``classical.rsa``."""

import random

from classical import rsa


def test_keygen_produces_coprime_exponent():
    pk, sk = rsa.keygen(bits=64, rng=random.Random(0))
    phi = (sk.p - 1) * (sk.q - 1)
    assert (pk.e * sk.d) % phi == 1
    assert pk.n == sk.n == sk.p * sk.q


def test_encrypt_decrypt_round_trip():
    pk, sk = rsa.keygen(bits=64, rng=random.Random(1))
    # Fix a toy message strictly less than the modulus.
    m = 0xDEADBEEF
    assert m < pk.n
    c = rsa.encrypt(pk, m)
    assert c != m  # with overwhelming probability for a random key
    assert rsa.decrypt(sk, c) == m


def test_sign_verify_round_trip():
    pk, sk = rsa.keygen(bits=64, rng=random.Random(2))
    m = 0xCAFEBABE
    assert m < pk.n
    s = rsa.sign(sk, m)
    assert rsa.verify(pk, m, s) is True


def test_verify_rejects_bad_signature():
    pk, sk = rsa.keygen(bits=64, rng=random.Random(3))
    m = 0x1234
    s = rsa.sign(sk, m)
    # Flip a bit.
    bad = s ^ 1
    assert rsa.verify(pk, m, bad) is False


def test_keygen_uses_65537_as_public_exponent():
    pk, _ = rsa.keygen(bits=64, rng=random.Random(4))
    assert pk.e == 65537
