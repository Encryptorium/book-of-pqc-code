"""Preimage target populations and the reduction ADRS removes.

The expected values are the chapter's printed table, which is what makes this
suite a regression guard on the chapter as well as on the package.
"""

import math

import pytest

from hash_cryptanalysis.multitarget import (
    effective_preimage_bits,
    effective_quantum_preimage_bits,
    fors_instance_targets,
    multi_target_advantage_bits,
    preimage_target_population,
    wots_layer_targets,
)
from hash_cryptanalysis.params import SHA2_PARAMETER_SETS, by_name


SHORT_NAMES = [ps.name.rsplit("-", 1)[-1] for ps in SHA2_PARAMETER_SETS]

#: The chapter's printed table: short name -> (targets, adv, no_adrs).
PRINTED_TABLE = {
    "128s": (57_589, 15.8, 112.2),
    "128f": (2_882, 11.5, 116.5),
    "192s": (278_885, 18.1, 173.9),
    "192f": (9_570, 13.2, 178.8),
    "256s": (360_984, 18.5, 237.5),
    "256f": (19_059, 14.2, 241.8),
}


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_target_population_matches_the_chapter(short):
    ps = by_name(short)
    assert preimage_target_population(ps) == PRINTED_TABLE[short][0]


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_population_splits_into_fors_and_wots(short):
    ps = by_name(short)
    assert fors_instance_targets(ps) == ps.k * ps.t
    assert wots_layer_targets(ps) == ps.d * ps.ell
    assert (
        fors_instance_targets(ps) + wots_layer_targets(ps)
        == preimage_target_population(ps)
    )


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_advantage_matches_the_chapter(short):
    ps = by_name(short)
    assert round(multi_target_advantage_bits(ps), 1) == PRINTED_TABLE[short][1]


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_undefended_security_matches_the_chapter(short):
    ps = by_name(short)
    assert round(effective_preimage_bits(ps), 1) == PRINTED_TABLE[short][2]


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_every_set_falls_below_its_category_floor_without_adrs(short):
    """The whole point of the table: no set meets its own floor undefended."""
    ps = by_name(short)
    assert effective_preimage_bits(ps) < ps.n_bits


def test_small_sets_expose_more_targets_than_fast_sets():
    """t = 2**a grows faster than k shrinks, so the 's' sets expose more."""
    for small, fast in (("128s", "128f"), ("192s", "192f"), ("256s", "256f")):
        assert preimage_target_population(by_name(small)) > preimage_target_population(
            by_name(fast)
        )


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_quantum_reduction_halves_the_classical_exponent(short):
    """Grover over N marked items costs sqrt(2**n / N), so subtract then halve."""
    ps = by_name(short)
    classical = effective_preimage_bits(ps)
    assert effective_quantum_preimage_bits(ps) == pytest.approx(classical / 2)


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_quantum_reduction_is_not_grover_minus_the_advantage(short):
    """The order matters: halving after subtracting is not subtracting after halving."""
    ps = by_name(short)
    wrong = ps.n_bits / 2 - multi_target_advantage_bits(ps)
    assert effective_quantum_preimage_bits(ps) > wrong


def test_custom_parameter_set_off_the_standard_table():
    """Exercise 1's parameters: n = 20 bytes, k = 10, a = 10, d = 5, w = 16.

    Sized so the answer is not one of the six standard rows, which makes this a
    test of the formulas rather than of the table. The exercise states no `h`,
    and none of these quantities reads it; `h = 50` is supplied only because a
    `ParameterSet` needs `h = d * h_prime` to be exact.
    """
    from hash_cryptanalysis.params import ParameterSet

    ps = ParameterSet("custom", n_bytes=20, h=50, d=5, a=10, k=10)
    assert ps.n_bits == 160
    assert ps.ell == 43
    assert fors_instance_targets(ps) == 10_240
    assert wots_layer_targets(ps) == 215
    assert preimage_target_population(ps) == 10_455
    assert round(multi_target_advantage_bits(ps), 1) == 13.4
    assert round(effective_preimage_bits(ps), 1) == 146.6
    assert math.isclose(
        effective_quantum_preimage_bits(ps), effective_preimage_bits(ps) / 2
    )
