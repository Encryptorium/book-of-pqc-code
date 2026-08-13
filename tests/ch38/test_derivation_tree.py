"""Tests for wallet_rotation.derivation_tree.

Covers BIP-32-style derivation under each of the six candidate
primitives, the parse_path helper, the per-primitive property
report, and the per-step support flag.
"""

from wallet_rotation import derivation_tree


MASTER_SEED = bytes.fromhex(
    "000102030405060708090a0b0c0d0e0f"
    "101112131415161718191a1b1c1d1e1f"
)


def test_parse_path_master_only():
    assert derivation_tree.parse_path("m") == []


def test_parse_path_hardened_marker():
    parsed = derivation_tree.parse_path("m/44'/0'/0'/0/0")
    assert parsed == [
        (44, True),
        (0, True),
        (0, True),
        (0, False),
        (0, False),
    ]


def test_parse_path_rejects_missing_master():
    try:
        derivation_tree.parse_path("44'/0'/0'/0/0")
    except AssertionError:
        return
    raise AssertionError("expected AssertionError for path without 'm'")


def test_parse_path_rejects_overflow_index():
    # 2147483648 == 2**31 == 0x80000000 in decimal; the parser rejects any
    # index that would overflow the 31-bit non-hardened space.
    try:
        derivation_tree.parse_path("m/2147483648")
    except AssertionError:
        return
    raise AssertionError("expected AssertionError for overflow index")


def test_properties_known_primitives():
    ecdsa = derivation_tree.properties("ECDSA-secp256k1")
    assert ecdsa["hardened"] is True
    assert ecdsa["non_hardened"] is True
    assert ecdsa["watch_only"] is True

    ml_dsa = derivation_tree.properties("ML-DSA-65")
    assert ml_dsa["hardened"] is True
    assert ml_dsa["non_hardened"] is False
    assert ml_dsa["watch_only"] is False

    slh_dsa = derivation_tree.properties("SLH-DSA-128s")
    assert slh_dsa["hardened"] is True
    assert slh_dsa["non_hardened"] is False
    assert slh_dsa["watch_only"] is False


def test_properties_composite_is_hardened_only():
    composite = derivation_tree.properties("Ed25519+ML-DSA-65")
    assert composite["hardened"] is True
    assert composite["non_hardened"] is False
    assert composite["watch_only"] is False


def test_properties_stateful_schemes_are_hardened_only():
    xmss = derivation_tree.properties("XMSS-MT")
    lms = derivation_tree.properties("LMS")
    for props in (xmss, lms):
        assert props["hardened"] is True
        assert props["non_hardened"] is False
        assert props["watch_only"] is False


def test_properties_rejects_unknown_primitive():
    try:
        derivation_tree.properties("RSA-2048")
    except AssertionError:
        return
    raise AssertionError("expected AssertionError for unknown primitive")


def test_derive_master_step_is_first():
    steps = derivation_tree.derive("ECDSA-secp256k1", MASTER_SEED, "m")
    assert len(steps) == 1
    assert steps[0]["depth"] == 0
    assert steps[0]["kind"] == "master"
    assert len(bytes.fromhex(steps[0]["secret_hex"])) == 32
    assert len(bytes.fromhex(steps[0]["chain_code_hex"])) == 32


def test_derive_path_walks_each_index():
    path = "m/44'/0'/0'/0/0"
    steps = derivation_tree.derive("ECDSA-secp256k1", MASTER_SEED, path)
    assert len(steps) == 6  # master plus five path components
    assert steps[1]["index"] == 44
    assert steps[1]["hardened"] is True
    assert steps[-1]["index"] == 0
    assert steps[-1]["hardened"] is False


def test_derive_supported_flag_under_ecdsa():
    path = "m/44'/0'/0'/0/0"
    steps = derivation_tree.derive("ECDSA-secp256k1", MASTER_SEED, path)
    # ECDSA supports both hardened and non-hardened, so every step survives.
    assert all(step["supported"] for step in steps)


def test_derive_supported_flag_under_ml_dsa():
    path = "m/44'/0'/0'/0/0"
    steps = derivation_tree.derive("ML-DSA-65", MASTER_SEED, path)
    # The first three (hardened) steps are supported; the last two
    # (non-hardened) are NOT supported because ML-DSA-65 does not
    # admit a public-key-only derivation.
    supports = [step["supported"] for step in steps if step["depth"] > 0]
    assert supports == [True, True, True, False, False]


def test_derive_supported_flag_under_slh_dsa():
    path = "m/44'/0'/0'/0/0"
    steps = derivation_tree.derive("SLH-DSA-128s", MASTER_SEED, path)
    supports = [step["supported"] for step in steps if step["depth"] > 0]
    assert supports == [True, True, True, False, False]


def test_derive_supported_flag_under_stateful_schemes():
    path = "m/44'/0'/0'/0/0"
    for primitive in ("XMSS-MT", "LMS", "Ed25519+ML-DSA-65"):
        steps = derivation_tree.derive(primitive, MASTER_SEED, path)
        supports = [step["supported"] for step in steps if step["depth"] > 0]
        assert supports == [True, True, True, False, False], primitive


def test_derive_is_deterministic():
    path = "m/0'/1/2"
    a = derivation_tree.derive("ECDSA-secp256k1", MASTER_SEED, path)
    b = derivation_tree.derive("ECDSA-secp256k1", MASTER_SEED, path)
    assert a == b


def test_derive_rejects_short_master_seed():
    try:
        derivation_tree.derive("ECDSA-secp256k1", b"too short", "m/0'")
    except AssertionError:
        return
    raise AssertionError("expected AssertionError for short master seed")


def test_watch_only_supported_only_for_ecdsa():
    assert derivation_tree.watch_only_supported("ECDSA-secp256k1") is True
    for primitive in (
        "ML-DSA-65",
        "SLH-DSA-128s",
        "Ed25519+ML-DSA-65",
        "XMSS-MT",
        "LMS",
    ):
        assert derivation_tree.watch_only_supported(primitive) is False, primitive


def test_evaluate_returns_pedagogical_dict():
    report = derivation_tree.evaluate("ML-DSA-65")
    assert report["primitive"] == "ML-DSA-65"
    assert report["hardened"] is True
    assert report["non_hardened"] is False
    assert report["watch_only"] is False
    assert "structured" in report["rationale"]


# The token that must appear in each primitive's PROPERTIES rationale.
_PROPERTY_TOKENS = {
    "ECDSA-secp256k1": "scalar offset",
    "ML-DSA-65": "structured signing key",
    "SLH-DSA-128s": "hash hypertree",
    "Ed25519+ML-DSA-65": "composite",
    "XMSS-MT": "hypertree subtree",
    "LMS": "Merkle subtree",
}


def test_property_rationales_are_bound_to_their_primitive(primitives):
    # Five of the six PROPERTIES rows carry identical flags (hardened
    # True, non_hardened False, watch_only False), so every flag
    # assertion in this file is blind to a permutation among them. Only
    # ML-DSA-65's rationale was pinned, by the "structured" substring in
    # test_evaluate_returns_pedagogical_dict. That leaves SLH-DSA-128s,
    # the composite, XMSS-MT and LMS freely interchangeable, which would
    # let LMS read "hardened-only because the ML-DSA component is
    # hardened-only" with the suite green.
    for primitive in primitives:
        token = _PROPERTY_TOKENS[primitive]
        assert token in derivation_tree.properties(primitive)["rationale"], primitive


def test_property_tokens_are_unique_to_one_primitive(primitives):
    for primitive in primitives:
        token = _PROPERTY_TOKENS[primitive]
        carriers = {
            other
            for other in primitives
            if token in derivation_tree.properties(other)["rationale"]
        }
        assert carriers == {primitive}, (token, carriers)


def test_primitives_tuple_matches_six_candidates():
    assert set(derivation_tree.PRIMITIVES) == {
        "ECDSA-secp256k1",
        "ML-DSA-65",
        "SLH-DSA-128s",
        "Ed25519+ML-DSA-65",
        "XMSS-MT",
        "LMS",
    }
