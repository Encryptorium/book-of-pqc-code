"""Sampling routines for LWE instances over Z_q.

Four functions:

- sample_secret(params, rng) returns a uniform secret s in Z_q^n
- sample_error(params, rng) returns an error vector e in {-B, ..., B}^m
- sample_lwe(params, s, rng) returns (A, b) with b = A @ s + e mod q
- sample_uniform(params, rng) returns (A, u) with u uniform in Z_q^m

All outputs are numpy int64 arrays with entries in the canonical
representative range [0, q). The sampling functions take a
``numpy.random.Generator`` so tests can fix a seed.
"""

from __future__ import annotations

import numpy as np

from .params import LWEParams


def sample_secret(params: LWEParams, rng: np.random.Generator) -> np.ndarray:
    """Draw a uniform secret s in Z_q^n."""
    return rng.integers(low=0, high=params.q, size=params.n, dtype=np.int64)


def sample_error(params: LWEParams, rng: np.random.Generator) -> np.ndarray:
    """Draw an error vector e of length m with entries in {-B, ..., B}.

    The returned entries are reduced mod q into the canonical range
    [0, q), so the caller can add them to an element of Z_q^m without
    a follow-up reduction step.
    """
    B = params.noise_bound
    raw = rng.integers(low=-B, high=B + 1, size=params.m, dtype=np.int64)
    return raw % params.q


def sample_lwe(
    params: LWEParams,
    s: np.ndarray,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Draw a search LWE instance (A, b) with b = A @ s + e mod q.

    The matrix A in Z_q^{m x n} is uniform, the error e is drawn by
    ``sample_error``, and the returned b has entries in [0, q).
    """
    s = np.asarray(s, dtype=np.int64)
    assert s.shape == (params.n,), (
        f"sample_lwe: secret has shape {s.shape}, expected ({params.n},)"
    )
    A = rng.integers(
        low=0, high=params.q, size=(params.m, params.n), dtype=np.int64
    )
    e = sample_error(params, rng)
    b = (A @ s + e) % params.q
    return A, b


def sample_uniform(
    params: LWEParams,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Draw a uniform pair (A, u) with A in Z_q^{m x n} and u in Z_q^m.

    This is the "random" side of the decisional LWE distinguishing game:
    the adversary must tell apart ``sample_lwe`` output from
    ``sample_uniform`` output.
    """
    A = rng.integers(
        low=0, high=params.q, size=(params.m, params.n), dtype=np.int64
    )
    u = rng.integers(low=0, high=params.q, size=params.m, dtype=np.int64)
    return A, u
