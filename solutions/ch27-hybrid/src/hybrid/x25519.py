"""X25519 (Curve25519 scalar multiplication) per RFC 7748.

The Montgomery ladder over ``GF(2^255 - 19)`` with scalar clamping as
specified in RFC 7748 Section 5. This is the classical component of
the X25519MLKEM768 hybrid KEM.

Public API:

- ``x25519_scalarmult(scalar, u) -> bytes``: compute ``scalar * u`` on
  Curve25519, returning the 32-byte u-coordinate of the result.
- ``x25519_base(scalar) -> bytes``: ``x25519_scalarmult(scalar, 9)``,
  the canonical base-point multiplication used for public-key
  generation.

Test vectors at RFC 7748 Section 5.2 are exercised by
``tests/ch27/test_x25519_kat.py``.
"""

_P = 2**255 - 19
_A24 = 121665
_BITS = 255


def _decode_scalar(k: bytes) -> int:
    if len(k) != 32:
        raise ValueError("scalar must be 32 bytes")
    k_bytes = bytearray(k)
    k_bytes[0] &= 248
    k_bytes[31] &= 127
    k_bytes[31] |= 64
    return int.from_bytes(k_bytes, "little")


def _decode_u(u: bytes) -> int:
    if len(u) != 32:
        raise ValueError("u-coordinate must be 32 bytes")
    u_bytes = bytearray(u)
    u_bytes[31] &= 127
    return int.from_bytes(u_bytes, "little")


def _encode_u(u: int) -> bytes:
    return (u % _P).to_bytes(32, "little")


def _cswap(swap: int, x2: int, x3: int) -> tuple[int, int]:
    mask = -swap & ((1 << 255) - 1)
    dummy = mask & (x2 ^ x3)
    return x2 ^ dummy, x3 ^ dummy


def x25519_scalarmult(scalar: bytes, u: bytes) -> bytes:
    """Compute scalar * u on Curve25519. Returns a 32-byte result."""
    k = _decode_scalar(scalar)
    x1 = _decode_u(u)
    x2, z2, x3, z3 = 1, 0, x1, 1
    swap = 0
    for t in range(_BITS - 1, -1, -1):
        kt = (k >> t) & 1
        swap ^= kt
        x2, x3 = _cswap(swap, x2, x3)
        z2, z3 = _cswap(swap, z2, z3)
        swap = kt
        A = (x2 + z2) % _P
        AA = (A * A) % _P
        B = (x2 - z2) % _P
        BB = (B * B) % _P
        E = (AA - BB) % _P
        C = (x3 + z3) % _P
        D = (x3 - z3) % _P
        DA = (D * A) % _P
        CB = (C * B) % _P
        x3 = pow((DA + CB) % _P, 2, _P)
        z3 = (x1 * pow((DA - CB) % _P, 2, _P)) % _P
        x2 = (AA * BB) % _P
        z2 = (E * ((AA + _A24 * E) % _P)) % _P
    x2, x3 = _cswap(swap, x2, x3)
    z2, z3 = _cswap(swap, z2, z3)
    result = (x2 * pow(z2, _P - 2, _P)) % _P
    if result == 0:
        # RFC 7748 Section 6.1: implementations MUST abort if the
        # Diffie-Hellman output u-coordinate is zero.
        raise ValueError("X25519 output u-coordinate is zero (RFC 7748 6.1)")
    return _encode_u(result)


_BASE_POINT = b"\x09" + b"\x00" * 31


def x25519_base(scalar: bytes) -> bytes:
    """Scalar multiplication by the Curve25519 base point (u = 9)."""
    return x25519_scalarmult(scalar, _BASE_POINT)
