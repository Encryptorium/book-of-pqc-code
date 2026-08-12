"""The namespaced identifier parser of Chapter 26, Block 2."""

import pytest

from agility.algid import parse_algid


def test_the_three_identifiers_the_chapter_prints():
    assert parse_algid("RSA-PSS/SHA-256/salt=32") == (
        "RSA-PSS",
        {"SHA-256": True, "salt": "32"},
    )
    assert parse_algid("ML-DSA-65") == ("ML-DSA-65", {})
    assert parse_algid("HMAC-SHA256/deprecated") == (
        "HMAC-SHA256",
        {"deprecated": True},
    )


def test_a_bare_primitive_has_no_parameters():
    primitive, params = parse_algid("AES-256-GCM")
    assert primitive == "AES-256-GCM"
    assert params == {}


def test_a_bare_segment_parses_to_the_boolean_true():
    """A flag carries no value, so it must not become the empty string:
    an empty string is falsy and would invert the flag's meaning."""

    _, params = parse_algid("X/flag")
    assert params["flag"] is True


def test_a_valued_segment_stays_a_string():
    _, params = parse_algid("X/salt=32")
    assert params["salt"] == "32"
    assert not isinstance(params["salt"], bool)


def test_a_later_segment_wins_on_a_repeated_key():
    _, params = parse_algid("X/salt=16/salt=32")
    assert params["salt"] == "32"


@pytest.mark.parametrize(
    "algid,primitive",
    [
        ("ECDHE-ECDSA-AES256-GCM-SHA384", "ECDHE-ECDSA-AES256-GCM-SHA384"),
        ("PBKDF2/hash=SHA-256/iterations=600000", "PBKDF2"),
        ("HMAC-SHA256/key_bytes=32", "HMAC-SHA256"),
    ],
)
def test_the_primitive_is_always_the_first_segment(algid, primitive):
    assert parse_algid(algid)[0] == primitive
