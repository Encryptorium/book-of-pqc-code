"""Deterministic rank ordering across the candidate set."""

import pytest

from l1_migration import throughput_compare


def test_rank_btc_returns_descending_throughput(candidate_set):
    """rank('btc') returns the four candidates ordered by tx/block desc."""
    ranking = throughput_compare.rank("btc")
    assert len(ranking) == 4
    primitives = [pair[0] for pair in ranking]
    counts = [pair[1] for pair in ranking]
    for primitive in primitives:
        assert primitive in candidate_set
    # Strictly non-increasing throughput.
    for i in range(len(counts) - 1):
        assert counts[i] >= counts[i + 1]


def test_rank_btc_ecdsa_is_first():
    """ECDSA dominates per-block tx throughput on Bitcoin."""
    ranking = throughput_compare.rank("btc")
    assert ranking[0][0] == "ECDSA-secp256k1"


def test_rank_btc_slh_dsa_is_last():
    """SLH-DSA-128s sits at the throughput floor on Bitcoin."""
    ranking = throughput_compare.rank("btc")
    assert ranking[-1][0] == "SLH-DSA-128s"


def test_rank_eth_matches_btc_ordering():
    """Per-tx gas dominated by signature bytes mirrors the BTC ordering.

    Both budgets are limited by the per-tx signature size, so the
    ordering matches even though the absolute throughput numbers
    differ. The chapter calls this out: signature bytes are the
    common bottleneck across both chains for the candidate set.
    """
    btc_order = [pair[0] for pair in throughput_compare.rank("btc")]
    eth_order = [pair[0] for pair in throughput_compare.rank("eth")]
    assert btc_order == eth_order


def test_rank_unknown_budget_assertion():
    """An unknown budget raises an assertion, not a silent fall-through."""
    with pytest.raises(AssertionError, match="unknown budget"):
        throughput_compare.rank("solana")


def test_relative_throughput_ecdsa_self_is_one():
    """Relative throughput of a primitive against itself is 1.0."""
    assert throughput_compare.relative_throughput(
        "ECDSA-secp256k1", "ECDSA-secp256k1"
    ) == 1.0


def test_relative_throughput_pq_below_ecdsa():
    """All PQ candidates report relative throughput strictly below 1.0."""
    for pq in ("ML-DSA-65", "SLH-DSA-128s", "Ed25519+ML-DSA-65"):
        for budget in ("btc", "eth"):
            ratio = throughput_compare.relative_throughput(
                pq, "ECDSA-secp256k1", budget
            )
            assert 0 < ratio < 1.0


def test_relative_throughput_ml_dsa_better_than_slh_dsa():
    """ML-DSA-65 retains more relative throughput than SLH-DSA-128s.

    ML-DSA-65 at 3309-byte signatures is roughly half the size of
    SLH-DSA-128s at 7856 bytes, so it sustains roughly twice the
    relative throughput on both budgets.
    """
    for budget in ("btc", "eth"):
        ml_ratio = throughput_compare.relative_throughput(
            "ML-DSA-65", "ECDSA-secp256k1", budget
        )
        slh_ratio = throughput_compare.relative_throughput(
            "SLH-DSA-128s", "ECDSA-secp256k1", budget
        )
        assert ml_ratio > slh_ratio


def test_relative_throughput_unknown_primitive_assertion():
    """Unknown primitive on either side raises an assertion."""
    with pytest.raises(AssertionError):
        throughput_compare.relative_throughput("FN-DSA-512", "ECDSA-secp256k1")
    with pytest.raises(AssertionError):
        throughput_compare.relative_throughput("ECDSA-secp256k1", "XMSS-MT")
