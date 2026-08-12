"""The brittle and agile signers of Chapter 26, Block 1."""

import base64
import json

import pytest

from agility.tokens import (
    REGISTRY,
    b64url,
    sign_agile,
    sign_brittle,
    verify_agile,
    verify_brittle,
)


PAYLOAD = {"sub": "user-42"}


def test_b64url_strips_padding():
    assert b64url(b"\x00") == "AA"
    assert b64url(b"ab") == "YWI"
    assert "=" not in b64url(b"abcd")


def test_b64url_is_url_safe():
    # 0xfb 0xff encodes to "+/" under standard base64.
    assert b64url(bytes([0xFB, 0xFF])) == "-_8"


def test_brittle_round_trip():
    assert verify_brittle(sign_brittle(PAYLOAD)) is True


def test_brittle_header_carries_no_alg():
    """The whole point of the brittle version: nothing on the wire names
    the hash function, so an audit tool reading tokens cannot count uses."""

    header = sign_brittle(PAYLOAD).split(".")[0]
    decoded = json.loads(base64.urlsafe_b64decode(header + "==="))
    assert "alg" not in decoded


def test_brittle_rejects_a_tampered_body():
    header, body, sig = sign_brittle(PAYLOAD).split(".")
    other = b64url(json.dumps({"sub": "user-43"}).encode())
    assert verify_brittle(f"{header}.{other}.{sig}") is False


@pytest.mark.parametrize("alg", ["HS256", "HS384", "HS512"])
def test_agile_round_trip_at_every_approved_algorithm(alg):
    assert verify_agile(sign_agile(PAYLOAD, alg)) is True


@pytest.mark.parametrize("alg", ["HS256", "HS384", "HS512"])
def test_agile_header_carries_the_identifier(alg):
    header = sign_agile(PAYLOAD, alg).split(".")[0]
    assert json.loads(base64.urlsafe_b64decode(header + "==="))["alg"] == alg


def test_agile_signatures_differ_by_algorithm():
    """Different hash functions produce different signatures over the
    same payload, so the identifier is load-bearing at verification."""

    sigs = {sign_agile(PAYLOAD, a).split(".")[2] for a in ("HS256", "HS384", "HS512")}
    assert len(sigs) == 3


def test_agile_signing_refuses_a_deprecated_algorithm():
    with pytest.raises(ValueError, match="deprecated"):
        sign_agile(PAYLOAD, "HS1")


def test_agile_verification_refuses_a_deprecated_algorithm():
    """A token minted before HS1 was flagged still fails verification,
    which is the deprecation flag doing its job on both paths."""

    hash_fn, _ = REGISTRY["HS1"]
    REGISTRY["HS1"] = (hash_fn, False)
    try:
        token = sign_agile(PAYLOAD, "HS1")
    finally:
        REGISTRY["HS1"] = (hash_fn, True)
    assert verify_agile(token) is False


def test_agile_verification_refuses_an_unknown_identifier():
    header = b64url(json.dumps({"typ": "JWT", "alg": "HS999"}).encode())
    body = b64url(json.dumps(PAYLOAD).encode())
    assert verify_agile(f"{header}.{body}.AAAA") is False


def test_agile_verification_refuses_alg_none():
    """The alg:none bypass family fails here because the registry lookup
    misses before any signature comparison happens."""

    header = b64url(json.dumps({"typ": "JWT", "alg": "none"}).encode())
    body = b64url(json.dumps(PAYLOAD).encode())
    assert verify_agile(f"{header}.{body}.") is False


def test_agile_verification_rejects_a_wrong_secret():
    token = sign_agile(PAYLOAD, "HS256")
    assert verify_agile(token, secret=b"not-the-secret") is False
