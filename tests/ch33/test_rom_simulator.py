"""Tests for ``fiat_shamir_qrom.rom_simulator``."""

import pytest

from fiat_shamir_qrom import rom_simulator


def test_rejects_bad_output_modulus() -> None:
    with pytest.raises(ValueError):
        rom_simulator.RandomOracle(output_modulus=0)
    with pytest.raises(ValueError):
        rom_simulator.RandomOracle(output_modulus=-5)


def test_query_requires_bytes_input() -> None:
    oracle = rom_simulator.RandomOracle(output_modulus=1013)
    with pytest.raises(ValueError):
        oracle.query("not bytes")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        oracle.query(42)  # type: ignore[arg-type]


def test_query_is_deterministic() -> None:
    oracle = rom_simulator.RandomOracle(output_modulus=1013, seed=b"seed-a")
    first = oracle.query(b"hello")
    second = oracle.query(b"hello")
    assert first == second
    assert 0 <= first < 1013


def test_different_seeds_give_different_samples() -> None:
    """The seed is the oracle's domain separator, not decoration.

    Two oracles differing only in seed must lazy-sample independently.
    A single input can collide modulo 1013 by chance, so compare the
    response vectors over several inputs: SHA-256 is deterministic, so
    this either holds for these fixed seeds or it does not. Dropping
    the seed from the digest leaves every round-trip and caching test
    in this file passing, because both parties still agree with each
    other.
    """
    a = rom_simulator.RandomOracle(output_modulus=1013, seed=b"alpha")
    b = rom_simulator.RandomOracle(output_modulus=1013, seed=b"beta")
    inputs = [b"x", b"y", b"z", b"w"]
    a_responses = [a.query(i) for i in inputs]
    b_responses = [b.query(i) for i in inputs]
    assert a_responses != b_responses
    assert all(0 <= r < 1013 for r in a_responses + b_responses)


def test_query_log_records_order_and_repeats() -> None:
    oracle = rom_simulator.RandomOracle(output_modulus=1013)
    oracle.query(b"a")
    oracle.query(b"b")
    oracle.query(b"a")  # repeat
    assert oracle.queries == (b"a", b"b", b"a")
    assert oracle.query_count() == 3


def test_is_queried_and_is_programmed_flags() -> None:
    oracle = rom_simulator.RandomOracle(output_modulus=1013)
    assert not oracle.is_queried(b"x")
    assert not oracle.is_programmed(b"x")
    oracle.query(b"x")
    assert oracle.is_queried(b"x")
    assert not oracle.is_programmed(b"x")


def test_reprogram_before_query_returns_programmed_value() -> None:
    oracle = rom_simulator.RandomOracle(output_modulus=1013)
    oracle.reprogram(b"x", 42)
    assert oracle.is_programmed(b"x")
    assert not oracle.is_queried(b"x")
    assert oracle.query(b"x") == 42
    assert oracle.is_queried(b"x")


def test_reprogram_after_query_raises() -> None:
    oracle = rom_simulator.RandomOracle(output_modulus=1013)
    oracle.query(b"x")  # x is now cached
    with pytest.raises(ValueError):
        oracle.reprogram(b"x", 7)


def test_reprogram_out_of_range_raises() -> None:
    oracle = rom_simulator.RandomOracle(output_modulus=1013)
    with pytest.raises(ValueError):
        oracle.reprogram(b"x", 1013)  # == modulus, out of range
    with pytest.raises(ValueError):
        oracle.reprogram(b"x", -1)


def test_reprogram_requires_bytes_input() -> None:
    oracle = rom_simulator.RandomOracle(output_modulus=1013)
    with pytest.raises(ValueError):
        oracle.reprogram("x", 5)  # type: ignore[arg-type]


def test_cached_response_requires_prior_query() -> None:
    oracle = rom_simulator.RandomOracle(output_modulus=1013)
    with pytest.raises(ValueError):
        oracle.cached_response(b"unseen")
    oracle.query(b"seen")
    assert oracle.cached_response(b"seen") == oracle.query(b"seen")


def test_bulk_sample_returns_list_of_responses() -> None:
    oracle = rom_simulator.RandomOracle(output_modulus=1013, seed=b"s")
    inputs = [b"a", b"b", b"c", b"a"]
    responses = rom_simulator.bulk_sample(oracle, inputs)
    assert len(responses) == 4
    assert responses[0] == responses[3]  # a queried twice, same value
    assert oracle.query_count() == 4


def test_responses_within_range() -> None:
    oracle = rom_simulator.RandomOracle(output_modulus=17, seed=b"tiny")
    for i in range(50):
        value = oracle.query(f"input-{i}".encode("ascii"))
        assert 0 <= value < 17


def test_default_output_matches_the_schnorr_challenge_space() -> None:
    """``DEFAULT_OUTPUT`` is the Schnorr challenge space, by construction.

    The module docstring claims the default "lines up with the Schnorr
    challenge space in ``fiat_shamir``", and ``fs_prove`` rejects any
    oracle whose modulus differs. Every test builds its oracle with an
    explicit modulus, so the default itself is otherwise unread and can
    drift away from the claim with the suite green.
    """
    from fiat_shamir_qrom import fiat_shamir

    assert rom_simulator.DEFAULT_OUTPUT == fiat_shamir.DEFAULT_ORDER

