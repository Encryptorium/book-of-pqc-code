"""Regev public-key generation.

keygen samples a uniform secret s in Z_q^n, a uniform matrix A in
Z_q^{m x n}, and a signed error vector e in {-B, ..., B}^m, then
returns the public key (A, b = A s + e mod q) and the secret key s.

Samplers are re-implemented locally with numpy rather than imported
from the Chapter 8 learning-with-errors package. Chapter 10's package
is buildable standalone, matching the pattern set by Chapters 8 and 9.
The sampler shapes are identical to Chapter 8's, so a reader who walks
both packages sees the same interface twice.
"""

from __future__ import annotations

import numpy as np

from .params import RegevParams


def keygen(
    params: RegevParams,
    rng: np.random.Generator,
) -> tuple[tuple[np.ndarray, np.ndarray], np.ndarray]:
    """Return ((A, b), s) with b = A @ s + e mod q.

    The secret s is uniform in Z_q^n, the matrix A is uniform in
    Z_q^{m x n}, and the error e is uniform in the signed range
    {-B, ..., B}^m. The public vector b is reduced mod q into
    canonical representatives [0, q), but the intermediate error e
    keeps its signed representation so that the variable name matches
    the chapter's prose. All outputs are numpy int64 arrays.
    """
    n, q, m, B = params.n, params.q, params.m, params.noise_bound
    s = rng.integers(low=0, high=q, size=n, dtype=np.int64)
    A = rng.integers(low=0, high=q, size=(m, n), dtype=np.int64)
    e = rng.integers(low=-B, high=B + 1, size=m, dtype=np.int64)
    b = (A @ s + e) % q
    return (A, b), s
