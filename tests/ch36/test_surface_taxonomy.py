"""Tests for ``blockchain_threat.surface_taxonomy``."""

import pytest

from blockchain_threat import (
    PRIMITIVE_CLASSIFICATION,
    classify,
    classify_all,
)


def test_classification_table_partitions_into_three_classes() -> None:
    classes = set(PRIMITIVE_CLASSIFICATION.values())
    assert classes == {
        "shor-vulnerable",
        "hash-quantum-degraded",
        "post-quantum-standardized",
    }


def test_strand_surfaces_classify(strand_assets: list[dict]) -> None:
    results = classify_all(strand_assets)
    assert results == [
        ("transaction", "shor-vulnerable"),
        ("consensus", "shor-vulnerable"),
        ("wallet", "shor-vulnerable"),
        ("on-chain-verifier", "hash-quantum-degraded"),
        ("governance", "shor-vulnerable"),
    ]


def test_classify_one_record_returns_class() -> None:
    record = {
        "surface": "demo",
        "primitive": "ML-DSA-65",
        "exposure": "public",
        "lifecycle": "per-block",
    }
    assert classify(record) == "post-quantum-standardized"


def test_unknown_primitive_asserts() -> None:
    record = {
        "surface": "demo",
        "primitive": "fictional-2030",
        "exposure": "public",
        "lifecycle": "per-block",
    }
    with pytest.raises(AssertionError, match="unknown primitive"):
        classify(record)


def test_classify_all_preserves_input_order() -> None:
    assets = [
        {"surface": "B", "primitive": "SHA-256", "exposure": "x", "lifecycle": "x"},
        {"surface": "A", "primitive": "ML-DSA-65", "exposure": "x", "lifecycle": "x"},
    ]
    result = classify_all(assets)
    assert [name for name, _ in result] == ["B", "A"]


def test_pq_signature_schemes_are_post_quantum_standardized() -> None:
    for primitive in (
        "ML-DSA-65",
        "ML-DSA-87",
        "SLH-DSA-128s",
        "SLH-DSA-256f",
        "XMSS-MT",
        "LMS",
    ):
        assert PRIMITIVE_CLASSIFICATION[primitive] == "post-quantum-standardized"


def test_fn_dsa_is_absent_pending_fips_206() -> None:
    # FIPS 206 (FN-DSA, from Falcon) is under development at chain-tip
    # 2026 with no Initial Public Draft released, so there is no final
    # parameter set and "post-quantum-standardized" would be false of
    # it. The table therefore omits it and the classifier crashes.
    assert "FN-DSA-512" not in PRIMITIVE_CLASSIFICATION
    record = {
        "surface": "demo",
        "primitive": "FN-DSA-512",
        "exposure": "public",
        "lifecycle": "per-block",
    }
    with pytest.raises(AssertionError, match="unknown primitive"):
        classify(record)


def test_strand_fixture_pins_each_surface_to_its_primitive(
    strand_assets: list[dict],
) -> None:
    # classify_all reports the vulnerability CLASS, and four of the
    # five Strand surfaces share one class, so a permutation of the
    # primitives across those four leaves every other test in this
    # file green. This test reads the primitive itself, so the
    # canonical fixture Ch 37 to Ch 41 thread through cannot drift.
    assert {a["surface"]: a["primitive"] for a in strand_assets} == {
        "transaction": "ECDSA-secp256k1",
        "consensus": "BLS-BLS12-381",
        "wallet": "ECDSA-secp256k1",
        "on-chain-verifier": "SHA-256",
        "governance": "Schnorr-secp256k1",
    }


def test_discrete_log_primitives_are_shor_vulnerable() -> None:
    for primitive in (
        "ECDSA-secp256k1",
        "Schnorr-secp256k1",
        "EdDSA-Ed25519",
        "BLS-BLS12-381",
        "RSA-2048",
    ):
        assert PRIMITIVE_CLASSIFICATION[primitive] == "shor-vulnerable"
