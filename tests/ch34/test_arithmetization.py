"""Tests for starks.arithmetization."""

from __future__ import annotations

import pytest

from starks.arithmetization import (
    AIR,
    BoundaryConstraint,
    DEFAULT_PRIME,
    TRACE_DOMAIN_GENERATOR,
    TRACE_LENGTH,
    TransitionConstraint,
    evaluate_air,
    fibonacci_air,
    fibonacci_trace,
    interpolate_trace,
)
from starks.lde import eval_poly, trace_domain


def test_fibonacci_air_default_shape():
    air = fibonacci_air()
    assert air.field_prime == DEFAULT_PRIME
    assert air.trace_length == TRACE_LENGTH
    assert len(air.transitions) == 1
    assert len(air.boundaries) == 2
    assert air.transitions[0].name == "fib_rec"
    assert air.transitions[0].window == 3
    assert air.boundaries[0].row == 0
    assert air.boundaries[0].expected == 1


def test_fibonacci_trace_values():
    trace = fibonacci_trace()
    assert trace == [1, 1, 2, 3, 5, 8, 13, 21]


def test_evaluate_air_passes_honest_trace():
    air = fibonacci_air()
    trace = fibonacci_trace()
    residues = evaluate_air(air, trace)
    assert all(r == 0 for r in residues)
    # 6 transition residues (windows 0..5) + 2 boundary residues
    assert len(residues) == 8


def test_evaluate_air_rejects_wrong_initial_value():
    air = fibonacci_air()
    trace = fibonacci_trace()
    bad = list(trace)
    bad[0] = 2
    residues = evaluate_air(air, bad)
    assert any(r != 0 for r in residues)


def test_evaluate_air_rejects_wrong_recurrence():
    air = fibonacci_air()
    trace = fibonacci_trace()
    bad = list(trace)
    bad[4] = (bad[4] + 1) % DEFAULT_PRIME  # break trace[4] = trace[3] + trace[2]
    residues = evaluate_air(air, bad)
    assert any(r != 0 for r in residues)


def test_evaluate_air_length_mismatch_raises():
    air = fibonacci_air()
    with pytest.raises(ValueError):
        evaluate_air(air, [1, 1, 2])


def test_fibonacci_air_invalid_prime_raises():
    with pytest.raises(ValueError):
        fibonacci_air(prime=1)


def test_fibonacci_air_short_trace_raises():
    with pytest.raises(ValueError):
        fibonacci_air(length=2)


def test_fibonacci_trace_invalid_prime_raises():
    with pytest.raises(ValueError):
        fibonacci_trace(prime=0)


def test_fibonacci_trace_short_length_raises():
    with pytest.raises(ValueError):
        fibonacci_trace(length=1)


def test_interpolate_trace_recovers_values():
    prime = DEFAULT_PRIME
    domain = trace_domain(
        generator=TRACE_DOMAIN_GENERATOR, length=TRACE_LENGTH, prime=prime
    )
    trace = fibonacci_trace()
    coeffs = interpolate_trace(trace, domain, prime)
    assert len(coeffs) == TRACE_LENGTH
    for x, y in zip(domain, trace):
        assert eval_poly(coeffs, x, prime) == y


def test_interpolate_trace_length_mismatch_raises():
    with pytest.raises(ValueError):
        interpolate_trace([1, 2], [1], DEFAULT_PRIME)


def test_interpolate_trace_duplicate_domain_raises():
    with pytest.raises(ValueError):
        interpolate_trace([1, 2], [3, 3], DEFAULT_PRIME)


def test_interpolate_trace_invalid_prime_raises():
    with pytest.raises(ValueError):
        interpolate_trace([1], [1], 1)


def test_custom_transition_constraint():
    prime = 11
    def constant_eval(trace, i, p):
        return (trace[i] - trace[i + 1]) % p
    air = AIR(
        field_prime=prime,
        trace_length=4,
        transitions=[TransitionConstraint(window=2, evaluator=constant_eval, name="const")],
        boundaries=[],
    )
    # Constant trace [5, 5, 5, 5] passes.
    assert evaluate_air(air, [5, 5, 5, 5]) == [0, 0, 0]
    # Changing any value breaks a transition.
    assert any(r != 0 for r in evaluate_air(air, [5, 5, 6, 5]))


def test_boundary_row_out_of_range_raises():
    prime = 11
    air = AIR(
        field_prime=prime,
        trace_length=3,
        transitions=[],
        boundaries=[BoundaryConstraint(row=10, expected=1, name="bad")],
    )
    with pytest.raises(ValueError):
        evaluate_air(air, [1, 1, 1])


def test_transition_window_too_small_raises():
    prime = 11
    air = AIR(
        field_prime=prime,
        trace_length=3,
        transitions=[
            TransitionConstraint(
                window=1,
                evaluator=lambda trace, i, p: 0,
                name="bad",
            )
        ],
        boundaries=[],
    )
    with pytest.raises(ValueError):
        evaluate_air(air, [1, 1, 1])
