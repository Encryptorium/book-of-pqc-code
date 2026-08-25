"""Per-tx byte budget and per-block throughput across the candidate set."""

import pytest

from l1_migration import byte_budget


def test_candidate_set_size(candidate_set):
    """The candidate set is exactly four primitives."""
    assert len(candidate_set) == 4
    for primitive in candidate_set:
        assert primitive in byte_budget.CANDIDATES


def test_signature_bytes_match_standards(candidate_set):
    """Per-primitive signature bytes match FIPS 204, FIPS 205, and BIP-340.

    Sources:
    - ECDSA-secp256k1 64-byte form: BIP-340 canonical encoding.
    - ML-DSA-65: FIPS 204 (Aug 2024) Table 2.
    - SLH-DSA-128s: FIPS 205 (Aug 2024) Table 2.
    - Composite: Ed25519 (RFC 8032) + ML-DSA-65 sum.
    """
    expected = {
        "ECDSA-secp256k1": 64,
        "ML-DSA-65": 3309,
        "SLH-DSA-128s": 7856,
        "Ed25519+ML-DSA-65": 64 + 3309,
    }
    for primitive in candidate_set:
        assert byte_budget.signature_bytes(primitive) == expected[primitive]


def test_public_key_bytes_match_standards(candidate_set):
    """Public-key sizes match the same standards."""
    expected = {
        "ECDSA-secp256k1": 33,
        "ML-DSA-65": 1952,
        "SLH-DSA-128s": 32,
        "Ed25519+ML-DSA-65": 32 + 1952,
    }
    for primitive in candidate_set:
        assert byte_budget.public_key_bytes(primitive) == expected[primitive]


def test_btc_block_weight_limit_anchor(budget_anchors):
    """The Bitcoin weight-limit constant matches the locked anchor."""
    assert byte_budget.BTC_BLOCK_WEIGHT_LIMIT == budget_anchors["btc_weight_limit"]


def test_eth_gas_limit_anchor(budget_anchors):
    """The Ethereum gas-limit constant matches the locked anchor."""
    assert (
        byte_budget.ETH_BLOCK_GAS_LIMIT
        == budget_anchors["eth_gas_limit_fusaka"]
    )


def test_witness_reveals_pk_only_for_pq_candidates():
    """ECDSA (P2TR-style) hides the pk in scriptPubKey; PQ candidates reveal it.

    The Bitcoin throughput model uses two output patterns. ECDSA at the
    Taproot baseline keeps the tweaked public key in the output script,
    so the witness on spend is the signature alone. Any future PQ
    signature soft fork is assumed to follow a P2WPKH-style commit-
    then-reveal pattern, so the witness reveals both the public key
    and the signature.
    """
    assert byte_budget.witness_reveals_pk("ECDSA-secp256k1") is False
    for pq in ("ML-DSA-65", "SLH-DSA-128s", "Ed25519+ML-DSA-65"):
        assert byte_budget.witness_reveals_pk(pq) is True


def test_witness_bytes_match_output_pattern():
    """witness_bytes sums sig + pk on PQ rows; sig alone on the ECDSA row."""
    assert byte_budget.witness_bytes("ECDSA-secp256k1") == 64
    assert byte_budget.witness_bytes("ML-DSA-65") == 1952 + 3309
    assert byte_budget.witness_bytes("SLH-DSA-128s") == 32 + 7856
    assert byte_budget.witness_bytes("Ed25519+ML-DSA-65") == (32 + 1952) + (64 + 3309)


def test_btc_tx_per_block_ecdsa_baseline():
    """ECDSA at 64-byte signatures yields ~9k transactions per Bitcoin block.

    With 380-weight overhead and a 64-byte witness (P2TR key-path),
    each transaction costs 444 weight units. The 4 MB weight budget
    yields floor(4_000_000 / 444) = 9009 transactions. The figure
    exists as the upper anchor for the migration tax on every PQ
    candidate.
    """
    tx = byte_budget.transactions_per_btc_block("ECDSA-secp256k1")
    assert tx == 4_000_000 // (380 + 64)
    assert tx == 9009


def test_btc_tx_per_block_ml_dsa_includes_public_key():
    """ML-DSA-65 spend reveals pk + sig in witness; toy model gives 709 tx/block.

    With a P2WPKH-style commit-then-reveal output pattern, the spend
    witness carries 1952 + 3309 = 5261 bytes. With 380 overhead the
    per-tx weight is 5641. The 4 MB budget yields floor(4_000_000 /
    5641) = 709 transactions per block, a 12.7-fold drop against the
    ECDSA baseline.
    """
    tx = byte_budget.transactions_per_btc_block("ML-DSA-65")
    assert tx == 4_000_000 // (380 + 1952 + 3309)
    assert tx == 709


def test_btc_tx_per_block_slh_dsa_includes_public_key():
    """SLH-DSA-128s spend witness is 32 + 7856 = 7888 bytes; toy model gives 483 tx/block."""
    tx = byte_budget.transactions_per_btc_block("SLH-DSA-128s")
    assert tx == 4_000_000 // (380 + 32 + 7856)
    assert tx == 483


def test_btc_tx_per_block_composite_includes_public_key():
    """Ed25519+ML-DSA-65 composite spend witness is 1984 + 3373 = 5357 bytes."""
    tx = byte_budget.transactions_per_btc_block("Ed25519+ML-DSA-65")
    assert tx == 4_000_000 // (380 + 1984 + 3373)
    assert tx == 697


def test_btc_tx_per_block_pq_candidates_lose_throughput():
    """All three PQ candidates yield strictly fewer tx/block than ECDSA."""
    ecdsa_tx = byte_budget.transactions_per_btc_block("ECDSA-secp256k1")
    for pq in ("ML-DSA-65", "SLH-DSA-128s", "Ed25519+ML-DSA-65"):
        pq_tx = byte_budget.transactions_per_btc_block(pq)
        assert pq_tx < ecdsa_tx, f"{pq} unexpectedly matches ECDSA throughput"


def test_slh_dsa_btc_throughput_lowest_of_pq():
    """SLH-DSA-128s yields the lowest BTC throughput among PQ candidates.

    7856-byte signature plus 32-byte public key plus 380 overhead is
    8268 weight per spend. ML-DSA-65's 5641 weight per spend is
    roughly two-thirds the per-tx weight, so it fits roughly 1.5x as
    many transactions per block. SLH-DSA-128s remains the throughput
    floor of the PQ candidate set.
    """
    slh_tx = byte_budget.transactions_per_btc_block("SLH-DSA-128s")
    for other in ("ML-DSA-65", "Ed25519+ML-DSA-65"):
        assert slh_tx < byte_budget.transactions_per_btc_block(other)


def test_calldata_gas_proportional_to_sig_size(candidate_set):
    """Calldata gas equals signature bytes * 16 gas per non-zero byte."""
    for primitive in candidate_set:
        sig_bytes = byte_budget.signature_bytes(primitive)
        assert byte_budget.calldata_gas(primitive) == sig_bytes * 16


def test_eth_tx_per_block_calldata_envelope():
    """Per-block Ethereum tx throughput under the marginal calldata model.

    The marginal model is the legacy 16-gas-per-nonzero-byte rate
    that applies on the execution-gas-dominant branch of the
    EIP-7623 max(). ECDSA: 21000 base + 64*16 = 22024 gas per tx.
    60M / 22024 = 2724. ML-DSA-65: 21000 + 3309*16 = 73944 gas per
    tx. 60M / 73944 = 811.
    """
    assert byte_budget.transactions_per_eth_block_calldata("ECDSA-secp256k1") == (
        60_000_000 // (21_000 + 64 * 16)
    )
    assert byte_budget.transactions_per_eth_block_calldata("ML-DSA-65") == (
        60_000_000 // (21_000 + 3309 * 16)
    )


def test_eth_calldata_floor_gas_per_primitive():
    """EIP-7623 floor gas per signature is 40 * sig_bytes for all-nonzero payload.

    Each nonzero calldata byte counts as four tokens under EIP-7623,
    and TOTAL_COST_FLOOR_PER_TOKEN is 10, so an all-nonzero signature
    payload contributes 40 gas per byte on the floor branch.
    """
    assert byte_budget.calldata_floor_gas("ECDSA-secp256k1") == 40 * 64
    assert byte_budget.calldata_floor_gas("ML-DSA-65") == 40 * 3309
    assert byte_budget.calldata_floor_gas("SLH-DSA-128s") == 40 * 7856
    assert byte_budget.calldata_floor_gas("Ed25519+ML-DSA-65") == 40 * (64 + 3309)


def test_eip_7623_constants_are_pinned_individually():
    """The two EIP-7623 constants are pinned separately, not just their product.

    EIP-7623 defines tokens_in_calldata = zero_bytes + 4*nonzero_bytes
    and TOTAL_COST_FLOOR_PER_TOKEN = 10. Every other assertion in this
    file reaches them only through calldata_floor_gas, which multiplies
    the two, so 4 and 10 could be swapped and every one of those
    assertions would still hold. That would leave both constants naming
    the wrong quantity from the EIP while the arithmetic came out right.
    """
    assert byte_budget.ETH_GAS_TOKENS_PER_NONZERO_BYTE == 4
    assert byte_budget.ETH_GAS_FLOOR_PER_TOKEN == 10


def test_eth_tx_per_block_calldata_floor():
    """Per-block tx throughput under the EIP-7623 data-floor model.

    For an all-nonzero signature, per-tx gas = 21000 + 40*sig_bytes.
    ECDSA: 21000 + 2560 = 23560. 60M / 23560 = 2546.
    ML-DSA-65: 21000 + 132360 = 153360. 60M / 153360 = 391.
    SLH-DSA-128s: 21000 + 314240 = 335240. 60M / 335240 = 178.
    Ed25519+ML-DSA-65: 21000 + 134920 = 155920. 60M / 155920 = 384.
    """
    assert byte_budget.transactions_per_eth_block_calldata_floor("ECDSA-secp256k1") == 2546
    assert byte_budget.transactions_per_eth_block_calldata_floor("ML-DSA-65") == 391
    assert byte_budget.transactions_per_eth_block_calldata_floor("SLH-DSA-128s") == 178
    assert byte_budget.transactions_per_eth_block_calldata_floor("Ed25519+ML-DSA-65") == 384


def test_floor_model_is_strictly_tighter_than_marginal(candidate_set):
    """The EIP-7623 floor model is a strictly tighter bound than the marginal model.

    Because 40 > 16, the floor model charges more per nonzero byte
    and therefore admits strictly fewer transactions per block.
    """
    for primitive in candidate_set:
        marginal = byte_budget.transactions_per_eth_block_calldata(primitive)
        floor = byte_budget.transactions_per_eth_block_calldata_floor(primitive)
        assert floor < marginal, f"{primitive}: floor {floor} not strictly tighter than marginal {marginal}"


def test_evaluate_returns_full_envelope(candidate_set):
    """evaluate returns sig bytes, pk bytes, witness bytes, btc tx/block,
    eth tx/block under both the marginal and the EIP-7623 floor models."""
    for primitive in candidate_set:
        result = byte_budget.evaluate(primitive)
        assert result["primitive"] == primitive
        assert result["sig_bytes"] == byte_budget.signature_bytes(primitive)
        assert result["pk_bytes"] == byte_budget.public_key_bytes(primitive)
        assert result["witness_bytes"] == byte_budget.witness_bytes(primitive)
        assert result["btc_tx_per_block"] == byte_budget.transactions_per_btc_block(
            primitive
        )
        assert result["eth_tx_per_block_calldata"] == (
            byte_budget.transactions_per_eth_block_calldata(primitive)
        )
        assert result["eth_tx_per_block_calldata_floor"] == (
            byte_budget.transactions_per_eth_block_calldata_floor(primitive)
        )
        assert result["deployment_shape"] in (
            "deployed-baseline",
            "soft-fork-or-account-abstraction",
            "composite-cutover",
        )


def test_deployment_shape_is_per_candidate():
    """Each candidate carries its own deployment shape, not just a valid one.

    test_evaluate_returns_full_envelope asserts only that the shape is
    a member of the three-element vocabulary, which four candidates
    drawn from three labels satisfy under any permutation: ECDSA can
    read composite-cutover and ML-DSA-65 can read deployed-baseline
    with the whole suite green. The chapter's Tradeoffs table prints
    this column, so the label has to be pinned per row.
    """
    expected = {
        "ECDSA-secp256k1": "deployed-baseline",
        "ML-DSA-65": "soft-fork-or-account-abstraction",
        "SLH-DSA-128s": "soft-fork-or-account-abstraction",
        "Ed25519+ML-DSA-65": "composite-cutover",
    }
    for primitive, shape in expected.items():
        assert byte_budget.evaluate(primitive)["deployment_shape"] == shape


def test_unknown_primitive_assertion():
    """Unknown primitives fail loudly via assert at every entry point."""
    with pytest.raises(AssertionError, match="unknown primitive"):
        byte_budget.signature_bytes("FN-DSA-512")
    with pytest.raises(AssertionError, match="unknown primitive"):
        byte_budget.public_key_bytes("XMSS-MT")
    with pytest.raises(AssertionError, match="unknown primitive"):
        byte_budget.transactions_per_btc_block("RSA-2048")
    with pytest.raises(AssertionError, match="unknown primitive"):
        byte_budget.calldata_gas("BLS-BLS12-381")
    with pytest.raises(AssertionError, match="unknown primitive"):
        byte_budget.evaluate("LMS")
    with pytest.raises(AssertionError, match="unknown primitive"):
        byte_budget.witness_reveals_pk("Falcon-512")
    with pytest.raises(AssertionError, match="unknown primitive"):
        byte_budget.witness_bytes("BLS-BLS12-381")
    with pytest.raises(AssertionError, match="unknown primitive"):
        byte_budget.calldata_floor_gas("Picnic")
    with pytest.raises(AssertionError, match="unknown primitive"):
        byte_budget.transactions_per_eth_block_calldata_floor("Picnic")
