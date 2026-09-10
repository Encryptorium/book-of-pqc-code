"""Toy lattice polynomial commitment for Chapter 32.

This module implements a pedagogical sketch of an SIS-style vector
commitment. It is not a working lattice polynomial commitment in the
sense of Greyhound, Jindo, Hachi, or Serval: the concrete constructions
in the 2024-2026 literature are an order of magnitude more intricate
than one chapter can accommodate, and they all live over the
polynomial ring ``R_q = Z_q[X] / (X^n + 1)``. This module deliberately
works over scalar ``Z_q`` rather than ``R_q`` so the binding equation
is fully inspectable; the displayed instance is therefore plain SIS
over a small matrix, not Module-SIS, and production lattice PCS
reduces to Module-SIS or a construction-specific module/ring SIS
variant.

What this module does capture is the load-bearing design pattern:

- Binding reduces to the hardness of (Module-)SIS over the relevant
  algebraic structure.
- Hiding, in the real schemes, comes from independent Gaussian
  randomness added to the commitment under Module-LWE; this toy
  carries no such randomness and is binding only.
- Openings reveal the committed vector; the verifier recomputes the
  commitment equation and compares.

Randomising the error alone would not make the toy hiding: a receiver
holding two candidate messages subtracts ``A m`` for each from ``C``
and keeps the one whose residual is short, which on these parameters
identifies the message every time. The real constructions commit as
``A_0 m + A_1 r + e`` with ``(r, e)`` drawn independently of ``m``, so
that ``A_1 r + e`` is a Module-LWE sample masking the message. The
fixed-error commit here demonstrates the binding equation only.

Chapter 32 uses this module to exhibit SIS-style binding concretely.
``verify`` is a deterministic recomputation of the equation, so it
rejects any opening that does not satisfy it. That is not the same as
detecting every tampering: a second opening in the kernel of ``A``
produces the same commitment and is accepted. Binding is the claimed
difficulty of finding such a second SHORT opening, which is Module-SIS,
and not an injectivity property of a short modular linear map. On a
matrix with two equal columns the unit vectors ``e_1`` and ``e_2`` are
both short, both open the same commitment, and both verify. The module
does not implement an evaluation-opening protocol because the toy
parameters are too small to support a sensible evaluation procedure;
the Chapter 32 prose cites Greyhound, Jindo, Hachi, and Serval for the
evaluation protocols at the 2024-2026 frontier.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass


# Toy scalar-SIS parameters. These are pedagogically sized (much smaller
# than the 2024-2026 frontier parameters). Chapter 32 explicitly calls
# this out and cites the Hwang et al. 2024, Nguyen-Seiler 2024, Hwang
# et al. 2026, and Nguyen et al. 2026 papers for concrete parameters.
DEFAULT_MODULUS = 257
DEFAULT_DIMENSION = 8  # vector length
DEFAULT_COMMIT_SIZE = 4  # number of commitment coordinates
DEFAULT_ERROR_BOUND = 2  # small-error infinity norm for the binding equation


@dataclass
class LatticeParams:
    """Parameters for the toy scalar-SIS commitment.

    ``modulus`` is the modulus q of the scalar ring ``Z_q``; the toy has
    no polynomial ring. ``dimension`` is the length of
    the committed vector m. ``commit_size`` is the length of the
    commitment vector (equivalently, the number of rows of the public
    matrix A). ``error_bound`` bounds the infinity norm of the random
    error e added to the binding equation; it supplies no hiding
    guarantee, for the reason the module docstring gives.
    """

    modulus: int
    dimension: int
    commit_size: int
    error_bound: int


@dataclass
class PublicMatrix:
    """Public randomness A in the SIS commitment equation."""

    params: LatticeParams
    rows: list[list[int]]


@dataclass
class LatticeCommit:
    """A commitment to a small-coefficient message vector.

    ``value`` is A*m + e mod q. ``params`` records the parameters used
    so the verifier can recompute the equation.
    """

    params: LatticeParams
    value: list[int]


def default_params() -> LatticeParams:
    """Return the default pedagogical parameters."""
    return LatticeParams(
        modulus=DEFAULT_MODULUS,
        dimension=DEFAULT_DIMENSION,
        commit_size=DEFAULT_COMMIT_SIZE,
        error_bound=DEFAULT_ERROR_BOUND,
    )


def sample_public_matrix(
    params: LatticeParams,
    seed: bytes | None = None,
) -> PublicMatrix:
    """Sample the public matrix A uniformly at random from Z_q.

    In a production deployment, A is derived from a public seed via a
    hash-based XOF to avoid trusting the sampler. This toy uses
    ``secrets.randbelow`` when no seed is provided, and a deterministic
    pseudo-random expansion when a seed is supplied so tests can be
    reproducible.
    """
    if seed is None:
        rows = [
            [secrets.randbelow(params.modulus) for _ in range(params.dimension)]
            for _ in range(params.commit_size)
        ]
    else:
        # Simple deterministic expansion from seed via a counter-mode
        # SHA-256 stream. Pedagogical only.
        rows = []
        counter = 0
        buffer = b""
        for _ in range(params.commit_size):
            row: list[int] = []
            for _ in range(params.dimension):
                while len(buffer) < 4:
                    buffer += hashlib.sha256(seed + counter.to_bytes(8, "big")).digest()
                    counter += 1
                word = int.from_bytes(buffer[:4], "big")
                buffer = buffer[4:]
                row.append(word % params.modulus)
            rows.append(row)
    return PublicMatrix(params=params, rows=rows)


def _centered(value: int, modulus: int) -> int:
    """Return the centered representative in (-q/2, q/2] of ``value`` mod q."""
    value = value % modulus
    if value > modulus // 2:
        value -= modulus
    return value


def sample_error(params: LatticeParams) -> list[int]:
    """Sample a small-norm error vector for the binding equation.

    Each coordinate is uniform in ``[-error_bound, error_bound]``. The
    returned representation is centered; the caller adds modulo q. The
    error carries no hiding guarantee: see the module docstring for the
    short-residual distinguisher that recovers the message anyway.
    """
    width = 2 * params.error_bound + 1
    return [secrets.randbelow(width) - params.error_bound for _ in range(params.commit_size)]


def commit(
    matrix: PublicMatrix,
    message: list[int],
    error: list[int],
) -> LatticeCommit:
    """Compute C = A * m + e mod q.

    ``message`` and ``error`` are centered-representation vectors. Each
    coordinate of the message should be small relative to q for the
    SIS-style binding argument to apply. Raises ValueError on
    dimension mismatches.
    """
    params = matrix.params
    if len(message) != params.dimension:
        raise ValueError("message dimension does not match params")
    if len(error) != params.commit_size:
        raise ValueError("error vector length does not match commit_size")

    value: list[int] = []
    for row, e in zip(matrix.rows, error):
        acc = 0
        for a, m in zip(row, message):
            acc += a * m
        acc = (acc + e) % params.modulus
        value.append(acc)
    return LatticeCommit(params=params, value=value)


def verify(
    matrix: PublicMatrix,
    commitment: LatticeCommit,
    message: list[int],
    error: list[int],
) -> bool:
    """Verify an opening by recomputing ``A * m + e`` and comparing.

    Returns True if the recomputed value matches the commitment
    coordinate-for-coordinate, False otherwise.
    """
    recomputed = commit(matrix, message, error)
    return recomputed.value == commitment.value


def sis_binding_witness(
    message_a: list[int],
    error_a: list[int],
    message_b: list[int],
    error_b: list[int],
    modulus: int,
) -> tuple[list[int], list[int]]:
    """Given two openings that produce the same commitment, extract an SIS solution.

    If C = A*m_a + e_a = A*m_b + e_b mod q, then
    A*(m_a - m_b) + (e_a - e_b) = 0 mod q, which is an SIS solution
    with combined message-error vector (m_a - m_b, e_a - e_b). Finding
    one is infeasible under SIS, so this routine exists to
    demonstrate the reduction, not as an attack tool.
    """
    if len(message_a) != len(message_b):
        raise ValueError("message dimensions must match")
    if len(error_a) != len(error_b):
        raise ValueError("error dimensions must match")
    diff_m = [_centered(a - b, modulus) for a, b in zip(message_a, message_b)]
    diff_e = [_centered(a - b, modulus) for a, b in zip(error_a, error_b)]
    return diff_m, diff_e
