"""Regev decryption.

decrypt recovers a message bit from a Regev ciphertext (c1, c2) under
the secret key s. The decryption rule computes v = (c2 - c1^T s) mod q
and rounds v to the nearer of 0 or floor(q/2) using the integer
expression ((2 v + floor(q/2)) // q) mod 2. The rounding is exact:
it maps v in the decoding region around 0 to the bit 0, and v in the
decoding region around floor(q/2) to the bit 1.

Correctness condition: the decryption is correct for both message
bits whenever 2 |e^T r| < q // 2 in symmetric representatives, which
is guaranteed by the noise budget 2 m B < q // 2. The asymptotic form
of the same condition is |e^T r| < q / 4.
"""

from __future__ import annotations

import numpy as np

from .params import RegevParams


def decrypt(
    params: RegevParams,
    secret_key: np.ndarray,
    ciphertext: tuple[np.ndarray, np.ndarray],
) -> int:
    """Decrypt a Regev ciphertext to a single bit.

    Returns 0 if v = (c2 - c1^T s) mod q is nearer to 0 than to
    q // 2 on the cycle Z_q, and 1 otherwise. The integer rounding
    expression ((2 v + q // 2) // q) mod 2 gives that answer without
    floating-point arithmetic, breaking the midpoint tie toward the
    bit 0.
    """
    s = secret_key
    c1, c2 = ciphertext
    q, n = params.q, params.n
    assert s.shape == (n,), (
        f"decrypt: secret has shape {s.shape}, expected ({n},)"
    )
    assert c1.shape == (n,), (
        f"decrypt: c1 has shape {c1.shape}, expected ({n},)"
    )
    v = int((int(c2) - int(c1 @ s)) % q)
    half_q = q // 2
    return ((2 * v + half_q) // q) % 2
