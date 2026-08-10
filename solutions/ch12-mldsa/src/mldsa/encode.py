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
    w = np.asarray(w, dtype=np.int64)
    assert w.shape == (256,), f"simple_bit_pack: expected length-256, got {w.shape}"
    width = bitlen(b)
    mask = (1 << width) - 1
    big = 0
    for i in range(256):
        v = int(w[i])
        assert 0 <= v <= b, f"simple_bit_pack: coeff {v} outside [0, {b}]"
        big |= (v & mask) << (i * width)
    return big.to_bytes(32 * width, "little")


def simple_bit_unpack(v: bytes, b: int) -> np.ndarray:
    """FIPS 204 Algorithm 18. Inverse of ``simple_bit_pack``."""
    width = bitlen(b)
    assert len(v) == 32 * width, f"simple_bit_unpack: expected {32 * width} bytes, got {len(v)}"
    big = int.from_bytes(v, "little")
    mask = (1 << width) - 1
    out = np.empty(256, dtype=np.int64)
    for i in range(256):
        out[i] = (big >> (i * width)) & mask
    return out


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
    h = np.asarray(h, dtype=np.int64)
    assert h.shape == (params.k, 256), f"hint_bit_pack: expected ({params.k}, 256)"
    y = bytearray(params.omega + params.k)
    index = 0
    for i in range(params.k):
        for j in range(256):
            if h[i][j] != 0:
                y[index] = j
                index += 1
        y[params.omega + i] = index
    return bytes(y)


def hint_bit_unpack(params: MLDSAParams, y: bytes) -> np.ndarray | None:
    """FIPS 204 Algorithm 21. Deserialize a hint, or return None (bottom) if
    the encoding is malformed."""
    omega, k = params.omega, params.k
    assert len(y) == omega + k, f"hint_bit_unpack: expected {omega + k} bytes, got {len(y)}"
    h = np.zeros((k, 256), dtype=np.int64)
    index = 0
    for i in range(k):
        end = y[omega + i]
        if end < index or end > omega:
            return None
        first = index
        while index < end:
            if index > first and y[index - 1] >= y[index]:
                return None  # positions within a poly must strictly increase
            h[i][y[index]] = 1
            index += 1
    for i in range(index, omega):
        if y[i] != 0:
            return None  # unused position slots must be zero
    return h


# --- Object encoders (parameterized by the set). ---

def pk_encode(params: MLDSAParams, rho: bytes, t1: np.ndarray) -> bytes:
    """FIPS 204 Algorithm 22. pk = rho || SimpleBitPack(t1[i]) for i in [0, k)."""
    assert len(rho) == 32, f"pk_encode: rho must be 32 bytes, got {len(rho)}"
    t1 = np.asarray(t1, dtype=np.int64)
    assert t1.shape == (params.k, 256), f"pk_encode: t1 must be ({params.k}, 256)"
    top = (1 << params.t1_bits()) - 1
    out = bytearray(rho)
    for i in range(params.k):
        out += simple_bit_pack(t1[i], top)
    return bytes(out)


def pk_decode(params: MLDSAParams, pk: bytes) -> tuple[bytes, np.ndarray]:
    """FIPS 204 Algorithm 23. Inverse of ``pk_encode``."""
    assert len(pk) == params.pk_len(), f"pk_decode: expected {params.pk_len()} bytes"
    top = (1 << params.t1_bits()) - 1
    rho = pk[:32]
    stride = 32 * params.t1_bits()
    t1 = np.empty((params.k, 256), dtype=np.int64)
    off = 32
    for i in range(params.k):
        t1[i] = simple_bit_unpack(pk[off:off + stride], top)
        off += stride
    return rho, t1


def sk_encode(
    params: MLDSAParams, rho: bytes, K: bytes, tr: bytes,
    s1: np.ndarray, s2: np.ndarray, t0: np.ndarray,
) -> bytes:
    """FIPS 204 Algorithm 24. sk = rho||K||tr || BitPack(s1)||BitPack(s2)||BitPack(t0)."""
    assert len(rho) == 32 and len(K) == 32 and len(tr) == 64, "sk_encode: bad seed lengths"
    s1 = np.asarray(s1, dtype=np.int64)
    s2 = np.asarray(s2, dtype=np.int64)
    t0 = np.asarray(t0, dtype=np.int64)
    assert s1.shape == (params.l, 256) and s2.shape == (params.k, 256), "sk_encode: bad s shapes"
    assert t0.shape == (params.k, 256), "sk_encode: bad t0 shape"
    eta = params.eta
    t0_a = (1 << (D - 1)) - 1
    t0_b = 1 << (D - 1)
    out = bytearray(rho + K + tr)
    for i in range(params.l):
        out += bit_pack(s1[i], eta, eta)
    for i in range(params.k):
        out += bit_pack(s2[i], eta, eta)
    for i in range(params.k):
        out += bit_pack(t0[i], t0_a, t0_b)
    return bytes(out)


def sk_decode(
    params: MLDSAParams, sk: bytes,
) -> tuple[bytes, bytes, bytes, np.ndarray, np.ndarray, np.ndarray]:
    """FIPS 204 Algorithm 25. Inverse of ``sk_encode``."""
    assert len(sk) == params.sk_len(), f"sk_decode: expected {params.sk_len()} bytes"
    eta = params.eta
    rho, K, tr = sk[:32], sk[32:64], sk[64:128]
    off = 128
    s_stride = 32 * params.eta_bits()
    s1 = np.empty((params.l, 256), dtype=np.int64)
    for i in range(params.l):
        s1[i] = bit_unpack(sk[off:off + s_stride], eta, eta)
        off += s_stride
    s2 = np.empty((params.k, 256), dtype=np.int64)
    for i in range(params.k):
        s2[i] = bit_unpack(sk[off:off + s_stride], eta, eta)
        off += s_stride
    t0_a = (1 << (D - 1)) - 1
    t0_b = 1 << (D - 1)
    t0_stride = 32 * params.t0_bits()
    t0 = np.empty((params.k, 256), dtype=np.int64)
    for i in range(params.k):
        t0[i] = bit_unpack(sk[off:off + t0_stride], t0_a, t0_b)
        off += t0_stride
    return rho, K, tr, s1, s2, t0


def sig_encode(params: MLDSAParams, c_tilde: bytes, z: np.ndarray, h: np.ndarray) -> bytes:
    """FIPS 204 Algorithm 26. sigma = c-tilde || BitPack(z) || HintBitPack(h)."""
    assert len(c_tilde) == params.c_tilde_len(), "sig_encode: bad c-tilde length"
    z = np.asarray(z, dtype=np.int64)
    assert z.shape == (params.l, 256), f"sig_encode: z must be ({params.l}, 256)"
    g1 = params.gamma_1
    out = bytearray(c_tilde)
    for i in range(params.l):
        out += bit_pack(z[i], g1 - 1, g1)
    out += hint_bit_pack(params, h)
    return bytes(out)


def sig_decode(params: MLDSAParams, sig: bytes) -> tuple[bytes, np.ndarray, np.ndarray | None]:
    """FIPS 204 Algorithm 27. Returns (c-tilde, z, h); h is None if malformed."""
    assert len(sig) == params.sig_len(), f"sig_decode: expected {params.sig_len()} bytes"
    clen = params.c_tilde_len()
    g1 = params.gamma_1
    c_tilde = sig[:clen]
    off = clen
    z_stride = 32 * params.gamma1_bits()
    z = np.empty((params.l, 256), dtype=np.int64)
    for i in range(params.l):
        z[i] = bit_unpack(sig[off:off + z_stride], g1 - 1, g1)
        off += z_stride
    h = hint_bit_unpack(params, sig[off:off + params.omega + params.k])
    return c_tilde, z, h


def w1_encode(params: MLDSAParams, w1: np.ndarray) -> bytes:
    """FIPS 204 Algorithm 28. SimpleBitPack each w1 poly at ((q-1)/(2*gamma2) - 1)."""
    w1 = np.asarray(w1, dtype=np.int64)
    assert w1.shape == (params.k, 256), f"w1_encode: w1 must be ({params.k}, 256)"
    top = (Q - 1) // (2 * params.gamma_2) - 1
    out = bytearray()
    for i in range(params.k):
        out += simple_bit_pack(w1[i], top)
    return bytes(out)
