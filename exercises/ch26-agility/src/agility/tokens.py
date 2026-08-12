"""Brittle and agile JWT-like signers (Chapter 26, Block 1).

Two signing paths over the same payload. ``sign_brittle`` hard-codes
HMAC-SHA256 at every call site and emits no algorithm identifier at all.
``sign_agile`` looks the primitive up in a registry keyed by algorithm
identifier, writes that identifier into the token header, and
``verify_agile`` reads it back out to pick the verifier.

These are deliberately JWT-*like* pedagogical tokens rather than
standards-compliant JWS objects. RFC 7515 Section 4.1.1 makes the ``alg``
Header Parameter mandatory, so the brittle token would be rejected
outright by a conforming verifier; omitting it is what makes the
observability cost visible. A production verifier also needs the
key-to-algorithm binding of RFC 8725 Section 3.1, key-id lookup, and
issuer, audience and expiry checks, none of which is modelled here.

``SECRET`` is a fixed pedagogical value so the module runs standalone.
Every signing and verifying function takes the secret as a parameter
defaulting to it; production code passes a key resolved per key-id.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any, Callable


SECRET = b"pedagogical-secret-bytes-only"

# alg identifier -> (hash constructor, deprecated flag)
REGISTRY: dict[str, tuple[Callable[[], Any], bool]] = {
    "HS256": (hashlib.sha256, False),
    "HS384": (hashlib.sha384, False),
    "HS512": (hashlib.sha512, False),
    "HS1": (hashlib.sha1, True),
}


def b64url(data: bytes) -> str:
    """Base64url-encode ``data`` with the padding stripped."""

    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def sign_brittle(payload: dict[str, Any], secret: bytes = SECRET) -> str:
    """Sign ``payload`` with HMAC-SHA256 hard-coded, emitting no ``alg``."""

    header = b64url(b'{"typ":"JWT"}')
    body = b64url(json.dumps(payload).encode())
    signed = f"{header}.{body}".encode()
    sig = hmac.new(secret, signed, hashlib.sha256).digest()
    return f"{header}.{body}.{b64url(sig)}"


def verify_brittle(token: str, secret: bytes = SECRET) -> bool:
    """Verify a brittle token, assuming HMAC-SHA256 without checking."""

    header, body, sig_in = token.split(".")
    signed = f"{header}.{body}".encode()
    expected = b64url(hmac.new(secret, signed, hashlib.sha256).digest())
    return hmac.compare_digest(sig_in, expected)


def sign_agile(
    payload: dict[str, Any], alg: str, secret: bytes = SECRET
) -> str:
    """Sign ``payload`` under ``alg``, writing the identifier into the header.

    Raises ``ValueError`` if the registry marks ``alg`` deprecated. A
    deprecated algorithm is refused for signing but still accepted for
    verification elsewhere, which is the asymmetry the chapter's
    lifecycle-management area describes.
    """

    hash_fn, deprecated = REGISTRY[alg]
    if deprecated:
        raise ValueError(f"algorithm {alg} is deprecated")
    header = b64url(json.dumps({"typ": "JWT", "alg": alg}).encode())
    body = b64url(json.dumps(payload).encode())
    signed = f"{header}.{body}".encode()
    sig = hmac.new(secret, signed, hash_fn).digest()
    return f"{header}.{body}.{b64url(sig)}"


def verify_agile(token: str, secret: bytes = SECRET) -> bool:
    """Verify a token by dispatching on its own ``alg`` header.

    Returns ``False`` for an unknown identifier and for a deprecated one,
    which is what makes the ``alg: none`` and unknown-algorithm bypass
    families fail against this verifier.
    """

    header, body, sig_in = token.split(".")
    alg = json.loads(base64.urlsafe_b64decode(header + "==="))["alg"]
    if alg not in REGISTRY:
        return False
    hash_fn, deprecated = REGISTRY[alg]
    if deprecated:
        return False
    signed = f"{header}.{body}".encode()
    expected = b64url(hmac.new(secret, signed, hash_fn).digest())
    return hmac.compare_digest(sig_in, expected)
