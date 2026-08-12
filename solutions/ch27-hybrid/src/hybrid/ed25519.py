"""Ed25519 (EdDSA over Curve25519) per RFC 8032 Section 5.1.

Pure-Python reference implementation. This is the classical component
of the Ed25519+ML-DSA-65 explicit-composite signature.

Public API:

- ``ed25519_keygen(seed: bytes) -> tuple[bytes, bytes]``: given a
  32-byte seed (secret key), return ``(public_key, secret_key)``.
- ``ed25519_sign(secret_key: bytes, message: bytes) -> bytes``: produce
  a 64-byte Ed25519 signature.
- ``ed25519_verify(public_key: bytes, message: bytes, signature: bytes)
  -> bool``: AND-mode friendly Boolean verification.

Test vectors at RFC 8032 Section 7.1 are exercised by
``tests/ch27/test_ed25519_kat.py``.
"""

import hashlib


_Q = 2**255 - 19
_L = 2**252 + 27742317777372353535851937790883648493
_D = -121665 * pow(121666, _Q - 2, _Q) % _Q
_BY = 4 * pow(5, _Q - 2, _Q) % _Q


def _xrecover(y: int) -> int:
    xx = (y * y - 1) * pow(_D * y * y + 1, _Q - 2, _Q) % _Q
    x = pow(xx, (_Q + 3) // 8, _Q)
    if (x * x - xx) % _Q != 0:
        x = (x * pow(2, (_Q - 1) // 4, _Q)) % _Q
    if x % 2 != 0:
        x = _Q - x
    return x


_BX = _xrecover(_BY)
_BASE = (_BX % _Q, _BY % _Q, 1, (_BX * _BY) % _Q)


def _edwards_add(P, Q):
    x1, y1, z1, t1 = P
    x2, y2, z2, t2 = Q
    a = (y1 - x1) * (y2 - x2) % _Q
    b = (y1 + x1) * (y2 + x2) % _Q
    c = t1 * 2 * _D * t2 % _Q
    d = z1 * 2 * z2 % _Q
    e = b - a
    f = d - c
    g = d + c
    h = b + a
    return (e * f % _Q, g * h % _Q, f * g % _Q, e * h % _Q)


def _scalarmult(P, e: int):
    if e == 0:
        return (0, 1, 1, 0)
    Q = _scalarmult(P, e // 2)
    Q = _edwards_add(Q, Q)
    if e & 1:
        Q = _edwards_add(Q, P)
    return Q


def _encode_point(P) -> bytes:
    x, y, z, _ = P
    zi = pow(z, _Q - 2, _Q)
    x = (x * zi) % _Q
    y = (y * zi) % _Q
    encoded = bytearray((y % (1 << 255)).to_bytes(32, "little"))
    encoded[31] |= (x & 1) << 7
    return bytes(encoded)


def _decode_point(s: bytes):
    if len(s) != 32:
        raise ValueError("point encoding must be 32 bytes")
    y = int.from_bytes(s, "little") & ((1 << 255) - 1)
    x = _xrecover(y)
    if x & 1 != (s[31] >> 7) & 1:
        x = _Q - x
    P = (x, y, 1, (x * y) % _Q)
    if not _on_curve(P):
        raise ValueError("decoded point not on curve")
    return P


def _on_curve(P) -> bool:
    x, y, z, t = P
    return (
        (z * t - x * y) % _Q == 0
        and (-x * x + y * y - z * z - _D * t * t) % _Q == 0
    )


def _h(data: bytes) -> bytes:
    return hashlib.sha512(data).digest()


def _h_int(data: bytes) -> int:
    return int.from_bytes(_h(data), "little")


def _secret_expand(seed: bytes) -> tuple[int, bytes]:
    if len(seed) != 32:
        raise ValueError("seed must be 32 bytes")
    digest = bytearray(_h(seed))
    digest[0] &= 248
    digest[31] &= 127
    digest[31] |= 64
    a = int.from_bytes(digest[:32], "little")
    prefix = bytes(digest[32:])
    return a, prefix


def ed25519_keygen(seed: bytes) -> tuple[bytes, bytes]:
    """Derive ``(public_key, secret_key)`` from a 32-byte seed.

    The secret key returned here is the 32-byte seed itself; the full
    expanded scalar is recomputed inside ``ed25519_sign``.
    """
    a, _ = _secret_expand(seed)
    A = _scalarmult(_BASE, a)
    return _encode_point(A), bytes(seed)


def ed25519_sign(secret_key: bytes, message: bytes) -> bytes:
    """Produce a 64-byte Ed25519 signature over ``message``."""
    a, prefix = _secret_expand(secret_key)
    A = _encode_point(_scalarmult(_BASE, a))
    r = _h_int(prefix + message) % _L
    R = _scalarmult(_BASE, r)
    R_enc = _encode_point(R)
    k = _h_int(R_enc + A + message) % _L
    s = (r + k * a) % _L
    return R_enc + s.to_bytes(32, "little")


def ed25519_verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """Return True iff ``signature`` is a valid Ed25519 signature."""
    if len(signature) != 64 or len(public_key) != 32:
        return False
    R_enc = signature[:32]
    s = int.from_bytes(signature[32:], "little")
    if s >= _L:
        return False
    try:
        R = _decode_point(R_enc)
        A = _decode_point(public_key)
    except ValueError:
        return False
    k = _h_int(R_enc + public_key + message) % _L
    left = _scalarmult(_BASE, s)
    right = _edwards_add(R, _scalarmult(A, k))
    return _encode_point(left) == _encode_point(right)
