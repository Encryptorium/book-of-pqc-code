"""Round-trip correctness tests for McEliece encrypt/decrypt."""

import random

from mceliece.mceliece import keygen, encrypt, decrypt

M = 4
IRRED = 0b10011
T = 2


def test_round_trip_single_message():
    """Encrypt and decrypt a single message."""
    pub, sec = keygen(M, T, IRRED, random.Random(42))
    msg = [1, 0, 1, 1, 0, 0, 1, 0]
    ct = encrypt(pub, msg, random.Random(99))
    recovered = decrypt(sec, ct)
    assert recovered == msg


def test_round_trip_zero_message():
    """The zero message encrypts and decrypts correctly."""
    pub, sec = keygen(M, T, IRRED, random.Random(42))
    msg = [0] * 8
    ct = encrypt(pub, msg, random.Random(99))
    recovered = decrypt(sec, ct)
    assert recovered == msg


def test_round_trip_all_messages():
    """All 256 possible 8-bit messages round-trip correctly."""
    pub, sec = keygen(M, T, IRRED, random.Random(42))
    for msg_int in range(256):
        msg = [(msg_int >> i) & 1 for i in range(8)]
        ct = encrypt(pub, msg, random.Random(msg_int))
        recovered = decrypt(sec, ct)
        assert recovered == msg, f"failed for message {msg_int}: {msg}"


def test_round_trip_across_seeds():
    """Round-trip across 20 key seeds with random messages."""
    for seed in range(20):
        rng = random.Random(seed)
        pub, sec = keygen(M, T, IRRED, rng)
        for trial in range(10):
            msg_rng = random.Random(seed * 100 + trial)
            msg = [msg_rng.randint(0, 1) for _ in range(pub["k"])]
            ct = encrypt(pub, msg, random.Random(seed * 1000 + trial))
            recovered = decrypt(sec, ct)
            assert recovered == msg, (
                f"failed for seed={seed}, trial={trial}: {msg}"
            )


def test_ciphertext_differs_from_codeword():
    """Ciphertext differs from m*G_pub by exactly t positions."""
    from mceliece.gf2 import vec_add, weight
    pub, sec = keygen(M, T, IRRED, random.Random(42))
    msg = [1, 1, 0, 0, 1, 0, 1, 1]
    enc_rng = random.Random(77)
    ct = encrypt(pub, msg, enc_rng)
    # compute m*G_pub
    G_pub = pub["G_pub"]
    n = pub["n"]
    mg = [0] * n
    for i, mi in enumerate(msg):
        if mi:
            mg = vec_add(mg, G_pub[i])
    diff = vec_add(ct, mg)
    assert weight(diff) == T
