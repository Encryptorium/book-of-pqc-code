"""Tests for the per-proof gas-cost arithmetic."""

import pytest

from zk_rollups import gas_budget as gb


# ---- Constants and configuration shape --------------------------------


def test_eth_block_gas_limit_matches_ch37_anchor():
    """Ch 40 reuses the Ch 37 ETH_BLOCK_GAS_LIMIT anchor (60M; EIP-7935 EL-client default, Fusaka)."""
    assert gb.ETH_BLOCK_GAS_LIMIT == 60_000_000


def test_three_configurations_in_canonical_order(configurations):
    """The CONFIGURATIONS tuple matches the chapter's three-config comparison."""
    assert list(gb.CONFIGURATIONS) == configurations


def test_legacy_per_proof_gas_is_five_million():
    """Legacy SHA-256 STARK is anchored at 5M gas per proof (ethSTARK shape)."""
    assert gb.LEGACY_SHA256_STARK_GAS_PER_PROOF == 5_000_000


def test_wider_hash_per_proof_gas_is_above_legacy():
    """Wider-hash STARK costs more per proof than legacy."""
    assert gb.WIDER_HASH_STARK_GAS_PER_PROOF > gb.LEGACY_SHA256_STARK_GAS_PER_PROOF


def test_recursive_outer_per_proof_gas_is_above_legacy():
    """Outer recursive verifier is at least as costly as legacy in absolute terms."""
    assert gb.RECURSIVE_STARK_OUTER_GAS_PER_PROOF >= gb.LEGACY_SHA256_STARK_GAS_PER_PROOF


def test_recursive_batch_size_is_one_hundred():
    """Default recursive batch size is 100 inner proofs per outer proof."""
    assert gb.RECURSIVE_STARK_BATCH_PROOFS == 100


# ---- per_proof_gas behavior --------------------------------------------


def test_per_proof_gas_legacy_returns_anchor():
    assert gb.per_proof_gas("legacy-sha256-stark") == gb.LEGACY_SHA256_STARK_GAS_PER_PROOF


def test_per_proof_gas_wider_hash_returns_anchor():
    assert gb.per_proof_gas("wider-hash-stark") == gb.WIDER_HASH_STARK_GAS_PER_PROOF


def test_per_proof_gas_recursive_amortizes_outer_over_batch():
    """Recursive per-effective-proof gas is outer / batch-size."""
    expected = gb.RECURSIVE_STARK_OUTER_GAS_PER_PROOF // gb.RECURSIVE_STARK_BATCH_PROOFS
    assert gb.per_proof_gas("recursive-stark-wrapper") == expected


def test_per_proof_gas_rejects_unknown_configuration():
    with pytest.raises(AssertionError):
        gb.per_proof_gas("unknown-config")


# ---- per_batch_gas and per_effective_proof_gas ------------------------


def test_per_batch_gas_legacy_scales_linearly():
    """Legacy per-batch gas equals per-proof gas times batch size."""
    expected = gb.LEGACY_SHA256_STARK_GAS_PER_PROOF * gb.RECURSIVE_STARK_BATCH_PROOFS
    assert gb.per_batch_gas("legacy-sha256-stark") == expected


def test_per_batch_gas_wider_hash_scales_linearly():
    """Wider-hash per-batch gas equals per-proof gas times batch size."""
    expected = gb.WIDER_HASH_STARK_GAS_PER_PROOF * gb.RECURSIVE_STARK_BATCH_PROOFS
    assert gb.per_batch_gas("wider-hash-stark") == expected


def test_per_batch_gas_recursive_is_one_outer_proof():
    """Recursive per-batch gas is one outer-proof verifier invocation."""
    assert gb.per_batch_gas("recursive-stark-wrapper") == gb.RECURSIVE_STARK_OUTER_GAS_PER_PROOF


def test_per_effective_proof_gas_matches_per_proof_for_non_recursive():
    """Legacy and wider-hash carry no amortization; effective equals per-proof."""
    assert gb.per_effective_proof_gas("legacy-sha256-stark") == gb.LEGACY_SHA256_STARK_GAS_PER_PROOF
    assert gb.per_effective_proof_gas("wider-hash-stark") == gb.WIDER_HASH_STARK_GAS_PER_PROOF


def test_per_effective_proof_gas_recursive_falls_below_legacy():
    """Recursive amortization drops the per-effective-proof cost below legacy."""
    assert gb.per_effective_proof_gas("recursive-stark-wrapper") < gb.LEGACY_SHA256_STARK_GAS_PER_PROOF


# ---- proofs_per_block_max ---------------------------------------------


def test_proofs_per_block_max_legacy_at_default_limit():
    """Legacy: 60_000_000 / 5_000_000 = 12 proofs per block."""
    assert gb.proofs_per_block_max("legacy-sha256-stark") == 12


def test_proofs_per_block_max_wider_hash_at_default_limit():
    """Wider-hash: 60_000_000 / 6_500_000 = 9 proofs per block."""
    assert gb.proofs_per_block_max("wider-hash-stark") == 9


def test_proofs_per_block_max_recursive_amortizes():
    """Recursive: 8 outer proofs per block, each amortizing 100 inner proofs = 800."""
    assert gb.proofs_per_block_max("recursive-stark-wrapper") == 800


def test_proofs_per_block_max_accepts_alternate_gas_limit():
    """Caller can override the per-block gas limit for sensitivity analysis."""
    assert gb.proofs_per_block_max("legacy-sha256-stark", gas_limit=10_000_000) == 2


def test_proofs_per_block_max_rejects_zero_gas_limit():
    with pytest.raises(AssertionError):
        gb.proofs_per_block_max("legacy-sha256-stark", gas_limit=0)


# ---- factor_vs_legacy --------------------------------------------------


def test_factor_vs_legacy_for_legacy_is_one():
    """Legacy per-effective-proof gas divided by legacy is exactly 1.0."""
    assert gb.factor_vs_legacy("legacy-sha256-stark") == 1.0


def test_factor_vs_legacy_for_wider_hash_is_above_one():
    """Wider-hash sits above legacy because of the wider-hash overhead."""
    assert gb.factor_vs_legacy("wider-hash-stark") > 1.0


def test_factor_vs_legacy_for_recursive_is_below_one():
    """Recursive amortization brings the factor below 1.0."""
    assert gb.factor_vs_legacy("recursive-stark-wrapper") < 1.0


def test_factor_vs_legacy_for_recursive_falls_below_one_tenth():
    """Recursive amortization at batch size 100 drops the factor below 0.1."""
    assert gb.factor_vs_legacy("recursive-stark-wrapper") < 0.1


def test_factor_vs_legacy_for_recursive_pins_to_chapter_value():
    """Recursive factor is exactly 0.014 (70K / 5M); pinned for chapter consistency."""
    assert abs(gb.factor_vs_legacy("recursive-stark-wrapper") - 0.014) < 1e-9


# ---- evaluate() shape -------------------------------------------------


def test_evaluate_returns_eight_keys(configurations):
    """The evaluate dict has the eight pedagogical fields."""
    expected_keys = {
        "configuration",
        "per_proof_gas",
        "per_batch_proof_count",
        "per_batch_gas",
        "per_effective_proof_gas",
        "factor_vs_legacy",
        "proofs_per_block_max",
        "rationale",
    }
    for cfg in configurations:
        out = gb.evaluate(cfg)
        assert set(out.keys()) == expected_keys


def test_evaluate_rationale_is_nonempty(configurations):
    """Every configuration has a one-line rationale."""
    for cfg in configurations:
        out = gb.evaluate(cfg)
        assert isinstance(out["rationale"], str)
        assert len(out["rationale"]) > 0


def test_compare_configurations_returns_three_rows(configurations):
    """The flatten returns one row per configuration in canonical order."""
    rows = gb.compare_configurations()
    assert [r["configuration"] for r in rows] == configurations


# ---- per_rollup_cycle_gas ---------------------------------------------


def test_per_rollup_cycle_gas_legacy_at_default_count():
    """Legacy at 100 proofs per cycle: 100 * 5M = 500M gas per cycle."""
    expected = 100 * gb.LEGACY_SHA256_STARK_GAS_PER_PROOF
    assert gb.per_rollup_cycle_gas("legacy-sha256-stark") == expected


def test_per_rollup_cycle_gas_recursive_at_default_count_is_one_outer_proof():
    """Recursive at 100 proofs per cycle: one outer-proof verifier invocation."""
    assert gb.per_rollup_cycle_gas("recursive-stark-wrapper") == gb.RECURSIVE_STARK_OUTER_GAS_PER_PROOF


def test_per_rollup_cycle_gas_recursive_above_batch_size_uses_two_outer_proofs():
    """Recursive at 150 proofs per cycle: two outer proofs (100 + 50)."""
    assert gb.per_rollup_cycle_gas("recursive-stark-wrapper", cycle_proof_count=150) == 2 * gb.RECURSIVE_STARK_OUTER_GAS_PER_PROOF


def test_per_rollup_cycle_gas_rejects_negative_count():
    with pytest.raises(AssertionError):
        gb.per_rollup_cycle_gas("legacy-sha256-stark", cycle_proof_count=-1)


def test_per_rollup_cycle_gas_at_zero_count_is_zero_for_non_recursive():
    """Zero proofs per cycle costs zero gas under non-recursive configurations."""
    assert gb.per_rollup_cycle_gas("legacy-sha256-stark", cycle_proof_count=0) == 0
    assert gb.per_rollup_cycle_gas("wider-hash-stark", cycle_proof_count=0) == 0


def test_per_rollup_cycle_gas_at_zero_count_is_zero_for_recursive():
    """Zero proofs per cycle costs zero gas under the recursive wrapper too."""
    assert gb.per_rollup_cycle_gas("recursive-stark-wrapper", cycle_proof_count=0) == 0


# ---- Gas anchors the chapter prints, pinned exactly --------------------
#
# WIDER_HASH_STARK_GAS_PER_PROOF was reached only through a ">" comparison
# and a floor division, so it could move from 6.5M to 6.6M with the whole
# suite green while the chapter's printed 1.300 factor and its "roughly
# thirty percent" prose both went wrong. This is the Ch 37 defect: a
# constant asserted only inside a ratio.


def test_wider_hash_per_proof_gas_is_six_point_five_million():
    """Pinned exactly; the chapter's 1.300 factor is computed from it."""
    assert gb.WIDER_HASH_STARK_GAS_PER_PROOF == 6_500_000


def test_recursive_outer_per_proof_gas_is_seven_million():
    """Pinned exactly; Block 2 prints 70,000 as 7M // 100."""
    assert gb.RECURSIVE_STARK_OUTER_GAS_PER_PROOF == 7_000_000


def test_factor_vs_legacy_for_wider_hash_pins_to_chapter_value():
    """The chapter, its figure and Appendix D all print 1.30."""
    assert abs(gb.factor_vs_legacy("wider-hash-stark") - 1.3) < 1e-9


def test_default_rollup_cycle_proofs_is_one_hundred():
    """The chapter's per-cycle worked example is 100 proofs per commitment."""
    assert gb.DEFAULT_ROLLUP_CYCLE_PROOFS == 100


# ---- evaluate() rationale, per configuration --------------------------

RATIONALE_TOKENS = {
    "legacy-sha256-stark": "SHA-256 at L4",
    "wider-hash-stark": "wider-output Fiat-Shamir",
    "recursive-stark-wrapper": "amortization",
}


def test_evaluate_rationale_names_its_own_configuration():
    """Each envelope's rationale explains that configuration and no other."""
    for cfg, token in RATIONALE_TOKENS.items():
        assert token in gb.evaluate(cfg)["rationale"], cfg


def test_evaluate_rationale_tokens_are_unique():
    """The uniqueness half: no token matches two configurations."""
    rationales = [r["rationale"] for r in gb.compare_configurations()]
    for token in RATIONALE_TOKENS.values():
        assert sum(token in r for r in rationales) == 1, token
