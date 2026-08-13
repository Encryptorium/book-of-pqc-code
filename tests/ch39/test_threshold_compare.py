"""Tests for the threshold-scheme by candidate support matrix."""

import pytest

from consensus_staking import threshold_compare as tc


# ---- Constant-and-shape tests -----------------------------------------


def test_primitives_match_aggregation_overhead(primitives):
    """The threshold matrix carries the same five candidates as aggregation_overhead."""
    assert set(tc.PRIMITIVES) == set(primitives)
    assert tc.PRIMITIVES == tuple(primitives)


def test_threshold_roles_match_fixture(threshold_roles):
    """The three role labels match the chapter's fixed taxonomy."""
    assert tc.THRESHOLD_ROLES == tuple(threshold_roles)


def test_matrix_covers_every_pair(primitives, threshold_roles):
    """Every (primitive, role) pair has a cell."""
    for p in primitives:
        for r in threshold_roles:
            assert r in tc.MATRIX[p]


# ---- lookup() shape tests ---------------------------------------------


def test_lookup_returns_six_keys(primitives, threshold_roles):
    """The lookup dict carries the six pedagogical fields."""
    expected = {
        "primitive",
        "role",
        "deployment_status",
        "admits_t_of_n",
        "requires_combine_round",
        "rationale",
    }
    for p in primitives:
        for r in threshold_roles:
            cell = tc.lookup(p, r)
            assert set(cell.keys()) == expected


def test_lookup_rejects_unknown_primitive():
    with pytest.raises(AssertionError):
        tc.lookup("unknown-primitive", "no-threshold")


def test_lookup_rejects_unknown_role():
    with pytest.raises(AssertionError):
        tc.lookup("ML-DSA-65", "unknown-role")


# ---- Per-cell load-bearing facts --------------------------------------


def test_bls_no_threshold_is_production():
    """BLS no-threshold cell records the deployed Ethereum baseline."""
    cell = tc.lookup("BLS-BLS12-381", "no-threshold")
    assert cell["deployment_status"] == "production"
    assert cell["requires_combine_round"] is False


def test_bls_threshold_pq_is_incompatible():
    """A threshold-PQ variant of BLS is not a research direction."""
    cell = tc.lookup("BLS-BLS12-381", "threshold-PQ")
    assert cell["deployment_status"] == "incompatible"


def test_classical_frost_is_shor_vulnerable_for_bls():
    """FROST is threshold Schnorr; classical-only and Shor-vulnerable."""
    cell = tc.lookup("BLS-BLS12-381", "classical-FROST")
    assert cell["deployment_status"] == "research-classical-only"


def test_classical_frost_is_incompatible_with_lattice_and_hash():
    """FROST does not transfer to lattice or hash-based primitives."""
    for primitive in ("ML-DSA-65", "SLH-DSA-128s", "FN-DSA-512", "threshold-ML-DSA"):
        cell = tc.lookup(primitive, "classical-FROST")
        assert cell["deployment_status"] == "incompatible"


def test_ml_dsa_no_threshold_is_fips_final():
    """ML-DSA-65 plain mode is FIPS 204 final."""
    cell = tc.lookup("ML-DSA-65", "no-threshold")
    assert cell["deployment_status"] == "fips-final"


def test_slh_dsa_no_threshold_is_fips_final():
    """SLH-DSA-128s plain mode is FIPS 205 final."""
    cell = tc.lookup("SLH-DSA-128s", "no-threshold")
    assert cell["deployment_status"] == "fips-final"


def test_fn_dsa_no_threshold_is_pre_draft():
    """FN-DSA-512 plain mode sits ahead of any published FIPS 206 document.

    ``pre-draft`` rather than ``fips-ipd``: FIPS 206 has released no
    initial public draft, so there is no draft standard to be at.
    """
    cell = tc.lookup("FN-DSA-512", "no-threshold")
    assert cell["deployment_status"] == "pre-draft"


def test_threshold_pq_statuses_are_pinned_per_primitive():
    """The threshold-PQ column's maturity labels, pinned by identity.

    Only two of the five cells in this column were pinned before this
    test (BLS as incompatible, threshold-ML-DSA as research-grade), so
    ML-DSA-65, SLH-DSA-128s and FN-DSA-512 could trade labels freely.
    The research-grade against research-early distinction is what the
    chapter's "the hypertree authentication path and the
    Gaussian-sampling step resist the standard threshold-protocol
    techniques" rests on, so a swap would contradict the prose while
    the suite stayed green.
    """
    expected = {
        "BLS-BLS12-381": "incompatible",
        "ML-DSA-65": "research-grade",
        "SLH-DSA-128s": "research-early",
        "FN-DSA-512": "research-early",
        "threshold-ML-DSA": "research-grade",
    }
    actual = {
        p: tc.lookup(p, "threshold-PQ")["deployment_status"] for p in tc.PRIMITIVES
    }
    assert actual == expected


def test_every_rationale_names_the_cell_it_belongs_to():
    """Each of the fifteen rationales carries a token unique to its cell.

    ``rationale`` is the only field that separates the cells the status
    and the two flags leave identical: nine of the fifteen cells read
    ``incompatible`` or share a research label with another cell. It is
    also the field ``lookup`` returns for the chapter to quote, and
    nothing asserted on it, so any two rationales could trade places.
    """
    tokens = {
        ("BLS-BLS12-381", "no-threshold"): "beacon-chain baseline",
        ("BLS-BLS12-381", "classical-FROST"): "not a post-quantum migration target",
        ("BLS-BLS12-381", "threshold-PQ"): "already collapses partials",
        ("ML-DSA-65", "no-threshold"): "FIPS 204 final",
        ("ML-DSA-65", "classical-FROST"): "Schnorr-style identification protocol",
        ("ML-DSA-65", "threshold-PQ"): "none NIST-standardized",
        ("SLH-DSA-128s", "no-threshold"): "FIPS 205 final",
        ("SLH-DSA-128s", "classical-FROST"): "hash-based signatures do not admit",
        ("SLH-DSA-128s", "threshold-PQ"): "hypertree signatures",
        ("FN-DSA-512", "no-threshold"): "FIPS 206 under development",
        ("FN-DSA-512", "classical-FROST"): "FROST framework does not transfer",
        ("FN-DSA-512", "threshold-PQ"): "Gaussian-sampling distributed protocols",
        ("threshold-ML-DSA", "no-threshold"): "degenerates to plain ML-DSA-65",
        ("threshold-ML-DSA", "classical-FROST"): "right combinator",
        ("threshold-ML-DSA", "threshold-PQ"): "candidate slot",
    }
    assert len(tokens) == len(tc.PRIMITIVES) * len(tc.THRESHOLD_ROLES)
    for (primitive, role), token in tokens.items():
        assert token in tc.lookup(primitive, role)["rationale"]
    for token in tokens.values():
        hits = [
            (p, r)
            for p in tc.PRIMITIVES
            for r in tc.THRESHOLD_ROLES
            if token in tc.lookup(p, r)["rationale"]
        ]
        assert len(hits) == 1


def test_every_threshold_pq_cell_admits_t_of_n_and_requires_combine():
    """Every research-grade threshold-PQ cell admits T-of-N and requires a combine round."""
    for primitive in ("ML-DSA-65", "SLH-DSA-128s", "FN-DSA-512", "threshold-ML-DSA"):
        cell = tc.lookup(primitive, "threshold-PQ")
        assert cell["admits_t_of_n"] is True
        assert cell["requires_combine_round"] is True


def test_threshold_ml_dsa_is_the_canonical_threshold_pq_slot():
    """threshold-ML-DSA's threshold-PQ cell is the canonical research-grade slot."""
    cell = tc.lookup("threshold-ML-DSA", "threshold-PQ")
    assert cell["deployment_status"] == "research-grade"
    assert cell["admits_t_of_n"] is True


# ---- deployment_summary() -----------------------------------------------


def test_deployment_summary_lists_fifteen_cells(primitives, threshold_roles):
    """Five primitives times three roles equals fifteen cells."""
    out = tc.deployment_summary()
    assert len(out) == len(primitives) * len(threshold_roles)


def test_deployment_summary_iterates_in_primitives_then_roles_order(primitives, threshold_roles):
    """The summary order is primitives outer, roles inner."""
    out = tc.deployment_summary()
    expected_pairs = [(p, r) for p in primitives for r in threshold_roles]
    actual_pairs = [(cell["primitive"], cell["role"]) for cell in out]
    assert actual_pairs == expected_pairs


def test_production_ready_at_no_threshold_returns_only_bls():
    """At chain-tip 2026 only BLS no-threshold is production-deployed."""
    out = tc.production_ready_at("no-threshold")
    assert out == ["BLS-BLS12-381"]


def test_production_ready_at_threshold_pq_is_empty():
    """At chain-tip 2026 no production threshold-PQ deployment exists."""
    out = tc.production_ready_at("threshold-PQ")
    assert out == []


def test_production_ready_rejects_unknown_role():
    with pytest.raises(AssertionError):
        tc.production_ready_at("unknown-role")
