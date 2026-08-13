"""Tests for ``pki_migration.chain_analyzer``."""

import pytest

from pki_migration.chain_analyzer import (
    CertRef,
    analyze_chain,
    classify_oid,
    OID_ECDSA_P256_SHA256,
    OID_ECDSA_P384_SHA384,
    OID_ED25519,
    OID_MLDSA65_ED25519_SHA512,
    OID_ML_DSA_65,
    OID_RSA_SHA256,
    OID_SLH_DSA_SHA2_128S,
)


def _chain(*oids: str) -> list[CertRef]:
    return [
        CertRef(subject=f"cn{i}", issuer=f"cn{i+1}", sig_oid=oid)
        for i, oid in enumerate(oids)
    ]


def test_classify_known_classical_oids() -> None:
    assert classify_oid(OID_RSA_SHA256) == "classical"
    assert classify_oid(OID_ECDSA_P256_SHA256) == "classical"
    assert classify_oid(OID_ECDSA_P384_SHA384) == "classical"
    assert classify_oid(OID_ED25519) == "classical"


def test_classify_known_pq_oids() -> None:
    assert classify_oid(OID_ML_DSA_65) == "single-pq"
    assert classify_oid(OID_SLH_DSA_SHA2_128S) == "single-pq"
    assert classify_oid(OID_MLDSA65_ED25519_SHA512) == "composite"


def test_classify_unknown_oid() -> None:
    assert classify_oid("9.9.9.9") == "unknown"


def test_classical_only_chain() -> None:
    report = analyze_chain(_chain(OID_RSA_SHA256, OID_RSA_SHA256, OID_RSA_SHA256))
    assert report.depth == 3
    assert report.per_cert == ("classical", "classical", "classical")
    assert report.overall == "classical-only"


def test_composite_only_chain() -> None:
    report = analyze_chain(
        _chain(OID_MLDSA65_ED25519_SHA512, OID_MLDSA65_ED25519_SHA512, OID_MLDSA65_ED25519_SHA512)
    )
    assert report.overall == "composite-only"


def test_single_pq_only_chain() -> None:
    report = analyze_chain(_chain(OID_ML_DSA_65, OID_ML_DSA_65))
    assert report.overall == "single-pq-only"


def test_classical_above_composite_leaf_is_bug() -> None:
    """Composite leaf with a classical link above it: forge the classical, forge the leaf."""
    report = analyze_chain(_chain(OID_MLDSA65_ED25519_SHA512, OID_RSA_SHA256))
    assert report.overall == "mixed-classical-above-pq-leaf"


def test_classical_above_single_pq_leaf_is_bug() -> None:
    report = analyze_chain(_chain(OID_ML_DSA_65, OID_RSA_SHA256))
    assert report.overall == "mixed-classical-above-pq-leaf"


def test_heterogeneous_pq_chain_is_not_a_bug() -> None:
    """Composite leaf over single-PQ intermediates is heterogeneous PQ, not a downgrade."""
    report = analyze_chain(
        _chain(OID_MLDSA65_ED25519_SHA512, OID_ML_DSA_65, OID_ML_DSA_65)
    )
    assert report.overall == "mixed-transition"


def test_classical_leaf_under_pq_links_is_transition() -> None:
    """Classical leaf still under PQ higher links during re-issuance is a rollout state, not a bug."""
    report = analyze_chain(
        _chain(OID_ECDSA_P256_SHA256, OID_MLDSA65_ED25519_SHA512, OID_MLDSA65_ED25519_SHA512)
    )
    assert report.overall == "mixed-transition"


def test_unknown_oid_reported_over_mixed() -> None:
    report = analyze_chain(_chain(OID_MLDSA65_ED25519_SHA512, "9.9.9.9"))
    assert report.overall == "unknown-oid-present"


def test_empty_chain() -> None:
    report = analyze_chain([])
    assert report.depth == 0
    assert report.per_cert == ()
    assert report.overall == "empty"


def test_single_cert_classical() -> None:
    report = analyze_chain(_chain(OID_ED25519))
    assert report.depth == 1
    assert report.overall == "classical-only"
