"""Compression and decompression for ML-KEM ciphertexts (FIPS 203 §4.2).

The compression map $\\text{Compress}_d(x)$ rounds $x \\in \\mathbb{Z}_q$
to the nearest integer multiple of $q / 2^d$ and returns that
multiple's index in $\\{0, 1, \\dots, 2^d - 1\\}$:

.. math::

    \\text{Compress}_d(x)
    = \\left\\lfloor \\frac{2^d \\cdot x}{q} \\right\\rceil \\bmod 2^d,

where $\\lfloor \\cdot \\rceil$ is round-half-up to the nearest integer.
The inverse $\\text{Decompress}_d(y)$ takes $y \\in \\mathbb{Z}_{2^d}$
and returns $\\lfloor q \\cdot y / 2^d \\rceil$, again rounding half up.
FIPS 203 (4.7) and (4.8) carry the width as the only subscript; the
Python functions below take it as a second argument instead.

Compression is lossy. The decompression noise is bounded by
$|\\text{Decompress}_d(\\text{Compress}_d(x)) - x| \\leq
\\lceil q / 2^{d+1} \\rceil$, which at $(q, d) = (3329, 10)$ gives a
bound of $2$ and at $(q, d) = (3329, 4)$ gives a bound of $105$. The
bound is attained at $d = 10$ and is one high at $d = 4$, where the
true maximum is $104$. These bounds feed directly into the K-PKE
noise budget.

Integer-arithmetic formulae, no floating point. For odd $q = 3329$
the round-half-up step is computed exactly via
$\\lfloor (2^d x + \\lfloor q/2 \\rfloor) / q \\rfloor$ because any
residue strictly above $(q-1)/2$ rounds up.
"""

from __future__ import annotations

import numpy as np

from .ntt import Q, N


def compress(x: np.ndarray, d: int) -> np.ndarray:
    """Apply $\\text{Compress}_q(\\cdot, d)$ coefficient-wise.

    Accepts a numpy array with integer entries in $[0, q)$ and returns
    an int64 numpy array of the same shape with entries in
    $[0, 2^d)$. Raises if $d \\leq 0$ or $d \\geq 12$.
    """
    assert 1 <= d <= 11, f"compress: d must be in [1, 11], got {d}"
    x = np.asarray(x, dtype=np.int64) % Q
    two_d = 1 << d
    # Round-half-up: ((x * 2^d) + q // 2) // q, mod 2^d.
    numerator = (x * two_d) + (Q // 2)
    return (numerator // Q) % two_d


def decompress(y: np.ndarray, d: int) -> np.ndarray:
    """Apply $\\text{Decompress}_q(\\cdot, d)$ coefficient-wise.

    Accepts a numpy array with integer entries in $[0, 2^d)$ and
    returns an int64 numpy array of the same shape with entries in
    $[0, q)$.
    """
    assert 1 <= d <= 11, f"decompress: d must be in [1, 11], got {d}"
    y = np.asarray(y, dtype=np.int64)
    two_d = 1 << d
    # Round-half-up: ((q * y) + 2^{d-1}) // 2^d.
    numerator = (Q * y) + (two_d >> 1)
    return numerator // two_d


def compression_noise_bound(d: int) -> int:
    """Return the decompression noise bound $\\lceil q / 2^{d+1} \\rceil$.

    This is the maximum absolute value (in symmetric representatives)
    of $\\text{Decompress}_q(\\text{Compress}_q(x, d), d) - x$ across
    all $x \\in \\mathbb{Z}_q$. The K-PKE noise budget has to cover
    this on top of the Module-LWE error.
    """
    assert 1 <= d <= 11, f"compression_noise_bound: d must be in [1, 11]"
    two_d_plus_1 = 1 << (d + 1)
    return (Q + two_d_plus_1 - 1) // two_d_plus_1  # ceiling division


def message_to_poly(message: bytes) -> np.ndarray:
    """Encode a 32-byte message as a polynomial with coefficients in
    $\\{0, \\lceil q/2 \\rceil\\}$.

    FIPS 203 uses ``Decompress_q(ByteDecode_1(m), 1)`` to lift a
    256-bit message into $R_q$, which is the same operation: each
    message bit $b$ becomes the coefficient
    $\\text{Decompress}_q(b, 1) = \\lfloor (q + 1) / 2 \\rfloor \\cdot b
    = 1665 \\cdot b$ at $q = 3329$.
    """
    assert len(message) == 32, (
        f"message_to_poly: message must be 32 bytes, got {len(message)}"
    )
    f = np.zeros(N, dtype=np.int64)
    for i in range(N):
        bit = (message[i >> 3] >> (i & 7)) & 1
        f[i] = ((Q + 1) // 2) * bit  # 1665 when q = 3329
    return f


def poly_to_message(f: np.ndarray) -> bytes:
    """Decode a polynomial back to a 32-byte message.

    Applies $\\text{Compress}_q(\\cdot, 1)$ coefficient-wise, then packs
    the 256 resulting bits little-endian into 32 bytes. This is the
    inverse of ``message_to_poly`` when the noise stays inside the
    decoding region around $0$ and $\\lfloor q/2 \\rfloor$.
    """
    f = np.asarray(f, dtype=np.int64) % Q
    assert f.shape == (N,), f"poly_to_message: expected length-{N}"
    bits = compress(f, 1)
    out = bytearray(32)
    for i in range(N):
        if int(bits[i]) & 1:
            out[i >> 3] |= 1 << (i & 7)
    return bytes(out)
