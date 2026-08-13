"""Tests for ``fiat_shamir_qrom.measure_and_reprogram``."""

import pytest

from fiat_shamir_qrom import measure_and_reprogram, rom_simulator


def make_echo_adversary(query_inputs):
    """Build a deterministic adversary that queries a fixed sequence.

    The adversary's output is the tuple of oracle responses for the
    given query inputs. Because the query sequence is fixed at
    construction time, the adversary's behavior is deterministic up to
    the oracle responses themselves, which is what the measure-and-
    reprogram scaffolding requires.
    """
    fixed_inputs = tuple(query_inputs)

    def adversary(oracle: rom_simulator.RandomOracle):
        return tuple(oracle.query(x) for x in fixed_inputs)

    return adversary


def test_run_adversary_records_queries_and_output() -> None:
    adv = make_echo_adversary([b"x", b"y", b"z"])
    result = measure_and_reprogram.run_adversary(
        adv, output_modulus=1013, seed=b"test"
    )
    assert result["queries"] == (b"x", b"y", b"z")
    assert isinstance(result["output"], tuple)
    assert len(result["output"]) == 3
    for value in result["output"]:
        assert 0 <= value < 1013


def test_simulate_classical_extraction_consistency() -> None:
    adv = make_echo_adversary([b"alpha", b"beta", b"gamma", b"delta"])
    result = measure_and_reprogram.simulate_classical_extraction(
        adv,
        output_modulus=1013,
        seed=b"mr-test",
        measured_index=2,
        reprogrammed_value=777,
    )
    assert result["measured_index"] == 2
    assert result["measured_input"] == b"gamma"
    assert result["reprogrammed_value"] == 777
    assert result["second_response_at_x_star"] == 777
    assert result["consistent"] is True


def test_second_run_output_reflects_reprogramming_at_index() -> None:
    adv = make_echo_adversary([b"a", b"b", b"c"])
    result = measure_and_reprogram.simulate_classical_extraction(
        adv,
        output_modulus=1013,
        seed=b"reflect",
        measured_index=1,
        reprogrammed_value=500,
    )
    # The second run's output tuple at position 1 must equal the
    # reprogrammed value.
    second_output = result["second_output"]
    assert second_output[1] == 500
    # Positions 0 and 2 are queried against a fresh oracle with the
    # same seed, so they must equal the first run's responses at
    # those positions.
    first_output = result["first_output"]
    assert second_output[0] == first_output[0]
    assert second_output[2] == first_output[2]


def test_empty_adversary_raises() -> None:
    def no_query_adversary(oracle):
        return "nothing queried"

    with pytest.raises(ValueError):
        measure_and_reprogram.simulate_classical_extraction(
            no_query_adversary,
            output_modulus=1013,
            seed=b"empty",
        )


def test_measured_index_out_of_range_raises() -> None:
    adv = make_echo_adversary([b"x", b"y"])
    with pytest.raises(ValueError):
        measure_and_reprogram.simulate_classical_extraction(
            adv,
            output_modulus=1013,
            seed=b"oor",
            measured_index=5,
        )
    with pytest.raises(ValueError):
        measure_and_reprogram.simulate_classical_extraction(
            adv,
            output_modulus=1013,
            seed=b"oor",
            measured_index=-1,
        )


def test_reprogrammed_value_out_of_range_raises() -> None:
    adv = make_echo_adversary([b"x"])
    with pytest.raises(ValueError):
        measure_and_reprogram.simulate_classical_extraction(
            adv,
            output_modulus=1013,
            seed=b"oor",
            measured_index=0,
            reprogrammed_value=1013,  # == modulus, out of range
        )
    with pytest.raises(ValueError):
        measure_and_reprogram.simulate_classical_extraction(
            adv,
            output_modulus=1013,
            seed=b"oor",
            measured_index=0,
            reprogrammed_value=-1,
        )


def test_divergent_adversary_raises() -> None:
    """An adversary whose queries branch on oracle responses diverges.

    The scaffolding requires that the second run hit the measured
    input. An adversary that re-queries a different input on the
    second run fails this invariant, and the scaffolding raises.
    """
    call_counter = {"n": 0}

    def divergent_adversary(oracle: rom_simulator.RandomOracle):
        call_counter["n"] += 1
        if call_counter["n"] == 1:
            return tuple(oracle.query(x) for x in (b"first", b"branch-a"))
        return tuple(oracle.query(x) for x in (b"first", b"branch-b"))

    with pytest.raises(ValueError):
        measure_and_reprogram.simulate_classical_extraction(
            divergent_adversary,
            output_modulus=1013,
            seed=b"divergent",
            measured_index=1,
            reprogrammed_value=5,
        )


def test_reduction_loss_dfms19_basic() -> None:
    # (2q + 1)^2 / |C| with q = 0 gives 1/|C|.
    assert measure_and_reprogram.reduction_loss_dfms19(0, 1024) == pytest.approx(1 / 1024)
    # With q = 3 and |C| = 1013: (2*3 + 1)^2 = 49, so 49 / 1013.
    assert measure_and_reprogram.reduction_loss_dfms19(3, 1013) == pytest.approx(
        49 / 1013
    )


def test_reduction_loss_dfms19_rejects_bad_inputs() -> None:
    with pytest.raises(ValueError):
        measure_and_reprogram.reduction_loss_dfms19(-1, 1024)
    with pytest.raises(ValueError):
        measure_and_reprogram.reduction_loss_dfms19(5, 0)
    with pytest.raises(ValueError):
        measure_and_reprogram.reduction_loss_dfms19(5, -10)


def test_parameter_bump_bits_zero_when_space_sufficient() -> None:
    # q = 2^40, target = 128, current |C| = 256 bits.
    # Required = 2*40 + 128 = 208 <= 256, so bump is 0.
    assert (
        measure_and_reprogram.parameter_bump_bits(
            query_budget_bits=40,
            challenge_space_bits=256,
            target_pq_bits=128,
        )
        == 0
    )


def test_parameter_bump_bits_positive_when_space_insufficient() -> None:
    # q = 2^80, target = 128, current |C| = 32 bits.
    # Required = 2*80 + 128 = 288. Bump = 288 - 32 = 256.
    assert (
        measure_and_reprogram.parameter_bump_bits(
            query_budget_bits=80,
            challenge_space_bits=32,
            target_pq_bits=128,
        )
        == 256
    )
    # q = 2^100, target = 128, current |C| = 32.
    # Required = 2*100 + 128 = 328. Bump = 328 - 32 = 296.
    assert (
        measure_and_reprogram.parameter_bump_bits(
            query_budget_bits=100,
            challenge_space_bits=32,
            target_pq_bits=128,
        )
        == 296
    )


def test_parameter_bump_bits_rejects_bad_inputs() -> None:
    with pytest.raises(ValueError):
        measure_and_reprogram.parameter_bump_bits(-1, 128, 128)
    with pytest.raises(ValueError):
        measure_and_reprogram.parameter_bump_bits(40, 0, 128)
    with pytest.raises(ValueError):
        measure_and_reprogram.parameter_bump_bits(40, 128, 0)


def test_random_measurement_is_within_range() -> None:
    adv = make_echo_adversary([b"q0", b"q1", b"q2", b"q3", b"q4"])
    # Default measured_index is random; run several times and check
    # it always lies in [0, 5).
    for _ in range(10):
        result = measure_and_reprogram.simulate_classical_extraction(
            adv,
            output_modulus=1013,
            seed=b"random-idx",
        )
        assert 0 <= result["measured_index"] < 5
        assert 0 <= result["reprogrammed_value"] < 1013
        assert result["consistent"] is True


def test_random_measured_index_can_reach_every_query() -> None:
    """``i*`` is drawn over the whole query log, final slot included.

    The chapter's statement of the lemma draws ``i*`` uniformly from
    ``{1, ..., q + 1}``, and the ``(2q + 1)`` factor is a count of
    those positions. A sampler that silently cannot reach the last
    index still satisfies every consistency assertion in this file,
    because whichever index it does pick reprograms correctly.
    """
    adversary = make_echo_adversary([b"q0", b"q1", b"q2"])
    seen = set()
    for _ in range(60):
        result = measure_and_reprogram.simulate_classical_extraction(
            adversary, output_modulus=1013, seed=b"idx"
        )
        seen.add(result["measured_index"])
    assert seen == {0, 1, 2}
