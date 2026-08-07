"""Tests for the noise budget 2 * m * B < q // 2.

Two parameter sets: one where the budget holds comfortably and every
honest seed decodes correctly, one where the budget is violated and a
measurable fraction of honest seeds decodes incorrectly. The second
case demonstrates that the budget is tight: when it is violated,
decryption actually fails, not just in theory.
"""

import numpy as np

from regev_pke import RegevParams, keygen, encrypt, decrypt


def test_feasible_params_report_positive_headroom(feasible):
    assert feasible.is_noise_budget_feasible() is True
    assert feasible.noise_budget_headroom() > 0


def test_infeasible_params_report_negative_headroom(infeasible):
    assert infeasible.is_noise_budget_feasible() is False
    assert infeasible.noise_budget_headroom() < 0


def _failure_rate(params: RegevParams, num_seeds: int) -> float:
    failures = 0
    for seed in range(num_seeds):
        rng = np.random.default_rng(seed=seed)
        pk, sk = keygen(params, rng)
        for bit in (0, 1):
            # Fresh randomness for each encryption, still driven by the
            # same seed so failures are reproducible.
            ct = encrypt(params, pk, bit, rng)
            if decrypt(params, sk, ct) != bit:
                failures += 1
    return failures / (2 * num_seeds)


def test_feasible_params_have_zero_failure_rate(feasible):
    rate = _failure_rate(feasible, num_seeds=200)
    assert rate == 0.0, (
        f"feasible params should decode every seed correctly, "
        f"got failure rate {rate}"
    )


def test_infeasible_params_have_nonzero_failure_rate(infeasible):
    rate = _failure_rate(infeasible, num_seeds=200)
    # The empirical rate for (q=13, m=8, B=1) is well above 5 percent.
    # The exact value depends on the seeded RNG, but demanding at least
    # 5 percent is a conservative lower bound that reliably fires.
    assert rate > 0.05, (
        f"infeasible params should fail on a measurable fraction of "
        f"seeds, got failure rate {rate}"
    )


def test_budget_is_tight_at_the_boundary_the_asymptotic_form_gets_wrong():
    """2 m B < q // 2 is exact where |e^T r| < q / 4 is one step too generous.

    At q = 97, m B = 24 satisfies the asymptotic form (24 < 24.25) and
    violates the exact one (48 is not < 48). The worst-case pair is
    reachable: every r_i = 1 and every e_i = -B gives e^T r = -24, which
    under the bit 1 decrypts to 24 and decodes as 0. Random seeds never
    find this pair, which is why only a constructed case pins it.
    """
    params = RegevParams(n=4, q=97, m=24, noise_bound=1)
    assert params.is_noise_budget_feasible() is False
    assert params.noise_budget_headroom() == 0.0

    q, n, m = params.q, params.n, params.m
    rng = np.random.default_rng(seed=0)
    s = rng.integers(0, q, size=n, dtype=np.int64)
    A = rng.integers(0, q, size=(m, n), dtype=np.int64)
    e = np.full(m, -params.noise_bound, dtype=np.int64)
    r = np.ones(m, dtype=np.int64)
    b = (A @ s + e) % q

    c1 = (A.T @ r) % q
    c2 = np.int64((int(b @ r) + (q // 2) * 1) % q)
    assert decrypt(params, s, (c1, c2)) == 0, (
        "the worst-case pair should decode the bit 1 as 0; if it now "
        "decodes correctly the decoder changed, not the budget"
    )
