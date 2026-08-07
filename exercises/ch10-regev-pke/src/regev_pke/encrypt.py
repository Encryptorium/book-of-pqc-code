"""Regev encryption.

encrypt draws a random vector r in {0, 1}^m, computes c1 = A^T r mod q
and c2 = b^T r + floor(q/2) * bit mod q, and returns the ciphertext
(c1, c2). The secret cancels from the decryption side: computing
c2 - c1^T s recovers floor(q/2) * bit + e^T r, and the message
survives rounding for both bits whenever 2 |e^T r| < q // 2.
"""

from __future__ import annotations

import numpy as np

from .params import RegevParams


def encrypt(
    params: RegevParams,
    public_key: tuple[np.ndarray, np.ndarray],
    bit: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Encrypt a single bit under the public key (A, b).

    Returns the ciphertext (c1, c2) with c1 in Z_q^n and c2 in Z_q.
    The randomness r is drawn uniformly from {0, 1}^m.
    """
    assert bit in (0, 1), f"encrypt: bit must be 0 or 1, got {bit}"
    A, b = public_key
    q, m, n = params.q, params.m, params.n
    assert A.shape == (m, n), (
        f"encrypt: A has shape {A.shape}, expected ({m}, {n})"
    )
    assert b.shape == (m,), (
        f"encrypt: b has shape {b.shape}, expected ({m},)"
    )
    r = rng.integers(low=0, high=2, size=m, dtype=np.int64)
    half_q = q // 2
    c1 = (A.T @ r) % q
    c2 = np.int64((int(b @ r) + half_q * bit) % q)
    return c1, c2
