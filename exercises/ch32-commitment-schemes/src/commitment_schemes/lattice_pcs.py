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
- Hiding is obtained via a small random error added to each commitment.
- Openings reveal the committed vector; the verifier recomputes the
  commitment equation and compares.

The toy does not add a rejection-sampling or noise-flooding randomizer
on top, which production constructions need to make hiding hold under
chosen-message use; the fixed-error commit demonstrates the binding
equation only.

Chapter 32 uses this module to exhibit SIS-style binding concretely and
to let the reader verify that tampering with either the committed
vector or the error term is detected with probability one. The module
does not implement an evaluation-opening protocol because the toy
parameters are too small to support a sensible evaluation procedure;
the Chapter 32 prose cites Greyhound, Jindo, Hachi, and Serval for the
evaluation protocols at the 2024-2026 frontier.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass


# Toy Module-SIS parameters. These are pedagogically sized (much smaller
# than the 2024-2026 frontier parameters). Chapter 32 explicitly calls
# this out and cites the Hwang et al. 2024, Nguyen-Seiler 2024, Hwang
# et al. 2026, and Nguyen et al. 2026 papers for concrete parameters.
DEFAULT_MODULUS = 257
DEFAULT_DIMENSION = 8  # vector length
DEFAULT_COMMIT_SIZE = 4  # number of commitment coordinates
DEFAULT_ERROR_BOUND = 2  # small-error infinity norm for hiding


@dataclass
class LatticeParams:
    """Parameters for the toy Module-SIS commitment.

    ``modulus`` is the ring modulus q. ``dimension`` is the length of
    the committed vector m. ``commit_size`` is the length of the
    commitment vector (equivalently, the number of rows of the public
    matrix A). ``error_bound`` bounds the infinity norm of the random
    error e used for hiding.
    """

    modulus: int
    dimension: int
    commit_size: int
    error_bound: int


@dataclass
class PublicMatrix:
    """Public randomness A in the Module-SIS commitment equation."""

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
    """Sample a small-norm error vector for hiding.

    Each coordinate is uniform in ``[-error_bound, error_bound]``. The
    returned representation is centered; the caller adds modulo q.
    """
    # EXERCISE: implement this function.
    #
    # Each coordinate is uniform in [-error_bound, error_bound], which is 2
    # * error_bound + 1 possible values, so draw from that width and
    # subtract the bound. There are commit_size coordinates, one per
    # commitment coordinate rather than one per message coordinate, because
    # e is added after A*m. The result is in centered representation and the
    # caller reduces modulo q. The error is what makes the commitment
    # hiding; its smallness is what keeps the norm bound in the binding
    # argument tight.
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
    # second time. Tampering with either the message or the error moves at
    # least one coordinate and is caught with probability one here; it is
    # the hardness of finding two openings that agree, not any probabilistic
    # check, that carries binding.
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
    one is infeasible under Module-SIS, so this routine exists to
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
