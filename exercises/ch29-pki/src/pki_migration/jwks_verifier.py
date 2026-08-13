"""JWKS composite-signature JWT verifier.

Pedagogical verifier for an RFC 7517 JWKS that carries an Ed25519 +
ML-DSA-65 composite public key under a dedicated ``kid`` (RFC 7517
section 4.5). The composite signature construction is Ch 27's; the
encoding for the X.509 layer is draft-ietf-lamps-pq-composite-sigs-19
(LAMPS identifier ``id-MLDSA65-Ed25519-SHA512``, OID
``1.3.6.1.5.5.7.6.48``); single ML-DSA gained finalized JOSE/COSE
serialization in RFC 9964 (AKP JWK key type; ``ML-DSA-44``,
``ML-DSA-65``, ``ML-DSA-87`` algorithm identifiers), but composite
ML-DSA + Ed25519 remains draft-level in JOSE, so the ``kty`` and
``alg`` identifiers below are illustrative for a deployment-owned
JWKS, not interoperable across JOSE libraries.

Public API:

- ``build_composite_jwk(kid, composite_pk) -> dict``: build the JWK
  for a composite key.
- ``find_jwk(jwks, kid) -> dict``: look up a JWK by ``kid``.
- ``verify_composite_jwt(jwt_compact, jwks) -> bool``: verify a JWT
  whose header's ``kid`` names a composite JWK.

The composite public key is published as two named members rather
than one blob: ``mldsa_pk`` carries the leading
``MLDSA65_PK_BYTES`` (1952) bytes and ``ed_pk`` the trailing 32,
matching Ch 27's ``mldsaPK || tradPK`` serialization (LAMPS draft
section 4.1). Each member holds what its name says, so a consumer
that is not this verifier can read either component without
knowing the other's length.

The verify path imports ``composite_sig_verify`` from
``solutions/ch27-hybrid`` via ``sys.path`` insertion.
"""

import base64
import json
import sys
from pathlib import Path

_HYBRID_SRC = Path(__file__).resolve().parents[3] / "ch27-hybrid" / "src"
if str(_HYBRID_SRC) not in sys.path:
    sys.path.insert(0, str(_HYBRID_SRC))

from hybrid.sig_combiner import (  # noqa: E402
    COMPOSITE_PK_BYTES,
    MLDSA65_PK_BYTES,
    composite_sig_verify,
)


COMPOSITE_KTY = "OKP-COMPOSITE"
COMPOSITE_ALG = "Ed25519+ML-DSA-65"


def _b64url_encode(data: bytes) -> str:
    """Base64url encode (RFC 7515 section 2) without padding."""
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    """Base64url decode; tolerates missing padding."""
    pad = (-len(s)) % 4
    return base64.urlsafe_b64decode(s + ("=" * pad))


def build_composite_jwk(kid: str, composite_pk: bytes) -> dict:
    """Build a composite JWK for a ``COMPOSITE_PK_BYTES``-byte public key.

    Ch 27 serializes the composite public key as
    ``mldsaPK || tradPK`` (LAMPS draft section 4.1), so the split
    point is ``MLDSA65_PK_BYTES``, not the Ed25519 length.

    Raises ``ValueError`` on wrong-sized input.
    """
    # EXERCISE: implement this function.
    #
    # The composite public key is the ML-DSA-65 key followed by the Ed25519
    # key, per the LAMPS draft's SerializePublicKey, so split it at
    # MLDSA65_PK_BYTES and publish the halves as separate base64url members
    # mldsa_pk and ed_pk. Splitting at the wrong offset still round-trips
    # through verify_composite_jwt, because that function reassembles
    # exactly what this one split, so nothing in the suite catches it except
    # an assertion against an independently derived Ed25519 key. Reject any
    # input that is not exactly COMPOSITE_PK_BYTES long with ValueError
    # rather than publishing a truncated key that will fail verification
    # much later. The kty and alg values are the module constants; they are
    # deployment-owned rather than JOSE-registered, which is why they are
    # versioned strings and not an IANA identifier.
    #
    # Reference: Chapter 29, 'JWKS and JWT migration'
    #
    # Proved by:
    #   tests/ch29/test_jwks_composite_verifier.py
    raise NotImplementedError("exercise: build_composite_jwk")


def find_jwk(jwks: dict, kid: str) -> dict:
    """Return the JWK in ``jwks["keys"]`` matching ``kid``.

    Raises ``KeyError`` if no entry matches.
    """
    for jwk in jwks["keys"]:
        if jwk.get("kid") == kid:
            return jwk
    raise KeyError(f"no JWK with kid={kid!r} in JWKS")


def verify_composite_jwt(jwt_compact: str, jwks: dict) -> bool:
    """Verify a compact JWT under a composite-kid JWK.

    Splits the compact JWT into ``header.payload.signature``. The
    header's ``kid`` must name a JWK whose ``kty`` is
    ``COMPOSITE_KTY``. Reconstructs ``pk = mldsa_pk || ed_pk`` from
    the JWK and calls ``composite_sig_verify`` from Ch 27.

    Raises ``ValueError`` on malformed JWT or a non-composite kid;
    raises ``KeyError`` if the JWKS does not contain the referenced
    kid.
    """
    # EXERCISE: implement this function.
    #
    # Split the compact JWT on dots; anything other than three parts is a
    # ValueError. Decode the header, read its kid, and look that kid up in
    # the JWKS. Three checks must all hold before any cryptography runs: the
    # JWK's kty is COMPOSITE_KTY, the JWK's alg is COMPOSITE_ALG, and the
    # header's alg is that same value. A header alg that disagrees with the
    # JWK alg is a confused-deputy signal and must not validate. Then
    # rebuild pk as mldsa_pk followed by ed_pk, matching the order
    # build_composite_jwk split on, take the signing input as the ASCII
    # bytes of the first two parts still base64url-encoded and joined by a
    # dot (RFC 7515 section 5.1), and hand pk, that input, and the decoded
    # signature to composite_sig_verify from Ch 27, which runs the AND-mode
    # check.
    #
    # Reference: Chapter 29, 'JWKS and JWT migration' (RFC 7515 section 5.1)
    #
    # Proved by:
    #   tests/ch29/test_jwks_composite_verifier.py
    raise NotImplementedError("exercise: verify_composite_jwt")


def build_compact_jwt(header: dict, payload: dict, signature: bytes) -> str:
    """Assemble a compact JWT from header, payload, and signature bytes.

    Useful for tests and the inline block: the signing side writes a
    JSON header and payload, then attaches a composite signature over
    the base64url-encoded ``header.payload`` string.
    """
    header_b64 = _b64url_encode(
        json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    payload_b64 = _b64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    sig_b64 = _b64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def signed_input(header: dict, payload: dict) -> bytes:
    """Return the JWS signing input ``base64url(header).base64url(payload)``
    as ASCII bytes. Callers pass this to ``composite_sig_sign``.
    """
    header_b64 = _b64url_encode(
        json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    payload_b64 = _b64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    return f"{header_b64}.{payload_b64}".encode("ascii")
