"""The core-SVP estimator against ML-DSA's Module-LWE instances.

Chapter 13 builds its estimator on ML-KEM and then turns it on the
other flagship of Part II. The published comparison point is the
CRYSTALS-Dilithium Round 3 submission's security table, row
"BKZ block-size b (GSA)" under "LWE Hardness", which reports 423, 624
and 863 for the three parameter sets. That row is the pure geometric
series assumption, which is exactly the model equation 9 states, so
the reproduction here is tighter than on the ML-KEM side where the
published table reports the Kyber security script's basis-shape model
instead.
"""

import pytest

from cryptanalysis.estimator import (
    ML_DSA_PARAMETER_SETS,
    estimate_ml_dsa_set,
    ml_dsa_table,
)

# Dilithium Round 3 submission, "LWE Hardness (Core-SVP and refined)",
# row "BKZ block-size b (GSA)".
PUBLISHED_GSA_BETA = {"ML-DSA-44": 423, "ML-DSA-65": 624, "ML-DSA-87": 863}

# Same table, rows "Classical Core-SVP" and "Quantum Core-SVP".
PUBLISHED_BITS = {
    "ML-DSA-44": (123, 112),
    "ML-DSA-65": (182, 165),
    "ML-DSA-87": (252, 229),
}


@pytest.mark.parametrize("row", ML_DSA_PARAMETER_SETS, ids=lambda r: r[0])
def test_beta_reproduces_the_published_gsa_row(row):
    """Every parameter set lands within one block size of the published beta."""
    estimate = estimate_ml_dsa_set(*row)
    published = PUBLISHED_GSA_BETA[estimate.name]
    assert abs(estimate.beta - published) <= 1


@pytest.mark.parametrize("row", ML_DSA_PARAMETER_SETS, ids=lambda r: r[0])
def test_bit_costs_land_within_the_rounding_effect(row):
    """The bit counts agree to the one bit the rounded exponents cost.

    The chapter uses the headline 0.292 and 0.265; the published table
    uses the unrounded log2(sqrt(3/2)) and log2(sqrt(13/9)). At these
    block sizes that is worth at most one bit.
    """
    estimate = estimate_ml_dsa_set(*row)
    classical, quantum = PUBLISHED_BITS[estimate.name]
    assert abs(estimate.classical - classical) <= 1
    assert abs(estimate.quantum - quantum) <= 1


def test_the_module_is_not_square_so_unknowns_and_samples_differ():
    """ML-DSA-65 has ell = 5 unknowns' worth of rows and k = 6 samples' worth."""
    estimate = estimate_ml_dsa_set("ML-DSA-65", 6, 5, 256, 8380417, 4)
    assert estimate.d == estimate.m_opt + 5 * 256 + 1
    assert estimate.m_opt <= 6 * 256


def test_ml_dsa_65_matches_ml_kem_768_block_size():
    """Both category-3 sets need the same block size under this model."""
    from cryptanalysis.estimator import estimate_parameter_set

    dsa = estimate_ml_dsa_set("ML-DSA-65", 6, 5, 256, 8380417, 4)
    kem = estimate_parameter_set("ML-KEM-768", 3, 256, 3329, 2)
    assert dsa.beta == kem.beta == 624


def test_table_returns_three_rows_in_order():
    table = ml_dsa_table()
    assert [row.name for row in table] == [
        "ML-DSA-44",
        "ML-DSA-65",
        "ML-DSA-87",
    ]
    assert [row.beta for row in table] == sorted(row.beta for row in table)
