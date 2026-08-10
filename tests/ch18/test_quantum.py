"""Generic attack exponents, and the Part III comparison the chapter prints.

The comparison table in the chapter is written as literals. Deriving the same
rows from the cost functions is what turns those literals into something a test
can hold, so a later edit to one row cannot drift away from the model.
"""

import pytest

from hash_cryptanalysis.quantum import (
    bht_collision_bits,
    birthday_collision_bits,
    classical_preimage_bits,
    grover_preimage_bits,
)


WIDTHS = [128, 192, 256]

#: The chapter's Grover/BHT table: n_bits -> (classical_pre, grover, birthday, bht).
PRINTED_COST_TABLE = {
    128: (128, 64, 64, 42.7),
    192: (192, 96, 96, 64.0),
    256: (256, 128, 128, 85.3),
}

#: The chapter's Part III comparison, floored to integers as printed there.
PRINTED_COMPARISON = {
    "Lamport+Merkle (n=32)": (256, 128, 128, 85),
    "WOTS+/XMSS (n=32)": (256, 128, 128, 85),
    "SLH-DSA-128s": (128, 64, 64, 42),
    "SLH-DSA-192s": (192, 96, 96, 64),
    "SLH-DSA-256s": (256, 128, 128, 85),
}


@pytest.mark.parametrize("n_bits", WIDTHS)
def test_cost_table_matches_the_chapter(n_bits):
    expected = PRINTED_COST_TABLE[n_bits]
    assert classical_preimage_bits(n_bits) == expected[0]
    assert grover_preimage_bits(n_bits) == expected[1]
    assert birthday_collision_bits(n_bits) == expected[2]
    assert round(bht_collision_bits(n_bits), 1) == expected[3]


@pytest.mark.parametrize("n_bits", WIDTHS)
def test_grover_halves_the_classical_preimage_exponent(n_bits):
    assert grover_preimage_bits(n_bits) == classical_preimage_bits(n_bits) / 2


@pytest.mark.parametrize("n_bits", WIDTHS)
def test_birthday_and_grover_coincide_numerically(n_bits):
    """Two unrelated square roots landing on the same exponent, not one mechanism."""
    assert birthday_collision_bits(n_bits) == grover_preimage_bits(n_bits)


@pytest.mark.parametrize("n_bits", WIDTHS)
def test_bht_is_the_smallest_exponent_of_the_four(n_bits):
    """BHT is cheapest in the query model and is still not the binding constraint."""
    others = (
        classical_preimage_bits(n_bits),
        grover_preimage_bits(n_bits),
        birthday_collision_bits(n_bits),
    )
    assert bht_collision_bits(n_bits) < min(others)


@pytest.mark.parametrize("scheme", sorted(PRINTED_COMPARISON))
def test_part_iii_comparison_row_derives_from_the_cost_model(scheme):
    """Every row of the chapter's comparison follows from n alone."""
    expected = PRINTED_COMPARISON[scheme]
    n_bits = expected[0]
    derived = (
        int(classical_preimage_bits(n_bits)),
        int(grover_preimage_bits(n_bits)),
        int(birthday_collision_bits(n_bits)),
        int(bht_collision_bits(n_bits)),
    )
    assert derived == expected


def test_category_floors_track_grover_not_bht():
    """The category floors are 64, 96, 128: Grover preimage, not BHT collision."""
    for n_bits, floor in ((128, 64), (192, 96), (256, 128)):
        assert grover_preimage_bits(n_bits) == floor
        assert bht_collision_bits(n_bits) < floor
