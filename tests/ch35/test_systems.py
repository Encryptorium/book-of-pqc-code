"""The six deployed configurations, pinned one at a time.

Three of these six share a grid cell and three more share another, so a table
that permuted rows within a cell would still classify correctly. Every test
below names one system and asserts the facts that distinguish it, which is
what a shape-only test cannot do.
"""

import pytest

from zk_case_studies.margins import query_miss_bits
from zk_case_studies.systems import SYSTEMS, STWO_DEFAULTS, names, posture


def test_the_chapter_walks_exactly_six_configurations():
    assert names() == ["sapling", "orchard", "boojum_outer", "boojum_inner",
                       "ethstark", "stwo"]


@pytest.mark.parametrize("key,l2,l4,detail_fragment", [
    ("sapling", "pairing", "crs", "BLS12-381"),
    ("orchard", "ipa_dlp", "fs_over_dlp", "Pallas and Vesta"),
    ("boojum_outer", "pairing", "crs", "wrapper"),
    ("boojum_inner", "fri", "fs_tier3_classical_rom", "Goldilocks"),
    ("ethstark", "fri", "fs_tier3_classical_rom", "61-bit prime"),
    ("stwo", "fri", "fs_tier3_classical_rom", "Mersenne-31"),
])
def test_each_system_carries_its_own_layers_and_its_own_primitive(
        key, l2, l4, detail_fragment):
    record = SYSTEMS[key]
    assert record["l2"] == l2
    assert record["l4"] == l4
    assert detail_fragment in record["detail"]


def test_no_two_systems_share_a_detail_string():
    # The detail field is what separates configurations inside one cell, so
    # a duplicate would reintroduce exactly the permutability it exists to
    # remove.
    details = [record["detail"] for record in SYSTEMS.values()]
    assert len(set(details)) == len(details)


def test_the_curves_are_not_interchangeable_between_the_two_zcash_pools():
    assert "BLS12-381" in SYSTEMS["sapling"]["detail"]
    assert "BLS12-381" not in SYSTEMS["orchard"]["detail"]
    assert "Pallas" in SYSTEMS["orchard"]["detail"]
    assert "Pallas" not in SYSTEMS["sapling"]["detail"]


def test_the_three_fri_systems_name_three_different_base_fields():
    fields = [SYSTEMS[k]["detail"] for k in ("boojum_inner", "ethstark", "stwo")]
    assert len(set(fields)) == 3
    assert "Goldilocks" in fields[0]
    assert "Mersenne-31" in fields[2]


@pytest.mark.parametrize("key,expected", [
    ("sapling", "red"),
    ("orchard", "red"),
    ("boojum_outer", "red"),
    ("boojum_inner", "amber"),
    ("ethstark", "amber"),
    ("stwo", "amber"),
])
def test_each_system_takes_the_posture_the_chapter_reports(key, expected):
    assert posture(key)["posture"] == expected


def test_the_printed_listing_order_reproduces_the_chapters_output():
    printed = ["sapling", "orchard", "boojum_outer", "boojum_inner", "ethstark"]
    assert [posture(k)["posture"] for k in printed] == [
        "red", "red", "red", "amber", "amber"]


def test_transition_scope_follows_the_posture():
    # Red cells need replacement; amber cells are reparameterizable. That
    # correspondence is the operator-facing claim of Table 35.3.
    for key in names():
        result = posture(key)
        if result["posture"] == "red":
            assert result["transition"] == "replacement"
        else:
            assert result["transition"] == "parameter bumps"


def test_posture_rejects_an_unknown_system():
    with pytest.raises(ValueError):
        posture("aleo")


def test_stwo_defaults_are_the_published_triple():
    assert STWO_DEFAULTS == {"n_queries": 70, "pow_bits": 26, "log_blowup": 1}


def test_stwo_defaults_reach_ninety_six_bits_only_under_the_capacity_bound():
    assert query_miss_bits(**STWO_DEFAULTS, regime="capacity") == 96.0
    assert query_miss_bits(**STWO_DEFAULTS, regime="johnson") == 61.0
    gap = (query_miss_bits(**STWO_DEFAULTS, regime="capacity")
           - query_miss_bits(**STWO_DEFAULTS, regime="johnson"))
    assert gap == pytest.approx(35.0)


def test_every_system_carries_a_label_naming_its_project_and_component():
    labels = {key: posture(key)["label"] for key in names()}
    assert labels["sapling"] == "Zcash Sapling"
    assert labels["orchard"] == "Zcash Orchard"
    assert labels["boojum_outer"] == "ZKsync Era outer wrapper"
    assert labels["boojum_inner"] == "ZKsync Era inner"
    assert labels["ethstark"] == "Starknet ethSTARK / Stone (legacy)"
    assert labels["stwo"] == "Starknet Stwo (current)"
    assert len(set(labels.values())) == len(labels)
