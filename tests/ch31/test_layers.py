"""Tests for the four-layer decomposition table of Chapter 31."""

import pytest

from zk_layers.layers import (
    LAYER_KEYS,
    LAYERS,
    POSTURES,
    SYSTEMS,
    hash_bits_for_pq_collision,
    layer_posture,
    thinnest_layer,
)


def test_the_decomposition_has_four_layers_in_order():
    assert LAYER_KEYS == ("L1", "L2", "L3", "L4")


def test_each_layer_carries_its_own_name():
    """Pin each layer key to its own name from Table 31.1.

    Checking only the key set, or only the count, would survive swapping
    the L2 and L3 names, which is the error the chapter's Part V bridge
    actually made before it was corrected. This is the test that fails.
    """
    expected = {
        "L1": "Arithmetization / encoding",
        "L2": "Commitment + consistency",
        "L3": "Protocol logic",
        "L4": "Non-interactivity + extraction",
    }
    assert {layer.key: layer.name for layer in LAYERS} == expected


def test_every_layer_states_a_role():
    for layer in LAYERS:
        assert layer.role.endswith(".")
        assert len(layer.role.split()) >= 8


def test_the_posture_vocabulary_is_ordered_worst_first():
    assert POSTURES[0] == "broken"
    assert POSTURES[-1] == "not-applicable"
    assert POSTURES.index("weakened") < POSTURES.index("safe")
    assert POSTURES.index("pq-assumption") < POSTURES.index("safe")


def test_each_system_carries_its_own_l2_and_l4_posture():
    """Pin each system to its own row of Table 31.2.

    Every posture value in the table appears more than once, so a test
    that checked only which values are used, or how many systems are
    broken at L2, would survive swapping two systems' postures. Swapping
    the STARK and PLONK rows leaves both of those unchanged and makes
    the chapter's central claim backwards. This is the test that fails.
    """
    expected = {
        "groth16": ("broken", "not-applicable"),
        "plonk_kzg": ("broken", "pending"),
        "ipa_fs": ("broken", "pending"),
        "starks_fri": ("weakened", "pending"),
        "lattice_fs": ("pq-assumption", "pending"),
    }
    assert set(SYSTEMS) == set(expected)
    for key, (l2, l4) in expected.items():
        assert SYSTEMS[key].key == key
        assert SYSTEMS[key].l2_posture == l2
        assert SYSTEMS[key].l4_posture == l4


def test_every_posture_used_is_in_the_vocabulary():
    for profile in SYSTEMS.values():
        assert profile.l2_posture in POSTURES
        assert profile.l4_posture in POSTURES


@pytest.mark.parametrize("system", sorted(SYSTEMS))
def test_l1_is_safe_for_every_system(system):
    assert layer_posture(system, "L1") == "safe"


@pytest.mark.parametrize("system", sorted(SYSTEMS))
def test_l3_inherits_l2_for_every_system(system):
    assert layer_posture(system, "L3") == layer_posture(system, "L2")


def test_groth16_has_no_fiat_shamir_surface():
    assert layer_posture("groth16", "L4") == "not-applicable"


def test_only_groth16_lacks_a_fiat_shamir_surface():
    lacking = [k for k, v in SYSTEMS.items() if v.l4_posture == "not-applicable"]
    assert lacking == ["groth16"]


@pytest.mark.parametrize(
    "system", ["groth16", "plonk_kzg", "ipa_fs", "starks_fri"]
)
def test_l2_is_the_layer_to_audit_first_for_every_classical_group_system(system):
    # Appendix D Exercise 4 gives L2 for all four of these.
    assert thinnest_layer(system) == "L2"


def test_a_lattice_system_moves_the_thinnest_layer_to_l4():
    # With L2 resting on an unbroken post-quantum assumption, the open
    # question is the QROM one at L4 rather than the commitment.
    assert thinnest_layer("lattice_fs") == "L4"


def test_an_unknown_system_is_rejected():
    with pytest.raises(ValueError, match="unknown system"):
        layer_posture("nova", "L2")
    with pytest.raises(ValueError, match="unknown system"):
        thinnest_layer("nova")


def test_an_unknown_layer_is_rejected():
    with pytest.raises(ValueError, match="unknown layer"):
        layer_posture("groth16", "L5")


def test_a_128_bit_target_needs_a_384_bit_hash_under_bht():
    assert hash_bits_for_pq_collision(128) == 384


def test_the_sizing_inverts_the_bht_bound_the_chapter_quotes():
    # Chapter 31 reads the bound the other way: a 256-bit hash delivers
    # about 85 bits. Sizing 85 bits back gives 255, which 256 clears.
    assert 256 // 3 == 85
    assert hash_bits_for_pq_collision(85) == 255


def test_the_no_qracm_bound_asks_for_less_width():
    assert hash_bits_for_pq_collision(128, model="cnps") == 320
    assert hash_bits_for_pq_collision(128, model="cnps") < hash_bits_for_pq_collision(128)


def test_an_odd_target_rounds_up_rather_than_down_under_cnps():
    # 5 * 65 / 2 = 162.5, and 162 bits would not reach the target.
    assert hash_bits_for_pq_collision(65, model="cnps") == 163


def test_a_non_positive_target_is_rejected():
    with pytest.raises(ValueError, match="target_bits must be positive"):
        hash_bits_for_pq_collision(0)


def test_an_unknown_model_is_rejected():
    with pytest.raises(ValueError, match="unknown model"):
        hash_bits_for_pq_collision(128, model="grover")
