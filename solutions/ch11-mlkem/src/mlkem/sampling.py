"""Sampling primitives for ML-KEM (FIPS 203 §4.2).

Two samplers, plus the helpers that wrap ``PRF`` and ``XOF`` into
polynomial-producing calls:

- ``cbd_eta``: FIPS 203 Algorithm 8, the centered binomial
  distribution $\\text{CBD}_\\eta$. Takes a byte string of length
  $64 \\eta$ and returns a polynomial in $R_q$ whose 256 coefficients
  are independent samples from the distribution $\\text{CBD}_\\eta$
  with support $\\{-\\eta, \\dots, \\eta\\}$, variance $\\eta / 2$,
  zero mean.
- ``sample_ntt``: FIPS 203 Algorithm 7, the rejection sampler that
  takes an XOF byte stream and produces a length-256 polynomial in
  the NTT domain with coefficients uniformly distributed in $Z_q$.

Plus the higher-level helpers used by K-PKE.KeyGen and K-PKE.Encrypt:

- ``sample_poly_cbd``: draws a single polynomial from $\\text{CBD}_\\eta$
  using ``PRF(eta, seed, nonce)``.
- ``sample_matrix_ntt``: draws the $k \\times k$ matrix $\\hat{A}$ in
  the NTT domain from a 32-byte seed by calling
  ``sample_ntt(rho + bytes([j, i]))`` for each $(i, j)$ entry. The
  byte order ``j`` first then ``i`` matches FIPS 203 §5.1 Algorithm 13
  literally.
"""

from __future__ import annotations

import hashlib

import numpy as np

from .hashes import PRF
from .ntt import Q, N


def _bytes_to_bits(b: bytes) -> list[int]:
    """Return a list of 8 * len(b) bits (LSB first within each byte).

    FIPS 203 Algorithm 3. Used as a helper inside cbd_eta; the
    direct-int path in cbd_eta does the same work without materializing
    the list.
    """
    bits = []
    for byte in b:
        for j in range(8):
            bits.append((byte >> j) & 1)
    return bits


def cbd_eta(byte_string: bytes, eta: int) -> np.ndarray:
    """Centered binomial distribution sampler $\\text{CBD}_\\eta$.

    FIPS 203 Algorithm 8. Given a byte string of length $64 \\eta$,
    return a length-256 int64 array ``f`` where

    .. math::

        f_i = \\sum_{j=0}^{\\eta-1} b_{2 i \\eta + j}
              - \\sum_{j=0}^{\\eta-1} b_{2 i \\eta + \\eta + j}

    and $b_0, b_1, \\dots$ is the bit sequence obtained by ``BytesToBits``
    applied to the input. Each coefficient lives in
    $\\{-\\eta, \\dots, \\eta\\}$; the returned array reduces the
    value modulo $q$ so negative samples are represented in the
    canonical range $[0, q)$.
    """
    assert eta in (2, 3), f"cbd_eta: eta must be 2 or 3, got {eta}"
    assert len(byte_string) == 64 * eta, (
        f"cbd_eta: byte_string length must be {64 * eta}, "
        f"got {len(byte_string)}"
    )
    bits = _bytes_to_bits(byte_string)
    assert len(bits) == 512 * eta
    f = np.zeros(N, dtype=np.int64)
    for i in range(N):
        x = sum(bits[2 * i * eta + j] for j in range(eta))
        y = sum(bits[2 * i * eta + eta + j] for j in range(eta))
        f[i] = (x - y) % Q
    return f


def sample_poly_cbd(eta: int, seed: bytes, nonce: int) -> np.ndarray:
    """Draw a single polynomial from $\\text{CBD}_\\eta$ using ``PRF``.

    Thin wrapper: expand ``PRF(eta, seed, nonce)`` to $64 \\eta$ bytes
    and hand them to ``cbd_eta``. This is the form used inside
    ``K_PKE.KeyGen`` and ``K_PKE.Encrypt``.
    """
    prf_bytes = PRF(eta, seed, nonce)
    return cbd_eta(prf_bytes, eta)


def sample_ntt(shake_input: bytes) -> np.ndarray:
    """Rejection sampler for a uniform NTT-domain polynomial.

    FIPS 203 Algorithm 7. Absorbs ``shake_input`` into a SHAKE-128
    instance and squeezes bytes in groups of three, interpreting each
    group as two 12-bit candidates. Each candidate is accepted if it
    is strictly less than $q = 3329$ and rejected otherwise. Stops
    when 256 coefficients have been collected.

    Implementation note: ``hashlib.shake_128.digest(N)`` returns the
    first $N$ bytes of a deterministic stream, so repeatedly calling
    ``.digest(N)`` with increasing $N$ is equivalent to squeezing more
    output. The initial squeeze is 840 bytes (enough for 560 12-bit
    candidates, which is comfortable overkill for the 256 needed at
    rejection rate $3328/4096 \\approx 0.813$).
    """
    shake = hashlib.shake_128()
    shake.update(shake_input)

    out = np.zeros(N, dtype=np.int64)
    j = 0
    bytes_requested = 168 * 5  # 840 bytes = five SHAKE-128 blocks
    raw = shake.digest(bytes_requested)
    idx = 0
    while j < N:
        if idx + 3 > len(raw):
            bytes_requested += 168
            raw = shake.digest(bytes_requested)
        b0 = raw[idx]
        b1 = raw[idx + 1]
        b2 = raw[idx + 2]
        idx += 3
        d1 = b0 | ((b1 & 0x0F) << 8)
        d2 = (b1 >> 4) | (b2 << 4)
        if d1 < Q:
            out[j] = d1
            j += 1
        if j < N and d2 < Q:
            out[j] = d2
            j += 1
    return out


def sample_matrix_ntt(rho: bytes, k: int, transpose: bool) -> np.ndarray:
    """Expand the $k \\times k$ matrix $\\hat{A}$ in the NTT domain.

    FIPS 203 §5.1 (``K-PKE.KeyGen``) builds $\\hat{A}[i][j]$ from the
    XOF input ``rho || j || i`` via ``sample_ntt``, with the byte
    order ``j`` first then ``i``. Passing ``transpose=True`` swaps the
    two bytes, which is how ``K-PKE.Encrypt`` computes $\\hat{A}^\\top$
    (FIPS 203 §5.2). Returns a $(k, k, 256)$ int64 array, entry
    ``(i, j)`` being the NTT-domain polynomial $\\hat{A}[i][j]$.
    """
    assert len(rho) == 32, f"sample_matrix_ntt: rho must be 32 bytes"
    assert 2 <= k <= 4, f"sample_matrix_ntt: k must be in [2, 4]"
    a_hat = np.zeros((k, k, N), dtype=np.int64)
    for i in range(k):
        for j in range(k):
            if transpose:
                # K-PKE.Encrypt expands A-hat-transpose with the same
                # seed. FIPS 203 specifies A-hat[i][j] = SampleNTT(
                # rho || j || i); transpose is equivalent to reading
                # A-hat[j][i] out of A-hat, which is SampleNTT(
                # rho || i || j).
                shake_input = rho + bytes([i, j])
            else:
                shake_input = rho + bytes([j, i])
            a_hat[i, j] = sample_ntt(shake_input)
    return a_hat
