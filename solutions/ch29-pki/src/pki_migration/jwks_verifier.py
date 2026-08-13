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
    if len(composite_pk) != COMPOSITE_PK_BYTES:
        raise ValueError(
            f"composite_pk must be {COMPOSITE_PK_BYTES} bytes, got {len(composite_pk)}"
        )
    return {
        "kty": COMPOSITE_KTY,
        "alg": COMPOSITE_ALG,
        "kid": kid,
        "mldsa_pk": _b64url_encode(composite_pk[:MLDSA65_PK_BYTES]),
        "ed_pk": _b64url_encode(composite_pk[MLDSA65_PK_BYTES:]),
    }


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
    parts = jwt_compact.split(".")
    if len(parts) != 3:
        raise ValueError("JWT must have three dot-separated parts")
    header_b64, payload_b64, sig_b64 = parts
    try:
        header = json.loads(_b64url_decode(header_b64))
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"JWT header decode failed: {exc}")
    kid = header.get("kid")
    if kid is None:
        raise ValueError("JWT header missing 'kid'")
    jwk = find_jwk(jwks, kid)
    if jwk.get("kty") != COMPOSITE_KTY:
        raise ValueError(
            f"kid={kid!r} is not a {COMPOSITE_KTY} key (kty={jwk.get('kty')!r})"
        )
    # AND-mode requires the JWK and the JWT header agree on the
    # composite algorithm; a header alg that disagrees with the JWK
    # alg is a confused-deputy signal and must not validate.
    if jwk.get("alg") != COMPOSITE_ALG or header.get("alg") != COMPOSITE_ALG:
        raise ValueError(
            f"alg mismatch on kid={kid!r}: jwk alg={jwk.get('alg')!r} "
            f"header alg={header.get('alg')!r}; both must equal {COMPOSITE_ALG!r}"
        )
    mldsa_pk = _b64url_decode(jwk["mldsa_pk"])
    ed_pk = _b64url_decode(jwk["ed_pk"])
    composite_pk = mldsa_pk + ed_pk
    signed_input = f"{header_b64}.{payload_b64}".encode("ascii")
    signature = _b64url_decode(sig_b64)
    return composite_sig_verify(composite_pk, signed_input, signature)


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
