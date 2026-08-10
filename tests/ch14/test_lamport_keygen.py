"""Tests for Lamport OTS key generation."""

import hashlib

from lamport_merkle.lamport import keygen


SEED = b"ch14-keygen-test"


def test_keygen_returns_256_pairs():
    sk, pk = keygen(rng=SEED)
    assert len(sk) == 256
    assert len(pk) == 256


def test_each_secret_is_32_bytes():
    sk, _ = keygen(rng=SEED)
    for s0, s1 in sk:
        assert len(s0) == 32
        assert len(s1) == 32


def test_public_key_is_sha256_of_secret():
    sk, pk = keygen(rng=SEED)
    for i in range(256):
        assert pk[i][0] == hashlib.sha256(sk[i][0]).digest()
        assert pk[i][1] == hashlib.sha256(sk[i][1]).digest()


def test_two_keygen_calls_differ():
    _, pk1 = keygen()
    _, pk2 = keygen()
    assert pk1 != pk2


def test_deterministic_keygen_reproduces():
    sk1, pk1 = keygen(rng=SEED)
    sk2, pk2 = keygen(rng=SEED)
    assert sk1 == sk2
    assert pk1 == pk2
