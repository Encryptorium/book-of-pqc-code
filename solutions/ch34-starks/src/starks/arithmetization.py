"""AIR (Algebraic Intermediate Representation) for Chapter 34.

An AIR is a compact algebraic description of a computation. A trace is
a sequence of field elements laid out row by row. A transition
constraint is a polynomial over a sliding window of the trace that must
be zero for every legal computation. A boundary constraint pins a
specific row to a specific value.

This module implements the AIR container types plus a Fibonacci-specific
helper that Chapter 34 uses as the running example: a length-8 trace
satisfying the recurrence trace[i+2] == trace[i+1] + trace[i] with
boundary values trace[0] == 1 and trace[1] == 1.

Trace-to-polynomial interpolation uses Lagrange on a multiplicative
subgroup of F_97. The trace domain is the order-8 subgroup generated
by g_8 = 64 (which equals 28^4 mod 97). The LDE module extends this
interpolated polynomial onto a coset of the order-32 subgroup for the
Reed-Solomon low-degree extension.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field


# Chapter 34's running-example parameters over F_97.
DEFAULT_PRIME = 97
TRACE_LENGTH = 8
# g_8 = 64 has order 8 in F_97* (derived from the primitive root 5 via
# 5^(96/8) = 5^12 = 64). The trace polynomial is interpolated over
# {g_8^i : i = 0..7} = {1, 64, 22, 50, 96, 33, 75, 47}.
TRACE_DOMAIN_GENERATOR = 64


@dataclass
class TransitionConstraint:
    """A transition constraint over a sliding window of the trace.

    ``window`` is the number of consecutive trace rows the constraint
    reads. ``evaluator(trace, i, prime)`` returns the residue modulo
    ``prime`` of the constraint expression evaluated at row ``i``. The
    constraint must evaluate to zero for every ``i`` in
    ``range(len(trace) - window + 1)``.
    """

    window: int
    evaluator: Callable[[list[int], int, int], int]
    name: str


@dataclass
class BoundaryConstraint:
    """A boundary constraint pinning ``trace[row] == expected``."""

    row: int
    expected: int
    name: str


@dataclass
class AIR:
    """A minimal AIR: field prime, trace length, transitions, boundaries."""

    field_prime: int
    trace_length: int
    transitions: list[TransitionConstraint] = field(default_factory=list)
    boundaries: list[BoundaryConstraint] = field(default_factory=list)


def fibonacci_air(prime: int = DEFAULT_PRIME, length: int = TRACE_LENGTH) -> AIR:
    """Return the Fibonacci AIR used as Chapter 34's running example.

    One transition constraint (``trace[i+2] - trace[i+1] - trace[i] == 0``
    for ``i`` in the valid range) and two boundary constraints
    (``trace[0] == 1`` and ``trace[1] == 1``). Raises ValueError for a
    non-positive prime or a trace length less than three.
    """
    if prime < 2:
        raise ValueError("prime must be at least two")
    if length < 3:
        raise ValueError("Fibonacci trace must have length at least three")

    def fib_rec(trace: list[int], i: int, p: int) -> int:
        return (trace[i + 2] - trace[i + 1] - trace[i]) % p

    return AIR(
        field_prime=prime,
        trace_length=length,
        transitions=[TransitionConstraint(window=3, evaluator=fib_rec, name="fib_rec")],
        boundaries=[
            BoundaryConstraint(row=0, expected=1, name="fib_init_0"),
            BoundaryConstraint(row=1, expected=1, name="fib_init_1"),
        ],
    )


def fibonacci_trace(length: int = TRACE_LENGTH, prime: int = DEFAULT_PRIME) -> list[int]:
    """Return the canonical length-N Fibonacci trace modulo ``prime``."""
    if length < 2:
        raise ValueError("Fibonacci trace must have length at least two")
    if prime < 2:
        raise ValueError("prime must be at least two")
    trace = [1, 1]
    for _ in range(length - 2):
        trace.append((trace[-1] + trace[-2]) % prime)
    return trace


def evaluate_air(air: AIR, trace: list[int]) -> list[int]:
    """Return the residue list of every constraint evaluated on ``trace``.

    The list is all zeros iff ``trace`` satisfies every transition and
    boundary constraint in ``air``. Transition residues come first in
    the order the constraints were declared, boundary residues last.
    Raises ValueError if the trace length does not match
    ``air.trace_length``.
    """
    if len(trace) != air.trace_length:
        raise ValueError(
            f"trace length {len(trace)} does not match AIR trace_length {air.trace_length}"
        )

    residues: list[int] = []
    for constraint in air.transitions:
        if constraint.window < 2:
            raise ValueError(f"transition window must be at least two: {constraint.name}")
        for i in range(air.trace_length - constraint.window + 1):
            residues.append(constraint.evaluator(trace, i, air.field_prime))
    for boundary in air.boundaries:
        if boundary.row < 0 or boundary.row >= air.trace_length:
            raise ValueError(f"boundary row out of range: {boundary.name}")
        residues.append((trace[boundary.row] - boundary.expected) % air.field_prime)
    return residues


def interpolate_trace(
    trace: list[int],
    trace_domain: list[int],
    prime: int,
) -> list[int]:
    """Lagrange-interpolate ``trace`` through the points of ``trace_domain``.

    Returns the polynomial coefficients in ascending-degree order
    (index ``k`` holds the coefficient of ``x^k``). The resulting
    polynomial has degree at most ``len(trace) - 1`` and satisfies
    ``poly(trace_domain[i]) == trace[i]`` for every ``i``. Raises
    ValueError on length mismatch, duplicate domain points, or an
    invalid prime.
    """
    if prime < 2:
        raise ValueError("prime must be at least two")
    n = len(trace)
    if n != len(trace_domain):
        raise ValueError("trace and trace_domain must have the same length")
    if len(set(trace_domain)) != n:
        raise ValueError("trace_domain must have distinct elements")

    coeffs = [0] * n
    for j in range(n):
        # Lagrange basis L_j(x) = prod_{m != j} (x - d[m]) / (d[j] - d[m])
        numerator = [1]
        denom = 1
        for m in range(n):
            if m == j:
                continue
            # Multiply numerator by (x - trace_domain[m]).
            new_num = [0] * (len(numerator) + 1)
            for idx, c in enumerate(numerator):
                new_num[idx] = (new_num[idx] - c * trace_domain[m]) % prime
                new_num[idx + 1] = (new_num[idx + 1] + c) % prime
            numerator = new_num
            denom = (denom * (trace_domain[j] - trace_domain[m])) % prime
        if denom == 0:
            raise ValueError("duplicate trace_domain points detected during interpolation")
        denom_inv = pow(denom, -1, prime)
        scale = (trace[j] * denom_inv) % prime
        for idx, c in enumerate(numerator):
            coeffs[idx] = (coeffs[idx] + scale * c) % prime

    return coeffs
