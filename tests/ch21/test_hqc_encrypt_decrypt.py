"""Tests for HQC encrypt/decrypt round-trip correctness."""

import random

from hqc.hqc import keygen, encrypt, decrypt


N, W, W_R, W_E, R = 83, 3, 3, 3, 17
K = N // R   # 4


def test_round_trip_single_message():
    pk, sk = keygen(N, W, W_R, W_E, R, random.Random(42))
    msg = [1, 0, 1, 1]
    ct = encrypt(pk, msg, random.Random(100))
    recovered = decrypt(sk, pk, ct)
    assert recovered == msg


def test_round_trip_zero_message():
    pk, sk = keygen(N, W, W_R, W_E, R, random.Random(42))
    msg = [0] * K
    ct = encrypt(pk, msg, random.Random(100))
    recovered = decrypt(sk, pk, ct)
    assert recovered == msg


def test_round_trip_all_ones():
    pk, sk = keygen(N, W, W_R, W_E, R, random.Random(42))
    msg = [1] * K
    ct = encrypt(pk, msg, random.Random(100))
    recovered = decrypt(sk, pk, ct)
    assert recovered == msg


def test_round_trip_all_messages():
    """All 2^k = 16 possible messages round-trip."""
    pk, sk = keygen(N, W, W_R, W_E, R, random.Random(42))
    for i in range(2**K):
        msg = [(i >> b) & 1 for b in range(K)]
        ct = encrypt(pk, msg, random.Random(i + 1000))
        recovered = decrypt(sk, pk, ct)
        assert recovered == msg, f"Failed for message {msg}"


def test_round_trip_across_seeds():
    """20 key seeds, all 16 messages each."""
    failures = 0
    total = 0
    for key_seed in range(20):
        pk, sk = keygen(N, W, W_R, W_E, R, random.Random(key_seed))
        for msg_i in range(2**K):
            msg = [(msg_i >> b) & 1 for b in range(K)]
            ct = encrypt(pk, msg, random.Random(key_seed * 1000 + msg_i))
            recovered = decrypt(sk, pk, ct)
            total += 1
            if recovered != msg:
                failures += 1
    # At these parameters some decryption failures may occur.
    # Require <5% failure rate (empirical gate).
    failure_rate = failures / total
    assert failure_rate < 0.05, (
        f"Decryption failure rate {failure_rate:.2%} exceeds 5% "
        f"({failures}/{total})"
    )


def test_ciphertext_shape():
    pk, sk = keygen(N, W, W_R, W_E, R, random.Random(42))
    msg = [1, 0, 1, 0]
    u, v = encrypt(pk, msg, random.Random(100))
    assert len(u) == N
    assert len(v) == N


def test_encrypt_randomized():
    pk, sk = keygen(N, W, W_R, W_E, R, random.Random(42))
    msg = [1, 0, 1, 0]
    ct1 = encrypt(pk, msg, random.Random(1))
    ct2 = encrypt(pk, msg, random.Random(2))
    assert ct1 != ct2
