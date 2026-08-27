"""RFC 7748 Section 5.2 known-answer tests for X25519.

Covers both the single-call vectors and the iterated (1 round, 1000
rounds) vectors. The 1,000,000-round vector is skipped by default
because a million pure-Python scalar multiplications take tens of
minutes; enable via
``CH27_X25519_STRESS=1``.
"""

import os

import pytest

from hybrid.x25519 import x25519_scalarmult


def _h(s: str) -> bytes:
    return bytes.fromhex(s)


def test_rfc7748_section_5_2_vector_one():
    scalar = _h("a546e36bf0527c9d3b16154b82465edd62144c0ac1fc5a18506a2244ba449ac4")
    u = _h("e6db6867583030db3594c1a424b15f7c726624ec26b3353b10a903a6d0ab1c4c")
    expected = _h("c3da55379de9c6908e94ea4df28d084f32eccf03491c71f754b4075577a28552")
    assert x25519_scalarmult(scalar, u) == expected


def test_rfc7748_section_5_2_vector_two():
    scalar = _h("4b66e9d4d1b4673c5ad22691957d6af5c11b6421e0ea01d42ca4169e7918ba0d")
    u = _h("e5210f12786811d3f4b7959d0538ae2c31dbe7106fc03c3efc4cd549c715a493")
    expected = _h("95cbde9476e8907d7aade45cb4b873f88b595a68799fa152e6f8f7647aac7957")
    assert x25519_scalarmult(scalar, u) == expected


def test_rfc7748_iterated_one_round():
    k = _h("0900000000000000000000000000000000000000000000000000000000000000")
    u = k
    k = x25519_scalarmult(k, u)
    expected = _h("422c8e7a6227d7bca1350b3e2bb7279f7897b87bb6854b783c60e80311ae3079")
    assert k == expected


def test_rfc7748_iterated_one_thousand_rounds():
    k = _h("0900000000000000000000000000000000000000000000000000000000000000")
    u = k
    for _ in range(1000):
        k, u = x25519_scalarmult(k, u), k
    expected = _h("684cf59ba83309552800ef566f2f4d3c1c3887c49360e3875f2eb94d99532c51")
    assert k == expected


@pytest.mark.skipif(
    os.environ.get("CH27_X25519_STRESS") != "1",
    reason="one-million-round X25519 KAT is slow; set CH27_X25519_STRESS=1 to run",
)
def test_rfc7748_iterated_one_million_rounds():
    k = _h("0900000000000000000000000000000000000000000000000000000000000000")
    u = k
    for _ in range(1_000_000):
        k, u = x25519_scalarmult(k, u), k
    expected = _h("7c3911e0ab2586fd864497297e575e6f3bc601c0883c30df5f4dd2d24f665424")
    assert k == expected


def test_rfc7748_section_6_1_aborts_on_zero_output():
    """RFC 7748 Section 6.1 requires aborting on zero-output u-coordinate."""
    zero_u = b"\x00" * 32
    scalar = bytes.fromhex(
        "a546e36bf0527c9d3b16154b82465edd62144c0ac1fc5a18506a2244ba449ac4"
    )
    with pytest.raises(ValueError, match="zero"):
        x25519_scalarmult(scalar, zero_u)
