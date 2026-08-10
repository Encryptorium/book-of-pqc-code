"""Tests for the full ML-KEM estimator table.

The three-row estimate for ML-KEM-512, ML-KEM-768, and ML-KEM-1024
must reproduce the Kyber Round 3 submission Table 4 (page 21) within
the block-size tolerance set by the chapter's locked design decision.
"""

from __future__ import annotations

import pytest

from cryptanalysis.estimator import (
    ML_KEM_PARAMETER_SETS,
    CoreSVPEstimate,
    estimate_parameter_set,
    ml_kem_table,
)


# Kyber Round 3 submission Table 4, page 21, primal-only core-SVP
# methodology from Section 5.1.4. Values: (beta, classical, quantum, d).
KYBER_ROUND_3_TABLE_4: dict[str, tuple[int, int, int, int]] = {
    "ML-KEM-512": (406, 118, 107, 999),
    "ML-KEM-768": (626, 183, 166, 1419),
    "ML-KEM-1024": (878, 256, 232, 1885),
}

BETA_TOLERANCE = 5
BIT_TOLERANCE = 3


def test_ml_kem_table_has_three_rows() -> None:
    """The estimator returns one row per ML-KEM parameter set."""
    table = ml_kem_table()
    assert len(table) == 3
    names = [row.name for row in table]
    assert names == ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]


def test_ml_kem_table_is_monotone_in_security_level() -> None:
    """ML-KEM-512 < ML-KEM-768 < ML-KEM-1024 in classical and quantum cost."""
    table = ml_kem_table()
    assert table[0].classical < table[1].classical < table[2].classical
    assert table[0].quantum < table[1].quantum < table[2].quantum
    assert table[0].beta < table[1].beta < table[2].beta


DIMENSION_TOLERANCE = 40  # our m_opt differs from Kyber's for k >= 3.


@pytest.mark.parametrize("row", ML_KEM_PARAMETER_SETS)
def test_parameter_set_matches_published_table(row: tuple) -> None:
    """Each ML-KEM parameter set reproduces Table 4 within tolerance."""
    name, k, n, q, eta_1 = row
    estimate = estimate_parameter_set(name, k, n, q, eta_1)
    published_beta, published_classical, published_quantum, published_d = (
        KYBER_ROUND_3_TABLE_4[name]
    )
    assert abs(estimate.beta - published_beta) <= BETA_TOLERANCE, (
        f"{name}: beta={estimate.beta} vs published {published_beta}, "
        f"gap > {BETA_TOLERANCE}"
    )
    assert abs(estimate.classical - published_classical) <= BIT_TOLERANCE, (
        f"{name}: classical={estimate.classical} vs published "
        f"{published_classical}, gap > {BIT_TOLERANCE}"
    )
    assert abs(estimate.quantum - published_quantum) <= BIT_TOLERANCE, (
        f"{name}: quantum={estimate.quantum} vs published "
        f"{published_quantum}, gap > {BIT_TOLERANCE}"
    )
    # The lattice attack dimension should be close to the published value.
    # Our m_opt differs from Kyber's published m for ML-KEM-768 and
    # ML-KEM-1024, so we allow a looser tolerance on d.
    assert abs(estimate.d - published_d) <= DIMENSION_TOLERANCE, (
        f"{name}: d={estimate.d} vs published {published_d}, "
        f"gap > {DIMENSION_TOLERANCE}"
    )


def test_parameter_set_returns_core_svp_estimate() -> None:
    """The entry point returns a frozen dataclass with the expected fields."""
    estimate = estimate_parameter_set("ML-KEM-768", 3, 256, 3329, 2)
    assert isinstance(estimate, CoreSVPEstimate)
    assert estimate.name == "ML-KEM-768"
    assert estimate.d == estimate.m_opt + 3 * 256 + 1
    assert estimate.beta >= 2
    assert estimate.classical > 0
    assert estimate.quantum > 0


def test_ml_kem_512_beta_is_406() -> None:
    """The exact match on ML-KEM-512 is the regression test anchor."""
    estimate = estimate_parameter_set("ML-KEM-512", 2, 256, 3329, 3)
    assert estimate.beta == 406


def test_printable_three_row_table() -> None:
    """The estimator table is small enough to print in one block."""
    table = ml_kem_table()
    rendered = "\n".join(
        f"{row.name:<12} beta={row.beta:>4}  "
        f"classical={row.classical:>4}  quantum={row.quantum:>4}"
        for row in table
    )
    assert "ML-KEM-512" in rendered
    assert "ML-KEM-768" in rendered
    assert "ML-KEM-1024" in rendered
    assert "406" in rendered
