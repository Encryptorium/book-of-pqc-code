"""Keygen, sign, and verify for the toy UOV scheme."""

import random

import pytest

from multivariate.uov import TOY, UOVParams, keygen, sign, verify


def test_round_trip_at_the_chapter_parameters():
    secret = keygen(random.Random(0), TOY)
    target = [3, 5]
    signature = sign(secret, target, random.Random(1))
    assert verify(secret.public, target, signature) is True


def test_signature_reproduces_the_chapter_output():
    """The chapter prints signature [4, 4, 4, 2, 3] at these two seeds."""
    secret = keygen(random.Random(0), TOY)
    signature = sign(secret, [3, 5], random.Random(1))
    assert signature == [4, 4, 4, 2, 3]


def test_verification_rejects_a_wrong_target():
    secret = keygen(random.Random(0), TOY)
    signature = sign(secret, [3, 5], random.Random(1))
    assert verify(secret.public, [3, 6], signature) is False


def test_verification_rejects_a_perturbed_signature():
    secret = keygen(random.Random(0), TOY)
    target = [3, 5]
    signature = sign(secret, target, random.Random(1))
    for position in range(TOY.n):
        tampered = list(signature)
        tampered[position] = (tampered[position] + 1) % TOY.q
        assert verify(secret.public, target, tampered) is False


def test_verification_rejects_a_wrong_length_signature():
    secret = keygen(random.Random(0), TOY)
    assert verify(secret.public, [3, 5], [1, 2, 3]) is False


def test_every_target_in_the_toy_image_is_signable():
    """All 49 targets over GF(7)^2 sign and verify."""
    secret = keygen(random.Random(0), TOY)
    rng = random.Random(2)
    for a in range(TOY.q):
        for b in range(TOY.q):
            signature = sign(secret, [a, b], rng)
            assert verify(secret.public, [a, b], signature) is True


def test_round_trip_at_larger_parameters():
    """The construction is not tuned to (5, 2, 7)."""
    params = UOVParams(n=12, m=4, q=13)
    secret = keygen(random.Random(7), params)
    rng = random.Random(8)
    for _ in range(10):
        target = [rng.randrange(params.q) for _ in range(params.m)]
        signature = sign(secret, target, rng)
        assert verify(secret.public, target, signature) is True


def test_keygen_is_deterministic_under_a_seed():
    first = keygen(random.Random(42), TOY)
    second = keygen(random.Random(42), TOY)
    assert first.T == second.T
    assert first.F == second.F
    assert first.public.P == second.public.P


def test_sign_rejects_a_wrong_length_target():
    secret = keygen(random.Random(0), TOY)
    with pytest.raises(ValueError):
        sign(secret, [1, 2, 3], random.Random(1))
