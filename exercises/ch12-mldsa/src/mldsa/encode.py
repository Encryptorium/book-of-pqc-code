"""Serialization for ML-DSA (FIPS 204 §7.1-7.2, Algorithms 16-28).

Everything ML-DSA puts on the wire is a little-endian bit-packing of length-256
polynomials at a field-specific width. Two primitives do the work:

* ``SimpleBitPack(w, b)`` packs unsigned coefficients in [0, b] using bitlen(b)
  bits each.
* ``BitPack(w, a, b)`` packs signed coefficients in [-a, b] by storing the
  unsigned value ``b - w_i`` in bitlen(a+b) bits.

Both follow FIPS 202's little-endian bit order, which is exactly what you get by
laying coefficient i into bit positions ``[i*width, (i+1)*width)`` of one big
integer and emitting it with ``int.to_bytes(..., "little")`` (the same idiom as
``ch11-mlkem/serialize.py``).

The hint has its own sparse format: HintBitPack lists the set positions poly by
poly followed by k cumulative end markers. HintBitUnpack is the one decoder that
can *reject*: it returns None (FIPS 204's bottom symbol) when the positions are
not strictly increasing, an end marker is out of range, or an unused slot is
nonzero. That rejection is what makes a tampered-hint signature fail verification.
"""

from __future__ import annotations

import numpy as np

from .params import ML_DSA_Q as Q, ML_DSA_D as D, MLDSAParams, bitlen


# --- Coefficient-level packers. ---

def simple_bit_pack(w: np.ndarray, b: int) -> bytes:
    """FIPS 204 Algorithm 16. Pack 256 unsigned coefficients in [0, b]."""
    # EXERCISE: implement this function.
    #
    # Pack 256 unsigned coefficients in [0, b] at bitlen(b) bits each. Lay
    # coefficient i into bit positions [i*width, (i+1)*width) of one big
    # integer and emit it with int.to_bytes(32*width, 'little').
    #
    # Reference: Chapter 12, 'Serialization: SimpleBitPack and BitPack' (FIPS 204 Algorithm 16)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_encode.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: simple_bit_pack")


def simple_bit_unpack(v: bytes, b: int) -> np.ndarray:
    """FIPS 204 Algorithm 18. Inverse of ``simple_bit_pack``."""
    # EXERCISE: implement this function.
    #
    # Invert simple_bit_pack: read the byte string into one big integer with
    # int.from_bytes(..., 'little'), then mask out each width-bit field to
    # recover the 256 coefficients.
    #
    # Reference: Chapter 12, 'Serialization: SimpleBitPack and BitPack' (FIPS 204 Algorithm 18)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_encode.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: simple_bit_unpack")


def bit_pack(w: np.ndarray, a: int, b: int) -> bytes:
    """FIPS 204 Algorithm 17. Pack 256 signed coefficients in [-a, b]."""
    w = np.asarray(w, dtype=np.int64)
    assert w.shape == (256,), f"bit_pack: expected length-256, got {w.shape}"
    width = bitlen(a + b)
    mask = (1 << width) - 1
    big = 0
    for i in range(256):
        c = int(w[i])
        assert -a <= c <= b, f"bit_pack: coeff {c} outside [-{a}, {b}]"
        big |= ((b - c) & mask) << (i * width)
    return big.to_bytes(32 * width, "little")


def bit_unpack(v: bytes, a: int, b: int) -> np.ndarray:
    """FIPS 204 Algorithm 19. Inverse of ``bit_pack`` (returns b - stored)."""
    width = bitlen(a + b)
    assert len(v) == 32 * width, f"bit_unpack: expected {32 * width} bytes, got {len(v)}"
    big = int.from_bytes(v, "little")
    mask = (1 << width) - 1
    out = np.empty(256, dtype=np.int64)
    for i in range(256):
        out[i] = b - ((big >> (i * width)) & mask)
    return out


# --- Hint (sparse) format. ---

def hint_bit_pack(params: MLDSAParams, h: np.ndarray) -> bytes:
    """FIPS 204 Algorithm 20. Serialize the k-by-256 hint into omega + k bytes."""
    # EXERCISE: implement this function.
    #
    # Serialize the k-by-256 hint into omega + k bytes. Walk each polynomial
    # i, writing the index j of every set position into the next free slot,
    # then write the running total into byte omega + i as the cumulative end
    # marker for that polynomial.
    #
    # Reference: Chapter 12, 'Serialization: SimpleBitPack and BitPack' (FIPS 204 Algorithm 20)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_encode.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: hint_bit_pack")


def hint_bit_unpack(params: MLDSAParams, y: bytes) -> np.ndarray | None:
    """FIPS 204 Algorithm 21. Deserialize a hint, or return None (bottom) if
    the encoding is malformed."""
    # EXERCISE: implement this function.
    #
    # Invert hint_bit_pack, returning None (FIPS 204's bottom) on a
    # malformed encoding. For each polynomial read its end marker; reject if
    # it is below the running index or above omega. Set the listed
    # positions, rejecting if they are not strictly increasing, and finally
    # reject if any unused slot up to omega is nonzero.
    #
    # Reference: Chapter 12, 'Serialization: SimpleBitPack and BitPack' (FIPS 204 Algorithm 21)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_encode.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: hint_bit_unpack")


# --- Object encoders (parameterized by the set). ---

def pk_encode(params: MLDSAParams, rho: bytes, t1: np.ndarray) -> bytes:
    """FIPS 204 Algorithm 22. pk = rho || SimpleBitPack(t1[i]) for i in [0, k)."""
    # EXERCISE: implement this function.
    #
    # pk = rho (32 bytes) followed by SimpleBitPack of each of the k rows of
    # t1 at top = 2^t1_bits() - 1.
    #
    # Reference: Chapter 12, 'Serialization: SimpleBitPack and BitPack' (FIPS 204 Algorithm 22)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_encode.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: pk_encode")


def pk_decode(params: MLDSAParams, pk: bytes) -> tuple[bytes, np.ndarray]:
    """FIPS 204 Algorithm 23. Inverse of ``pk_encode``."""
    # EXERCISE: implement this function.
    #
    # Invert pk_encode: take rho from the first 32 bytes, then
    # SimpleBitUnpack each of the k fixed-width slices back into t1.
    #
    # Reference: Chapter 12, 'Serialization: SimpleBitPack and BitPack' (FIPS 204 Algorithm 23)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_encode.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: pk_decode")


def sk_encode(
    params: MLDSAParams, rho: bytes, K: bytes, tr: bytes,
    s1: np.ndarray, s2: np.ndarray, t0: np.ndarray,
) -> bytes:
    """FIPS 204 Algorithm 24. sk = rho||K||tr || BitPack(s1)||BitPack(s2)||BitPack(t0)."""
    # EXERCISE: implement this function.
    #
    # sk = rho || K || tr || BitPack(s1) || BitPack(s2) || BitPack(t0). s1
    # and s2 pack at (eta, eta); t0 packs at (2^(d-1) - 1, 2^(d-1)).
    #
    # Reference: Chapter 12, 'Serialization: SimpleBitPack and BitPack' (FIPS 204 Algorithm 24)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_encode.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: sk_encode")


def sk_decode(
    params: MLDSAParams, sk: bytes,
) -> tuple[bytes, bytes, bytes, np.ndarray, np.ndarray, np.ndarray]:
    """FIPS 204 Algorithm 25. Inverse of ``sk_encode``."""
    # EXERCISE: implement this function.
    #
    # Invert sk_encode: slice off rho, K, tr from the fixed 128-byte header,
    # then BitUnpack s1 (l polys), s2 (k polys) at (eta, eta) and t0 (k
    # polys) at (2^(d-1) - 1, 2^(d-1)).
    #
    # Reference: Chapter 12, 'Serialization: SimpleBitPack and BitPack' (FIPS 204 Algorithm 25)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_encode.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: sk_decode")


def sig_encode(params: MLDSAParams, c_tilde: bytes, z: np.ndarray, h: np.ndarray) -> bytes:
    """FIPS 204 Algorithm 26. sigma = c-tilde || BitPack(z) || HintBitPack(h)."""
    # EXERCISE: implement this function.
    #
    # sigma = c-tilde || BitPack(z) over l polynomials at (gamma1 - 1,
    # gamma1) || HintBitPack(h).
    #
    # Reference: Chapter 12, 'Serialization: SimpleBitPack and BitPack' (FIPS 204 Algorithm 26)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_encode.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: sig_encode")


def sig_decode(params: MLDSAParams, sig: bytes) -> tuple[bytes, np.ndarray, np.ndarray | None]:
    """FIPS 204 Algorithm 27. Returns (c-tilde, z, h); h is None if malformed."""
    # EXERCISE: implement this function.
    #
    # Invert sig_encode, returning (c-tilde, z, h) where h is None if
    # HintBitUnpack rejects. Slice c-tilde, BitUnpack the l response
    # polynomials at (gamma1 - 1, gamma1), then HintBitUnpack the final
    # omega + k bytes.
    #
    # Reference: Chapter 12, 'Serialization: SimpleBitPack and BitPack' (FIPS 204 Algorithm 27)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_encode.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: sig_decode")


def w1_encode(params: MLDSAParams, w1: np.ndarray) -> bytes:
    """FIPS 204 Algorithm 28. SimpleBitPack each w1 poly at ((q-1)/(2*gamma2) - 1)."""
    # EXERCISE: implement this function.
    #
    # SimpleBitPack each of the k rows of w1 at top = (q-1)/(2*gamma2) - 1,
    # using w1_bits() bits per coefficient. This is the exact byte string
    # the challenge hash commits to, so the width has to match on both
    # sides.
    #
    # Reference: Chapter 12, 'Serialization: SimpleBitPack and BitPack' (FIPS 204 Algorithm 28)
    #
    # Proved by:
    #   tests/ch12/test_mldsa_encode.py
    #   tests/ch12/test_vectors.py
    raise NotImplementedError("exercise: w1_encode")
