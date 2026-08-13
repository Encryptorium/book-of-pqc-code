"""Composite vs component byte arithmetic."""

import pytest

from l1_migration import composite_overhead


def test_overhead_ed25519_ml_dsa_65_sums_correctly():
    """Ed25519+ML-DSA-65 composite signature is 64 + 3309 = 3373 bytes.

    Public key total is 32 + 1952 = 1984 bytes. Per RFC 8032 (Ed25519)
    and FIPS 204 (ML-DSA-65).
    """
    info = composite_overhead.overhead("Ed25519+ML-DSA-65")
    assert info["composite_sig_bytes"] == 64 + 3309
    assert info["composite_pk_bytes"] == 32 + 1952
    assert info["component_a"] == "Ed25519"
    assert info["component_b"] == "ML-DSA-65"
    assert info["component_a_sig_bytes"] == 64
    assert info["component_b_sig_bytes"] == 3309


def test_overhead_ed25519_slh_dsa_128s_sums_correctly():
    """Ed25519+SLH-DSA-128s composite is 64 + 7856 = 7920 bytes."""
    info = composite_overhead.overhead("Ed25519+SLH-DSA-128s")
    assert info["composite_sig_bytes"] == 64 + 7856
    assert info["composite_pk_bytes"] == 32 + 32


def test_sig_overhead_vs_strongest_is_classical_size():
    """The marginal byte cost of carrying the second signature is the smaller component.

    For Ed25519+ML-DSA-65, the strongest component is ML-DSA-65 (3309
    bytes); the overhead vs that alone equals the Ed25519 size (64).
    """
    info = composite_overhead.overhead("Ed25519+ML-DSA-65")
    assert info["sig_overhead_vs_strongest"] == 64

    info_slh = composite_overhead.overhead("Ed25519+SLH-DSA-128s")
    assert info_slh["sig_overhead_vs_strongest"] == 64


def test_pk_overhead_vs_strongest_is_classical_size():
    """Public-key overhead equals the smaller component pk size."""
    info = composite_overhead.overhead("Ed25519+ML-DSA-65")
    assert info["pk_overhead_vs_strongest"] == 32

    info_slh = composite_overhead.overhead("Ed25519+SLH-DSA-128s")
    assert info_slh["pk_overhead_vs_strongest"] == 32


def test_overhead_ratio_close_to_one_for_balanced_pq():
    """Composite vs the larger PQ component is a small multiplicative penalty.

    Ed25519+ML-DSA-65 is 3373 / 3309 ≈ 1.019 (about 2% byte overhead).
    Ed25519+SLH-DSA-128s is 7920 / 7856 ≈ 1.008 (about 0.8% overhead).
    The composite is cheap in bytes precisely because the classical
    component is small relative to the PQ component.
    """
    ratio_ml = composite_overhead.overhead_ratio("Ed25519+ML-DSA-65")
    assert 1.01 < ratio_ml < 1.03

    ratio_slh = composite_overhead.overhead_ratio("Ed25519+SLH-DSA-128s")
    assert 1.005 < ratio_slh < 1.015


def test_unknown_composite_assertion():
    """An unknown composite key fails loudly."""
    with pytest.raises(AssertionError, match="unknown composite"):
        composite_overhead.overhead("Ed25519+XMSS-MT")
    with pytest.raises(AssertionError, match="unknown composite"):
        composite_overhead.overhead_ratio("ECDSA+ML-DSA-65")
