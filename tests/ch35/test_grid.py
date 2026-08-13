"""The (L2, L4) grid and its dominance rule."""

import pytest

from zk_case_studies.grid import (
    L2_COLORS,
    L4_COLORS,
    ORDER,
    classify,
    dominant_color,
)


def test_every_l2_class_carries_the_colour_the_chapter_assigns_it():
    assert L2_COLORS == {"pairing": "red", "ipa_dlp": "red",
                         "fri": "amber", "lattice_pcs": "amber"}


def test_every_l4_class_carries_the_colour_the_chapter_assigns_it():
    assert L4_COLORS == {"crs": "red", "fs_over_dlp": "red",
                         "fs_tier1": "amber", "fs_tier2": "amber",
                         "fs_tier3_classical_rom": "amber"}


def test_severity_order_runs_red_then_amber_then_green():
    assert ORDER["red"] < ORDER["amber"] < ORDER["green"]


def test_dominance_takes_the_more_severe_colour_in_both_orders():
    for pair in (("red", "amber"), ("red", "green"), ("amber", "green")):
        assert dominant_color(*pair) == pair[0]
        assert dominant_color(*reversed(pair)) == pair[0]


def test_a_green_layer_never_rescues_a_red_one():
    # This is the rule Figure 35.1 originally contradicted by painting its
    # green-L2 cells green regardless of the L4 row above them.
    assert dominant_color("green", "red") == "red"
    assert dominant_color("green", "amber") == "amber"


def test_dominance_rejects_an_unknown_colour_and_an_empty_call():
    with pytest.raises(ValueError):
        dominant_color("red", "purple")
    with pytest.raises(ValueError):
        dominant_color()


def test_sapling_lands_red_by_the_pairing_route():
    result = classify({"l2": "pairing", "l4": "crs"})
    assert result["cell"] == ("red", "red")
    assert result["posture"] == "red"
    assert result["cnfl_route"].startswith("pairing forward forgery")


def test_orchard_lands_red_by_the_discrete_log_route_not_the_pairing_one():
    # Same verdict as Sapling, different cryptographic route. A classifier
    # that returned the pairing wording here would erase the distinction the
    # Zcash case study is built on.
    result = classify({"l2": "ipa_dlp", "l4": "fs_over_dlp"})
    assert result["cell"] == ("red", "red")
    assert result["posture"] == "red"
    assert result["cnfl_route"].startswith("DLP forward forgery")


def test_a_fri_system_lands_amber_with_the_qrom_pending_route():
    result = classify({"l2": "fri", "l4": "fs_tier3_classical_rom"})
    assert result["cell"] == ("amber", "amber")
    assert result["posture"] == "amber"
    assert "QROM-pending" in result["cnfl_route"]
    assert "forgery" not in result["cnfl_route"]


def test_a_composite_reads_by_its_weakest_layer():
    # An amber L2 under a red L4 is dominant red: the wrapper is what the
    # on-chain verifier reads first.
    assert classify({"l2": "fri", "l4": "crs"})["posture"] == "red"
    assert classify({"l2": "pairing",
                     "l4": "fs_tier3_classical_rom"})["posture"] == "red"


def test_classify_rejects_missing_keys_and_unknown_values():
    with pytest.raises(ValueError):
        classify({"l2": "pairing"})
    with pytest.raises(ValueError):
        classify({"l4": "crs"})
    with pytest.raises(ValueError):
        classify({"l2": "bulletproofs", "l4": "crs"})
    with pytest.raises(ValueError):
        classify({"l2": "pairing", "l4": "fs_tier9"})
