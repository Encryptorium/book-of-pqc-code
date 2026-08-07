"""Polynomial serialization for ML-KEM (FIPS 203 §4.2.1).

FIPS 203 specifies bit-packed serialization of polynomials in $R_q$
(at $d = 12$) and of compressed polynomials (at $d \\in \\{1, 4, 5,
10, 11\\}$ for message, $d_v$, and $d_u$). Each coefficient occupies
$d$ bits, and a length-256 polynomial packs into exactly $32 d$
bytes. The encoding is little-endian within each $d$-bit field and
little-endian across fields.

The two-byte-level functions are:

- ``byte_encode_d(f, d)``: accept a length-256 int64 polynomial with
  coefficients in $[0, 2^d)$ (for $d < 12$) or $[0, q)$ (for $d = 12$)
  and return $32 d$ bytes. FIPS 203 Algorithm 5.
- ``byte_decode_d(B, d)``: accept $32 d$ bytes and return the
  length-256 polynomial they encode. FIPS 203 Algorithm 6. For
  $d = 12$, the returned coefficients are reduced modulo $q$ (the
  standard specifies ``mod q`` for $d = 12$ as a defensive measure).

Both functions operate on a single polynomial. K-PKE and ML-KEM wrap
these to encode and decode vectors in $R_q^k$ by concatenating $k$
per-polynomial byte strings.
"""

from __future__ import annotations

import numpy as np

from .ntt import Q, N


def byte_encode_d(f: np.ndarray, d: int) -> bytes:
    """FIPS 203 Algorithm 5. Pack a polynomial into $32 d$ bytes.

    For $d < 12$ the inputs must satisfy $0 \\leq f_i < 2^d$. For
    $d = 12$ the inputs must satisfy $0 \\leq f_i < q$. The bit-packed
    output is little-endian across coefficients and little-endian
    within each coefficient's $d$-bit field.
    """
    assert 1 <= d <= 12, f"byte_encode_d: d must be in [1, 12], got {d}"
    f = np.asarray(f, dtype=np.int64)
    assert f.shape == (N,), f"byte_encode_d: expected length-{N}"
    modulus = Q if d == 12 else (1 << d)
    for i in range(N):
        v = int(f[i])
        assert 0 <= v < modulus, (
            f"byte_encode_d: f[{i}] = {v} outside [0, {modulus})"
        )

    mask = (1 << d) - 1
    big = 0
    for i in range(N):
        big |= (int(f[i]) & mask) << (i * d)
    return big.to_bytes(32 * d, "little")


def byte_decode_d(B: bytes, d: int) -> np.ndarray:
    """FIPS 203 Algorithm 6. Unpack $32 d$ bytes into a polynomial.

    Returns a length-256 int64 array. For $d < 12$ the returned
    coefficients are in $[0, 2^d)$; for $d = 12$ they are reduced
    modulo $q$.
    """
    assert 1 <= d <= 12, f"byte_decode_d: d must be in [1, 12], got {d}"
    assert len(B) == 32 * d, (
        f"byte_decode_d: expected {32 * d} bytes, got {len(B)}"
    )
    mask = (1 << d) - 1
    big = int.from_bytes(B, "little")
    f = np.zeros(N, dtype=np.int64)
    for i in range(N):
        coeff = (big >> (i * d)) & mask
        if d == 12:
            coeff %= Q
        f[i] = coeff
    return f


def byte_encode_vector(fs: np.ndarray, d: int) -> bytes:
    """Encode a length-$k$ vector of polynomials as $32 d k$ bytes.

    Argument ``fs`` must have shape ``(k, N)`` with $k \\geq 1$. Each
    row is passed through ``byte_encode_d`` and the results are
    concatenated in row order.
    """
    fs = np.asarray(fs, dtype=np.int64)
    assert fs.ndim == 2 and fs.shape[1] == N, (
        f"byte_encode_vector: expected (k, {N}), got {fs.shape}"
    )
    return b"".join(byte_encode_d(fs[i], d) for i in range(fs.shape[0]))


def byte_decode_vector(B: bytes, d: int, k: int) -> np.ndarray:
    """Decode $32 d k$ bytes into a length-$k$ vector of polynomials."""
    assert len(B) == 32 * d * k, (
        f"byte_decode_vector: expected {32 * d * k} bytes, got {len(B)}"
    )
    chunk = 32 * d
    out = np.zeros((k, N), dtype=np.int64)
    for i in range(k):
        out[i] = byte_decode_d(B[i * chunk : (i + 1) * chunk], d)
    return out
