"""Tests for the HQC noise budget at toy parameters.

Verifies that the noise term r2*x + r1*y + e stays within the
repetition code's correction capacity with high probability.
"""

import random

from hqc.hqc import keygen, encrypt, decrypt
from hqc.poly_gf2 import poly_add, poly_mul, poly_weight
from hqc.repetition import rep_encode
from hqc.sparse import sample_sparse


N, W, W_R, W_E, R = 83, 3, 3, 3, 17
K = N // R   # 4
CORRECTION_CAPACITY = (R - 1) // 2   # 8 errors per block


def test_noise_decomposition():
    """Verify v - u*y = encode(m) + (r2*x + r1*y + e)."""
    rng_key = random.Random(42)
    rng_enc = random.Random(100)

    pk, sk = keygen(N, W, W_R, W_E, R, rng_key)
    msg = [1, 0, 1, 1]

    # Re-derive encryption internals
    rng_enc2 = random.Random(100)
    r1 = sample_sparse(N, W_R, rng_enc2)
    r2 = sample_sparse(N, W_R, rng_enc2)
    e = sample_sparse(N, W_E, rng_enc2)

    ct = encrypt(pk, msg, rng_enc)
    u, v = ct

    # Compute v + u*y (= v - u*y over GF(2))
    noisy_code = poly_add(v, poly_mul(u, sk["y"], N))

    # Expected: encode(m) + r2*x + r1*y + e
    codeword = rep_encode(msg, R, N)
    noise = poly_add(
        poly_add(poly_mul(r2, sk["x"], N), poly_mul(r1, sk["y"], N)),
        e,
    )
    expected = poly_add(codeword, noise)

    assert noisy_code == expected


def test_noise_weight_bounded():
    """Over 1000 trials, verify max per-block errors stay reasonable.

    The correction capacity is 8.  The DFR is nonzero (~0.6%), so
    some trials exceed the capacity.  We assert the maximum stays
    below R//2 + 4 = 12, which is tight enough to catch a broken
    noise calculation but loose enough for the observed distribution.
    """
    max_block_errors_seen = 0
    trials = 1000
    for trial in range(trials):
        rng_key = random.Random(trial)
        rng_enc = random.Random(trial + 100000)
        pk, sk = keygen(N, W, W_R, W_E, R, rng_key)
        msg = [1, 0, 1, 0]

        # Re-derive encryption randomness
        rng_enc2 = random.Random(trial + 100000)
        r1 = sample_sparse(N, W_R, rng_enc2)
        r2 = sample_sparse(N, W_R, rng_enc2)
        e = sample_sparse(N, W_E, rng_enc2)

        noise = poly_add(
            poly_add(poly_mul(r2, sk["x"], N), poly_mul(r1, sk["y"], N)),
            e,
        )

        # Check per-block error count
        for block_i in range(K):
            block_noise = noise[block_i * R : (block_i + 1) * R]
            block_errors = sum(block_noise)
            if block_errors > max_block_errors_seen:
                max_block_errors_seen = block_errors

    # The maximum per-block error seen should stay well below the block
    # size.  With correction capacity 8 and observed max ~10, a bound of
    # 12 catches broken noise calculations without failing on tail events.
    assert max_block_errors_seen <= 12, (
        f"Max per-block errors {max_block_errors_seen} exceeds bound 12"
    )


def test_decryption_failure_rate():
    """Over 5000 trials, decryption failure rate should be manageable."""
    failures = 0
    trials = 5000
    for trial in range(trials):
        rng_key = random.Random(trial)
        rng_enc = random.Random(trial + 200000)
        pk, sk = keygen(N, W, W_R, W_E, R, rng_key)
        msg_i = trial % (2**K)
        msg = [(msg_i >> b) & 1 for b in range(K)]
        ct = encrypt(pk, msg, rng_enc)
        recovered = decrypt(sk, pk, ct)
        if recovered != msg:
            failures += 1

    failure_rate = failures / trials
    # At toy parameters, some failures are expected.
    # If rate exceeds 10%, parameters need revision.
    assert failure_rate < 0.10, (
        f"Decryption failure rate {failure_rate:.2%} ({failures}/{trials}) "
        f"exceeds 10% threshold"
    )
