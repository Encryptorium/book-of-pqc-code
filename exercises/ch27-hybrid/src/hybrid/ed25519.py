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
    # EXERCISE: implement this function.
    #
    # Expand the 32-byte seed with _secret_expand to get the clamped scalar
    # a, multiply the base point by a, and encode the result. The public key
    # is that encoded point; the secret key returned is the seed itself, not
    # the expanded scalar, because signing re-derives both a and the nonce
    # prefix from the seed each time.
    #
    # Reference: RFC 8032 Section 5.1.5, cited in Chapter 27, 'ML-DSA-65+Ed25519 composite signatures'
    #
    # Proved by:
    #   tests/ch27/test_ed25519_kat.py
    #   tests/ch27/test_composite_sig_roundtrip.py
    raise NotImplementedError("exercise: ed25519_keygen")


def ed25519_sign(secret_key: bytes, message: bytes) -> bytes:
    """Produce a 64-byte Ed25519 signature over ``message``."""
    # EXERCISE: implement this function.
    #
    # Deterministic Schnorr over Edwards25519. Expand the seed into the
    # scalar a and the 32-byte prefix, and recompute the encoded public key
    # A. The nonce is r = H(prefix || message) reduced mod L, which is what
    # makes the signature deterministic without an RNG; R is the base point
    # times r. The challenge is k = H(encode(R) || A || message) mod L and
    # the response is s = (r + k*a) mod L. Return encode(R) || s as 32
    # little-endian bytes each, 64 bytes total. Both hash outputs are read
    # little-endian before reduction.
    #
    # Reference: RFC 8032 Section 5.1.6, cited in Chapter 27, 'ML-DSA-65+Ed25519 composite signatures'
    #
    # Proved by:
    #   tests/ch27/test_ed25519_kat.py
    #   tests/ch27/test_composite_sig_roundtrip.py
    raise NotImplementedError("exercise: ed25519_sign")


def ed25519_verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """Return True iff ``signature`` is a valid Ed25519 signature."""
    # EXERCISE: implement this function.
    #
    # Return False rather than raising on every rejection path, because the
    # composite combiner needs a Boolean from both halves. Reject a
    # signature or public key of the wrong length, and reject an s that is
    # not below the group order L, which is the canonical-encoding check
    # that blocks trivial malleability. Decode R and A, returning False if
    # either decode raises. Recompute k = H(R_enc || public_key || message)
    # mod L and check that the base point times s equals R plus A times k,
    # comparing the two through their encodings so the projective
    # representatives do not have to match.
    #
    # Reference: RFC 8032 Section 5.1.7, cited in Chapter 27, 'ML-DSA-65+Ed25519 composite signatures'
    #
    # Proved by:
    #   tests/ch27/test_ed25519_kat.py
    #   tests/ch27/test_composite_sig_roundtrip.py
    raise NotImplementedError("exercise: ed25519_verify")
