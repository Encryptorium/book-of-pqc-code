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
    # EXERCISE: implement this function.
    #
    # Return the chapter's pedagogical parameter set as a LatticeParams:
    # modulus 257, message dimension 8, commitment dimension 4, error bound
    # 2. The module constants above already hold these values. Production
    # lattice PCS parameters are two orders of magnitude larger in every
    # dimension and live over the ring R_q = Z_q[X]/(X^n + 1) rather than
    # scalar Z_q.
    #
    # Reference: Chapter 32, 'Lattice PCS: SIS binding, recent literature'
    #
    # Proved by:
    #   tests/ch32/test_lattice_pcs.py
    raise NotImplementedError("exercise: default_params")


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
    # EXERCISE: implement this function.
    #
    # A is commit_size rows of dimension entries, each uniform in Z_q. With
    # no seed, draw each entry with secrets.randbelow. With a seed, expand
    # it deterministically so a test can reproduce the matrix: run a
    # counter-mode SHA-256 stream over seed concatenated with an 8-byte
    # big-endian counter, consume the digest four bytes at a time as a
    # big-endian integer, and reduce each word modulo q. In production A is
    # derived from a public seed for exactly this reason, so nobody has to
    # trust whoever sampled it.
    #
    # Reference: Chapter 32, 'Lattice PCS: SIS binding, recent literature'
    #
    # Proved by:
    #   tests/ch32/test_lattice_pcs.py
    raise NotImplementedError("exercise: sample_public_matrix")


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
    # EXERCISE: implement this function.
    #
    # Each coordinate is uniform in [-error_bound, error_bound], which is 2
    # * error_bound + 1 possible values, so draw from that width and
    # subtract the bound. There are commit_size coordinates, one per
    # commitment coordinate rather than one per message coordinate, because
    # e is added after A*m. The result is in centered representation and the
    # caller reduces modulo q. The error supplies the small additive term of
    # the binding equation, and its smallness is what keeps the norm bound
    # in the SIS argument tight. It is not a hiding mechanism: a receiver
    # holding two candidate messages subtracts A*m for each from C and keeps
    # the one whose residual is short, which identifies the message every
    # time at these parameters. Hiding in the real schemes comes from an
    # independent Module-LWE term the toy has no analogue of.
    #
    # Reference: Chapter 32, 'Lattice PCS: SIS binding, recent literature'
    #
    # Proved by:
    #   tests/ch32/test_lattice_pcs.py
    raise NotImplementedError("exercise: sample_error")


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
    # EXERCISE: implement this function.
    #
    # C = A*m + e mod q. Accumulate each row's dot product against the
    # message, add that row's error coordinate, and reduce modulo q once per
    # row. Message and error arrive in centered representation, so partial
    # sums can be negative before the reduction; Python's % returns a
    # non-negative representative, which is the form the verifier compares
    # against. Reject a message whose length is not the parameter dimension
    # and an error whose length is not commit_size.
    #
    # Reference: Chapter 32, 'Lattice PCS: SIS binding, recent literature'
    #
    # Proved by:
    #   tests/ch32/test_lattice_pcs.py
    raise NotImplementedError("exercise: commit")


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
    # EXERCISE: implement this function.
    #
    # Recompute A*m + e from the revealed opening and compare coordinate for
    # coordinate against the stored commitment, returning a bool. There is
    # no evaluation protocol at these toy parameters: the opening reveals
    # the vector outright, so verification is the commit equation run a
    # second time. The check is deterministic, so an opening that does not
    # satisfy the equation is always rejected. That is weaker than catching
    # every tampering: a second opening differing by a kernel vector of A
    # recomputes to the same commitment and is accepted. Binding is the
    # claimed hardness of finding a second SHORT opening, which is SIS,
    # rather than any property of this recomputation.
    #
    # Reference: Chapter 32, 'Lattice PCS: SIS binding, recent literature'
    #
    # Proved by:
    #   tests/ch32/test_lattice_pcs.py
    raise NotImplementedError("exercise: verify")


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
    # EXERCISE: implement this function.
    #
    # If A*m_a + e_a and A*m_b + e_b are the same commitment, then A*(m_a -
    # m_b) + (e_a - e_b) = 0 mod q, so the coordinatewise differences are a
    # solution to the homogeneous SIS instance. Return them in centered
    # representation, since it is the shortness of that solution and not
    # merely its existence that makes SIS hard: an unbounded solution is
    # trivial to write down. Reject mismatched lengths. The routine exhibits
    # the binding reduction; producing two such openings in the first place
    # is the infeasible half.
    #
    # Reference: Chapter 32, 'Lattice PCS: SIS binding, recent literature'
    #
    # Proved by:
    #   tests/ch32/test_lattice_pcs.py
    raise NotImplementedError("exercise: sis_binding_witness")
