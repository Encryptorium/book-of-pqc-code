"""Sampling routines for Ring-LWE and Module-LWE instances over R_q.

Five public functions:

- sample_ring_secret(params, rng): uniform secret s in R_q
- sample_ring_error(params, rng): small error e in R_q with
  coefficients drawn uniformly from {-B, ..., B} and reduced mod q
- sample_ring_uniform(params, rng): uniform polynomial u in R_q
  (used by the decisional game's "random" side)
- sample_ring_lwe(params, rng): a Ring-LWE sample (a, s, e, b) with
  b = a * s + e in R_q
- sample_module_lwe(params, rng): a Module-LWE sample (A, s, e, b)
  with b = A s + e over R_q^k, shapes (m, k, n), (k, n), (m, n),
  (m, n)

All polynomial coordinates are returned as numpy int64 arrays in
the canonical range [0, q). The sampling functions take a
``numpy.random.Generator`` so tests can fix a seed.

For symmetry with Chapter 8's ``sample_lwe``, ``sample_ring_lwe``
returns the full tuple (a, s, e, b) rather than just (a, b), so
tests can check the defining identity b = a * s + e directly
without re-drawing the secret and the error.
"""

from __future__ import annotations

import numpy as np

from .params import RingParams, ModuleParams
from .ring import ring_mul_naive


def sample_ring_secret(
    params: RingParams, rng: np.random.Generator
) -> np.ndarray:
    """Draw a uniform secret s in R_q.

    The secret is a length-n polynomial with every coefficient
    uniformly random in Z_q. This matches the Ring-LWE statement
    where the secret distribution is uniform over R_q.
    """
    return rng.integers(low=0, high=params.q, size=params.n, dtype=np.int64)


def sample_ring_error(
    params: RingParams, rng: np.random.Generator
) -> np.ndarray:
    """Draw an error polynomial e in R_q with small coefficients.

    Every coefficient of e is drawn uniformly from the integer
    interval {-B, ..., B} for B = params.noise_bound and reduced
    modulo q into the canonical range [0, q). Uniform-on-an-interval
    noise is a toy stand-in. The LPR worst-case reduction is stated
    for Gaussian error in the canonical embedding and ML-KEM
    specifies a centered binomial, so the three are not
    interchangeable inside a hardness proof: the proof assumptions
    and the concrete security estimates track separately.
    """
    B = params.noise_bound
    raw = rng.integers(low=-B, high=B + 1, size=params.n, dtype=np.int64)
    return raw % params.q


def sample_ring_uniform(
    params: RingParams, rng: np.random.Generator
) -> np.ndarray:
    """Draw a uniform polynomial u in R_q.

    This is the "random" side of the decisional Ring-LWE game:
    instead of b = a * s + e, the distinguisher receives a
    uniformly random u independent of a. u has the same shape as
    the b output of ``sample_ring_lwe``.
    """
    return rng.integers(low=0, high=params.q, size=params.n, dtype=np.int64)


def sample_ring_lwe(
    params: RingParams, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Draw a Ring-LWE sample (a, s, e, b) with b = a * s + e in R_q.

    Returns four length-n int64 arrays. The secret s and the error
    e are returned alongside a and b so that tests and pedagogical
    walkthroughs can verify the defining identity. The three inputs
    are drawn via the single-purpose helpers sample_ring_uniform,
    sample_ring_secret, and sample_ring_error, so changing any one
    of them automatically flows through to this function.
    """
    a = sample_ring_uniform(params, rng)
    s = sample_ring_secret(params, rng)
    e = sample_ring_error(params, rng)
    b = (ring_mul_naive(a, s, params.q) + e) % params.q
    return a, s, e, b


def sample_module_lwe(
    params: ModuleParams, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Draw a Module-LWE sample (A, s, e, b) over R_q^k.

    Shapes:

    - A: (m, k, n)  -- an m-by-k matrix of ring elements
    - s: (k, n)     -- a rank-k secret vector
    - e: (m, n)     -- an error vector of m ring elements
    - b: (m, n)     -- b[i] = sum_j A[i, j] * s[j] + e[i] in R_q

    At k = 1 this reduces to a stack of m Ring-LWE samples that
    share the same secret s. Seeded identically to
    ``sample_ring_lwe`` (same rng, same params.n, params.q,
    params.noise_bound, params.m = 1), the k = 1 output of this
    function agrees sample-for-sample with ``sample_ring_lwe``.
    """
    n, q, k, m = params.n, params.q, params.k, params.m
    B = params.noise_bound
    A = rng.integers(low=0, high=q, size=(m, k, n), dtype=np.int64)
    s = rng.integers(low=0, high=q, size=(k, n), dtype=np.int64)
    raw_e = rng.integers(low=-B, high=B + 1, size=(m, n), dtype=np.int64)
    e = raw_e % q

    b = np.zeros((m, n), dtype=np.int64)
    for i in range(m):
        row = np.zeros(n, dtype=np.int64)
        for j in range(k):
            row = (row + ring_mul_naive(A[i, j], s[j], q)) % q
        b[i] = (row + e[i]) % q
    return A, s, e, b
