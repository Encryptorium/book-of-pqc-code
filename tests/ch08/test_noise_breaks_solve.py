"""Tests that Gaussian elimination fails on noisy LWE instances.

The whole point of Chapter 8's "noise makes it hard" section is that
the same algorithm which trivially solves b = A @ s (noise-free) fails
once we add a small error vector e. These tests run the elimination
on ``sample_lwe`` output and confirm it either returns None or, in
the rare coincidental case, returns a secret that differs from the
true s on at least one coordinate.
"""

import numpy as np

from lwe import (
    sample_secret,
    sample_lwe,
    gaussian_eliminate_mod_q,
)


def test_noisy_recovery_fails_on_toy_params(toy):
    # Over many seeds, confirm the recovered secret is never equal
    # to the true one. The <=2/100 threshold is an empirically
    # chosen upper bound; the actual rate is zero on 100 seeds of
    # the default_rng stream.
    failures = 0
    total = 100
    for seed in range(total):
        rng = np.random.default_rng(seed=seed)
        s = sample_secret(toy, rng)
        A, b = sample_lwe(toy, s, rng)
        recovered = gaussian_eliminate_mod_q(A, b, toy.q)
        if recovered is not None and np.array_equal(recovered, s):
            failures += 1
    assert failures <= 2, (
        f"gaussian_eliminate_mod_q returned the true secret on "
        f"{failures}/{total} noisy instances; expected almost all to fail"
    )


def test_noisy_system_usually_returns_none(toy):
    # Confirm the consistency check catches most noisy instances
    # when m > n. The >=90/100 threshold is an empirically chosen
    # lower bound on the none-count over the default_rng stream.
    none_count = 0
    total = 100
    for seed in range(total):
        rng = np.random.default_rng(seed=seed)
        s = sample_secret(toy, rng)
        A, b = sample_lwe(toy, s, rng)
        recovered = gaussian_eliminate_mod_q(A, b, toy.q)
        if recovered is None:
            none_count += 1
    assert none_count >= 90, (
        f"expected almost all noisy instances to return None, "
        f"got {none_count}/{total}"
    )


def test_noisy_square_system_returns_wrong_secret(square):
    # When m == n there are no consistency rows. The solver returns
    # a plausible-looking but wrong secret rather than signalling
    # failure. This test pins down that exact behaviour so the
    # chapter prose about the m == n caveat stays honest.
    wrong_count = 0
    none_count = 0
    correct_count = 0
    total = 50
    for seed in range(total):
        rng = np.random.default_rng(seed=seed)
        s = sample_secret(square, rng)
        A, b = sample_lwe(square, s, rng)
        recovered = gaussian_eliminate_mod_q(A, b, square.q)
        if recovered is None:
            none_count += 1
        elif np.array_equal(recovered, s):
            correct_count += 1
        else:
            wrong_count += 1
    # With m == n the noise-free consistency check never fires, so
    # None should be vanishingly rare (it would only arise from a
    # rank-deficient random A, which happens with probability
    # O(1/q) for each random seed).
    assert none_count <= 2, (
        f"expected almost no None returns for m == n, got {none_count}/{total}"
    )
    # The recovered secret should almost never equal the true one,
    # because the noise is projected through a nonzero elimination
    # path in every coordinate. The rare exception is when every
    # error entry happens to be zero, which has probability
    # (1/3)^n ~ 1.2% per seed.
    assert correct_count <= 3, (
        f"expected almost no accidental recoveries for m == n, "
        f"got {correct_count}/{total}"
    )
    assert wrong_count >= total - none_count - correct_count - 1
