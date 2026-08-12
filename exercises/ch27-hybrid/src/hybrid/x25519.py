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
    # EXERCISE: implement this function.
    #
    # The Montgomery ladder. Decode the scalar with the clamping helper (low
    # three bits cleared, bit 254 set, bit 255 cleared) and the u-coordinate
    # with its mask, then run the ladder from bit 254 down to bit 0 over the
    # state (x2, z2, x3, z3) starting at (1, 0, x1, 1). Track a running swap
    # bit, conditionally swap both pairs with _cswap before each step, and
    # set swap to the current scalar bit afterwards; the
    # double-and-add-always shape is what keeps the trace independent of the
    # scalar. Each step is the RFC 7748 formula block: A = x2 + z2, B = x2 -
    # z2, E = A^2 - B^2, and so on, with a24 = 121665. Swap one last time
    # after the loop, recover the affine result as x2 * z2^(p-2) mod p, and
    # encode it little-endian. Raise ValueError when the result is zero: RFC
    # 7748 Section 6.1 allows the check and RFC 10024 Section 4.3 makes it a
    # MUST for TLS.
    #
    # Reference: RFC 7748 Section 5 (the ladder and clamping) and Section 6.1 (the zero-output abort), cited in Chapter 27, 'The X25519MLKEM768 hybrid KEM'
    #
    # Proved by:
    #   tests/ch27/test_x25519_kat.py
    raise NotImplementedError("exercise: x25519_scalarmult")


_BASE_POINT = b"\x09" + b"\x00" * 31


def x25519_base(scalar: bytes) -> bytes:
    """Scalar multiplication by the Curve25519 base point (u = 9)."""
    return x25519_scalarmult(scalar, _BASE_POINT)
