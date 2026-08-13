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
    # EXERCISE: implement this function.
    #
    # Return the running example's AIR: one transition constraint of window
    # 3 whose evaluator returns (trace[i+2] - trace[i+1] - trace[i]) mod p,
    # and two boundary constraints pinning row 0 and row 1 to the value 1.
    # Define the evaluator as a local function and pass it into
    # TransitionConstraint; the window is 3 because the recurrence reads
    # three consecutive rows, and the window is what fixes how many start
    # positions the constraint is checked at. Reject a prime below two and a
    # length below three, since a length-2 trace admits no window-3 start
    # position at all.
    #
    # Reference: Chapter 34, '4.1 Arithmetization' (Block 2)
    #
    # Proved by:
    #   tests/ch34/test_arithmetization.py
    raise NotImplementedError("exercise: fibonacci_air")


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
    # EXERCISE: implement this function.
    #
    # Return one residue per constraint instance, transition residues first
    # in declaration order and boundary residues last. For each transition,
    # call its evaluator at every start position i in range(trace_length -
    # window + 1), so a window-3 constraint on a length-8 trace contributes
    # six residues. For each boundary, append (trace[row] - expected) mod
    # prime. The list is all zeros exactly when the trace satisfies the AIR.
    # Hold the package's error contract: raise ValueError on structural
    # malformation (a trace length that does not match the AIR, a window
    # below two, a boundary row out of range) and return a nonzero residue
    # for a trace that merely fails a constraint.
    #
    # Reference: Chapter 34, '4.1 Arithmetization' (Block 2)
    #
    # Proved by:
    #   tests/ch34/test_arithmetization.py
    raise NotImplementedError("exercise: evaluate_air")


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
    # EXERCISE: implement this function.
    #
    # Lagrange interpolation, returning coefficients in ascending-degree
    # order. For each index j, build the basis numerator as the product over
    # m != j of (x - trace_domain[m]) by repeatedly multiplying the running
    # coefficient list by one linear factor: allocate a list one longer, and
    # let each existing coefficient c contribute -c * trace_domain[m] at its
    # own index and +c one index up. Accumulate the denominator as the
    # product over m != j of (trace_domain[j] - trace_domain[m]) alongside,
    # invert it modulo prime, scale the numerator by trace[j] times that
    # inverse, and add the result into the accumulating coefficients. The
    # polynomial has degree at most len(trace) - 1 and reproduces the trace
    # on the domain. Reject a length mismatch, duplicate domain points, and
    # a prime below two.
    #
    # Reference: Chapter 34, '4.2 LDE' (Block 3)
    #
    # Proved by:
    #   tests/ch34/test_arithmetization.py
    raise NotImplementedError("exercise: interpolate_trace")
