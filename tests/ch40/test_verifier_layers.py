"""Tests for the four-layer verifier-contract decomposition matrix."""

import pytest

from zk_rollups import verifier_layers as vl


# ---- Layer and candidate constants ------------------------------------


def test_layers_match_ch31_decomposition(layers):
    """The LAYERS tuple matches the Ch 31 four-layer decomposition."""
    assert list(vl.LAYERS) == layers


def test_layer_count_is_four():
    """Exactly four layers per the Ch 31 decomposition."""
    assert len(vl.LAYERS) == 4


def test_l2_commitment_candidates_match_ch32(l2_commitment_candidates):
    """L2 commitment candidate set matches Ch 32's PQ-secure analysis."""
    assert list(vl.CANDIDATES_BY_LAYER["L2-commitment"]) == l2_commitment_candidates


def test_l4_fiat_shamir_candidates_match_ch33(l4_fiat_shamir_candidates):
    """L4 Fiat-Shamir candidate set covers SHA-256 through Keccak-256."""
    assert list(vl.CANDIDATES_BY_LAYER["L4-fiat-shamir"]) == l4_fiat_shamir_candidates


def test_l1_carries_three_arithmetization_candidates():
    """L1 arithmetization: AIR, R1CS, Plonkish."""
    assert list(vl.CANDIDATES_BY_LAYER["L1-arithmetization"]) == [
        "AIR",
        "R1CS",
        "Plonkish",
    ]


def test_l3_carries_three_protocol_logic_candidates():
    """L3 protocol logic: Sumcheck-IOP, FRI-IOP, IPA-IOP."""
    assert list(vl.CANDIDATES_BY_LAYER["L3-protocol-logic"]) == [
        "Sumcheck-IOP",
        "FRI-IOP",
        "IPA-IOP",
    ]


# ---- Lookup behavior --------------------------------------------------


def test_lookup_returns_five_keys():
    """The lookup result has the five pedagogical fields."""
    out = vl.lookup("L2-commitment", "FRI")
    assert set(out.keys()) == {
        "layer",
        "candidate",
        "pq_status",
        "deployment_status",
        "rationale",
    }


def test_lookup_kzg_is_shor_broken():
    """KZG binding reduces to d-SDH; Shor breaks it."""
    out = vl.lookup("L2-commitment", "KZG")
    assert out["pq_status"] == "shor-broken"


def test_lookup_fri_is_grover_weakened():
    """FRI inherits Grover-weakening through the Merkle hash."""
    out = vl.lookup("L2-commitment", "FRI")
    assert out["pq_status"] == "grover-weakened"


def test_lookup_lattice_pcs_is_pq_secure():
    """Lattice PCS is the only L2 commitment candidate without a quantum speedup."""
    out = vl.lookup("L2-commitment", "lattice-PCS")
    assert out["pq_status"] == "pq-secure"
    assert out["deployment_status"] == "pq-research"


def test_lookup_l1_candidates_are_off_chain():
    """L1 arithmetization is off-chain in the prover; no on-chain decision."""
    for candidate in vl.CANDIDATES_BY_LAYER["L1-arithmetization"]:
        assert vl.lookup("L1-arithmetization", candidate)["pq_status"] == "off-chain"


def test_lookup_l4_candidates_are_grover_weakened():
    """Every L4 hash candidate is grover-weakened (no PQ-secure hash on-chain)."""
    for candidate in vl.CANDIDATES_BY_LAYER["L4-fiat-shamir"]:
        assert vl.lookup("L4-fiat-shamir", candidate)["pq_status"] == "grover-weakened"


def test_lookup_ipa_iop_is_shor_broken():
    """IPA-IOP soundness reduces to discrete log; Shor breaks it."""
    out = vl.lookup("L3-protocol-logic", "IPA-IOP")
    assert out["pq_status"] == "shor-broken"


def test_lookup_rejects_unknown_layer():
    with pytest.raises(AssertionError):
        vl.lookup("unknown-layer", "AIR")


def test_lookup_rejects_candidate_not_in_layer():
    """KZG is an L2 candidate; it cannot be queried at L4."""
    with pytest.raises(AssertionError):
        vl.lookup("L4-fiat-shamir", "KZG")


# ---- candidates_with_status -------------------------------------------


def test_shor_broken_set_includes_kzg_and_ipa():
    """KZG (L2) and IPA-IOP (L3) are the two Shor-broken cells."""
    cells = vl.candidates_with_status("shor-broken")
    assert ("L2-commitment", "KZG") in cells
    assert ("L3-protocol-logic", "IPA-IOP") in cells


def test_pq_secure_set_includes_lattice_pcs():
    """Lattice PCS is the only pq-secure cell at chain-tip 2026."""
    cells = vl.candidates_with_status("pq-secure")
    assert ("L2-commitment", "lattice-PCS") in cells
    assert len(cells) == 1


def test_grover_weakened_set_includes_every_l4_candidate(l4_fiat_shamir_candidates):
    """Every L4 hash candidate sits in the grover-weakened set."""
    cells = vl.candidates_with_status("grover-weakened")
    for candidate in l4_fiat_shamir_candidates:
        assert ("L4-fiat-shamir", candidate) in cells


def test_off_chain_set_contains_every_l1_candidate():
    """L1 arithmetization candidates are all off-chain (no on-chain decision)."""
    cells = vl.candidates_with_status("off-chain")
    for candidate in vl.CANDIDATES_BY_LAYER["L1-arithmetization"]:
        assert ("L1-arithmetization", candidate) in cells


def test_candidates_with_status_rejects_unknown_status():
    with pytest.raises(AssertionError):
        vl.candidates_with_status("unknown-status")


# ---- deployment_summary order and shape -------------------------------


def test_deployment_summary_visits_every_cell():
    """The flatten covers L1 through L4 candidates in order."""
    rows = vl.deployment_summary()
    expected = sum(
        len(vl.CANDIDATES_BY_LAYER[layer]) for layer in vl.LAYERS
    )
    assert len(rows) == expected


def test_deployment_summary_layer_order_matches_layers_constant():
    """Layer order in the flatten matches the LAYERS tuple order."""
    rows = vl.deployment_summary()
    last_layer_index = -1
    layer_to_index = {layer: i for i, layer in enumerate(vl.LAYERS)}
    for row in rows:
        idx = layer_to_index[row["layer"]]
        assert idx >= last_layer_index
        last_layer_index = idx


def test_deployment_summary_is_deterministic():
    """Repeated invocations produce the same row order."""
    rows1 = vl.deployment_summary()
    rows2 = vl.deployment_summary()
    assert [(r["layer"], r["candidate"]) for r in rows1] == [
        (r["layer"], r["candidate"]) for r in rows2
    ]


# ---- system_profile for the production-system anchors -----------------


def test_zksync_profile_carries_plonkish_l1():
    """ZKsync Boojum uses Plonkish arithmetization at L1."""
    profile = vl.system_profile("ZKsync-Era-Boojum")
    assert profile["layers"]["L1-arithmetization"]["candidate"] == "Plonkish"


def test_zksync_profile_carries_fri_l2():
    """ZKsync Boojum uses FRI at L2."""
    profile = vl.system_profile("ZKsync-Era-Boojum")
    assert profile["layers"]["L2-commitment"]["candidate"] == "FRI"


def test_starknet_profile_carries_air_l1():
    """Starknet ethSTARK uses AIR arithmetization at L1."""
    profile = vl.system_profile("Starknet-ethSTARK")
    assert profile["layers"]["L1-arithmetization"]["candidate"] == "AIR"


def test_starknet_profile_carries_fri_l2():
    """Starknet ethSTARK uses FRI at L2."""
    profile = vl.system_profile("Starknet-ethSTARK")
    assert profile["layers"]["L2-commitment"]["candidate"] == "FRI"


def test_both_anchors_carry_sha256_at_l4():
    """Both production anchors deploy SHA-256 at L4 at chain-tip 2026."""
    for system in ("ZKsync-Era-Boojum", "Starknet-ethSTARK"):
        profile = vl.system_profile(system)
        assert profile["layers"]["L4-fiat-shamir"]["candidate"] == "SHA-256"


def test_system_profile_includes_citation_key():
    """Each production anchor carries a citable cite key for book.bib."""
    for system in ("ZKsync-Era-Boojum", "Starknet-ethSTARK"):
        profile = vl.system_profile(system)
        assert isinstance(profile["citation_key"], str)
        assert len(profile["citation_key"]) > 0


def test_system_profile_inner_only_flag_is_set():
    """system_profile reports inner_only=True so callers cannot misread the scope.

    The data model captures the inner four-layer decomposition only; the outer
    pairing wrapper claim (ZKsync) is engineering inference per the Ch 35 hedge
    and sits outside the model. The inner_only and outer_wrapper_note keys are
    the data-model-side hedge that mirrors the docstring.
    """
    for system in ("ZKsync-Era-Boojum", "Starknet-ethSTARK"):
        profile = vl.system_profile(system)
        assert profile["inner_only"] is True
        assert isinstance(profile["outer_wrapper_note"], str)
        assert len(profile["outer_wrapper_note"]) > 0


def test_system_profile_rejects_unknown_system():
    with pytest.raises(AssertionError):
        vl.system_profile("unknown-rollup")


# ---- Per-cell label fields ---------------------------------------------
#
# Every cell's rationale and deployment_status is prose that the chapter
# quotes and that nothing else asserted on, so all fourteen rationales and
# thirteen of the fourteen deployment_status values were freely permutable
# with the suite green. Each test below pairs a per-cell assertion with a
# uniqueness check, so the per-cell one cannot be satisfied by two cells
# sharing a token.

RATIONALE_TOKENS = {
    ("L1-arithmetization", "AIR"): "STARK-style",
    ("L1-arithmetization", "R1CS"): "Groth16",
    ("L1-arithmetization", "Plonkish"): "Halo 2",
    ("L2-commitment", "KZG"): "d-SDH",
    ("L2-commitment", "FRI"): "proximity gap",
    ("L2-commitment", "Merkle"): "vector commitment",
    ("L2-commitment", "lattice-PCS"): "Module-SIS",
    ("L3-protocol-logic", "Sumcheck-IOP"): "information-theoretic",
    ("L3-protocol-logic", "FRI-IOP"): "layered over Merkle",
    ("L3-protocol-logic", "IPA-IOP"): "inner-product argument",
    ("L4-fiat-shamir", "SHA-256"): "~85 bits",
    ("L4-fiat-shamir", "SHAKE-128"): "128-bit security",
    ("L4-fiat-shamir", "SHAKE-256"): "conservative-assumption",
    ("L4-fiat-shamir", "Keccak-256"): "native EVM opcode",
}


def test_every_cell_rationale_names_its_own_cell():
    """Each cell's rationale carries a token specific to that cell."""
    for (layer, candidate), token in RATIONALE_TOKENS.items():
        rationale = vl.lookup(layer, candidate)["rationale"]
        assert token in rationale, f"{layer}/{candidate} lost {token!r}"


def test_rationale_tokens_are_unique_across_the_matrix():
    """No token matches two cells, so the per-cell test cannot be gamed."""
    rationales = [r["rationale"] for r in vl.deployment_summary()]
    for token in RATIONALE_TOKENS.values():
        hits = [r for r in rationales if token in r]
        assert len(hits) == 1, f"{token!r} matches {len(hits)} cells"


def test_every_cell_rationale_is_distinct():
    """Fourteen cells, fourteen distinct rationales."""
    rationales = [r["rationale"] for r in vl.deployment_summary()]
    assert len(rationales) == 14
    assert len(set(rationales)) == 14


def test_deployment_status_is_pinned_per_cell():
    """SHA-256 is the legacy default and lattice-PCS the research cell.

    The other twelve are production. Pinning each one is what stops the
    chapter's "legacy default" and "research-to-early-adoption" columns
    from swapping into any other cell.
    """
    for row in vl.deployment_summary():
        key = (row["layer"], row["candidate"])
        if key == ("L4-fiat-shamir", "SHA-256"):
            assert row["deployment_status"] == "legacy"
        elif key == ("L2-commitment", "lattice-PCS"):
            assert row["deployment_status"] == "pq-research"
        else:
            assert row["deployment_status"] == "production", key


def test_exactly_one_legacy_and_one_research_cell():
    """The uniqueness half: neither label may spread to a second cell."""
    statuses = [r["deployment_status"] for r in vl.deployment_summary()]
    assert statuses.count("legacy") == 1
    assert statuses.count("pq-research") == 1
    assert statuses.count("production") == 12
