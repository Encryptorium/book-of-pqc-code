"""Round-trip tests for Regev encrypt and decrypt."""

import numpy as np

from regev_pke import keygen, encrypt, decrypt


def test_encrypt_shapes(toy):
    rng = np.random.default_rng(seed=0)
    pk, _ = keygen(toy, rng)
    c1, c2 = encrypt(toy, pk, 0, rng)
    assert c1.shape == (toy.n,)
    assert c1.dtype == np.int64
    assert np.all(c1 >= 0) and np.all(c1 < toy.q)
    assert 0 <= int(c2) < toy.q


def test_round_trip_zero_bit_across_seeds(toy):
    for seed in range(100):
        rng = np.random.default_rng(seed=seed)
        pk, sk = keygen(toy, rng)
        ct = encrypt(toy, pk, 0, rng)
        recovered = decrypt(toy, sk, ct)
        assert recovered == 0, f"zero-bit decryption failed at seed {seed}"


def test_round_trip_one_bit_across_seeds(toy):
    for seed in range(100):
        rng = np.random.default_rng(seed=seed)
        pk, sk = keygen(toy, rng)
        ct = encrypt(toy, pk, 1, rng)
        recovered = decrypt(toy, sk, ct)
        assert recovered == 1, f"one-bit decryption failed at seed {seed}"


def test_both_bits_with_shared_public_key(toy):
    # Generate one keypair and verify both bits decrypt correctly
    # with distinct encryption randomness.
    rng = np.random.default_rng(seed=7)
    pk, sk = keygen(toy, rng)
    ct0 = encrypt(toy, pk, 0, rng)
    ct1 = encrypt(toy, pk, 1, rng)
    assert decrypt(toy, sk, ct0) == 0
    assert decrypt(toy, sk, ct1) == 1
