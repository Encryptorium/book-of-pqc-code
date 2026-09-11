"""Tests for ``pki_migration.jwks_verifier``.

End-to-end: generate a composite keypair via Ch 27 ``composite_sig_keygen``,
publish the public key as a JWK, sign a JWT, and verify it via the Ch 29
JWKS verifier.
"""

import pytest

from hybrid.ed25519 import ed25519_keygen
from hybrid.sig_combiner import (
    COMPOSITE_PK_BYTES,
    COMPOSITE_SIG_BYTES,
    MLDSA65_PK_BYTES,
    MLDSA65_SIG_BYTES,
    composite_sig_keygen,
    composite_sig_sign,
)
from pki_migration.jwks_verifier import (
    COMPOSITE_ALG,
    COMPOSITE_KTY,
    _b64url_decode,
    build_compact_jwt,
    build_composite_jwk,
    find_jwk,
    signed_input,
    verify_composite_jwt,
)


_SEED_ED = b"\x01" * 32
_SEED_MLDSA = b"\x02" * 32


def _gen_jwks(kid: str = "composite-2026-04"):
    pk, sk = composite_sig_keygen(_SEED_ED, _SEED_MLDSA)
    jwk = build_composite_jwk(kid, pk)
    jwks = {"keys": [jwk]}
    return pk, sk, jwks


def _sign_jwt(sk: bytes, kid: str, payload: dict) -> str:
    header = {"alg": COMPOSITE_ALG, "kid": kid, "typ": "JWT"}
    msg = signed_input(header, payload)
    sig = composite_sig_sign(sk, msg)
    return build_compact_jwt(header, payload, sig)


def test_composite_jwk_fields() -> None:
    pk, _sk, jwks = _gen_jwks(kid="k1")
    assert len(pk) == COMPOSITE_PK_BYTES
    jwk = jwks["keys"][0]
    assert jwk["kty"] == COMPOSITE_KTY
    assert jwk["alg"] == COMPOSITE_ALG
    assert jwk["kid"] == "k1"
    assert "ed_pk" in jwk and "mldsa_pk" in jwk


def test_jwk_members_hold_what_their_names_say() -> None:
    """The Ed25519 member is derived independently; the ML-DSA member is
    checked for length only.

    A round-trip cannot catch a mislabelling, because build and verify
    would slice at the same wrong offset and the concatenation would
    reassemble the original bytes. Comparing ``ed_pk`` against
    ``ed25519_keygen``'s own output is what tests the published names,
    and it pins the slice boundary from one side, which is enough to
    catch a swapped pair. ``mldsa_pk`` gets no independent comparison
    here.
    """
    _pk, _sk, jwks = _gen_jwks(kid="k-named")
    jwk = jwks["keys"][0]
    ed_pk_expected, _ed_sk = ed25519_keygen(_SEED_ED)
    assert _b64url_decode(jwk["ed_pk"]) == ed_pk_expected
    assert len(_b64url_decode(jwk["mldsa_pk"])) == MLDSA65_PK_BYTES


def test_build_composite_jwk_rejects_wrong_size() -> None:
    with pytest.raises(ValueError):
        build_composite_jwk("bad", b"\x00" * 10)


def test_find_jwk_hits() -> None:
    _pk, _sk, jwks = _gen_jwks(kid="k-hit")
    assert find_jwk(jwks, "k-hit")["kid"] == "k-hit"


def test_find_jwk_missing_raises_keyerror() -> None:
    _pk, _sk, jwks = _gen_jwks(kid="k-exists")
    with pytest.raises(KeyError):
        find_jwk(jwks, "not-there")


def test_roundtrip_verify_composite_jwt() -> None:
    _pk, sk, jwks = _gen_jwks(kid="composite-2026-04")
    jwt = _sign_jwt(sk, kid="composite-2026-04", payload={"sub": "alice", "exp": 999})
    assert verify_composite_jwt(jwt, jwks) is True


def test_tampered_payload_fails_verify() -> None:
    _pk, sk, jwks = _gen_jwks(kid="composite-2026-04")
    jwt = _sign_jwt(sk, kid="composite-2026-04", payload={"sub": "alice"})
    header_b64, payload_b64, sig_b64 = jwt.split(".")
    # Change a single character in the payload; base64url still decodes but
    # signed_input changes, so AND-mode verify should reject.
    tampered = header_b64 + "." + payload_b64[:-2] + "AA" + "." + sig_b64
    assert verify_composite_jwt(tampered, jwks) is False


def test_tampered_ed25519_half_fails_and_mode() -> None:
    """Zero the Ed25519 component only: AND-mode rejects.

    ``composite_sig_sign`` returns ``mldsa_sig || ed_sig``, so the Ed25519
    component is the 64-byte SUFFIX and not the prefix.  The slice
    assertions below are what keep this test about the component it names:
    without them a mutation of the ML-DSA half would produce the same
    rejection and the test would pass while proving something else.
    """
    _pk, sk, jwks = _gen_jwks(kid="composite-2026-04")
    jwt = _sign_jwt(sk, kid="composite-2026-04", payload={"sub": "alice"})
    from pki_migration.jwks_verifier import _b64url_decode, _b64url_encode

    header_b64, payload_b64, sig_b64 = jwt.split(".")
    sig = _b64url_decode(sig_b64)
    assert len(sig) == COMPOSITE_SIG_BYTES
    ed_bytes = COMPOSITE_SIG_BYTES - MLDSA65_SIG_BYTES
    forged = sig[:MLDSA65_SIG_BYTES] + bytes(ed_bytes)

    assert forged[:MLDSA65_SIG_BYTES] == sig[:MLDSA65_SIG_BYTES], (
        "the ML-DSA component must be untouched"
    )
    assert forged[MLDSA65_SIG_BYTES:] != sig[MLDSA65_SIG_BYTES:], (
        "the Ed25519 component must actually change"
    )

    tampered = header_b64 + "." + payload_b64 + "." + _b64url_encode(forged)
    assert verify_composite_jwt(tampered, jwks) is False


def test_missing_kid_in_header_raises() -> None:
    _pk, sk, jwks = _gen_jwks(kid="k")
    header = {"alg": COMPOSITE_ALG, "typ": "JWT"}
    msg = signed_input(header, {"sub": "x"})
    sig = composite_sig_sign(sk, msg)
    jwt = build_compact_jwt(header, {"sub": "x"}, sig)
    with pytest.raises(ValueError, match="kid"):
        verify_composite_jwt(jwt, jwks)


def test_kid_not_in_jwks_raises_keyerror() -> None:
    _pk, sk, jwks = _gen_jwks(kid="k-actual")
    jwt = _sign_jwt(sk, kid="k-requested", payload={"sub": "x"})
    with pytest.raises(KeyError):
        verify_composite_jwt(jwt, jwks)


def test_non_composite_kid_raises() -> None:
    _pk, sk, jwks = _gen_jwks(kid="k-composite")
    jwks["keys"].append({"kty": "RSA", "kid": "k-rsa", "n": "AA", "e": "AQAB"})
    jwt = _sign_jwt(sk, kid="k-rsa", payload={"sub": "x"})
    with pytest.raises(ValueError, match=COMPOSITE_KTY):
        verify_composite_jwt(jwt, jwks)


def test_malformed_jwt_raises() -> None:
    _pk, _sk, jwks = _gen_jwks()
    with pytest.raises(ValueError, match="three"):
        verify_composite_jwt("only.two", jwks)


def test_multi_kid_jwks_selects_correct_key() -> None:
    """Two composite kids published side-by-side; verify picks the right one."""
    pk_a, sk_a = composite_sig_keygen(b"\x0a" * 32, b"\x0b" * 32)
    pk_b, sk_b = composite_sig_keygen(b"\x0c" * 32, b"\x0d" * 32)
    jwks = {
        "keys": [
            build_composite_jwk("k-a", pk_a),
            build_composite_jwk("k-b", pk_b),
        ],
    }
    jwt_b = _sign_jwt(sk_b, kid="k-b", payload={"sub": "b"})
    assert verify_composite_jwt(jwt_b, jwks) is True
    # A JWT signed with sk_a but claiming kid=k-b fails (different pk).
    forged = _sign_jwt(sk_a, kid="k-b", payload={"sub": "b"})
    assert verify_composite_jwt(forged, jwks) is False
