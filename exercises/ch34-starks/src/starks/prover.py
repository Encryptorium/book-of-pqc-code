"""End-to-end STARK prover for Chapter 34.

Assembles the four stages of a FRI-based STARK over F_97 into a single
non-interactive proof. The prover accepts an AIR plus a trace, verifies
that the trace satisfies the AIR, interpolates the trace to a
polynomial on the order-8 trace domain, evaluates the polynomial on the
order-32 LDE coset to produce a Reed-Solomon codeword, Merkle-commits
the codeword, binds the commitment to a Fiat-Shamir transcript, runs
FRI to prove the codeword is close to a low-degree polynomial, and
appends a grinding nonce.

Pedagogical simplification
--------------------------

The toy sends the trace in the clear as part of the proof. A
production STARK hides the trace and uses an additional composition
polynomial (a random linear combination of the constraint quotients)
whose own LDE codeword is also Merkle-committed and FRI-proven. The
toy's role is to demonstrate the four-stage pipeline at minimal
complexity, not to implement privacy or optimize proof size. Chapter
35 connects the toy to Zcash, ZKsync, and Starknet, where the
production version is deployed.

The verifier side of the toy binds the sent trace to the committed
codeword by (i) checking AIR directly on the trace and (ii) checking
that every FRI-queried position of the codeword agrees with the
Lagrange interpolation of the sent trace at the corresponding LDE
point. The FRI proof then certifies that the committed codeword is
close to a polynomial of degree less than the trace length. Together,
the three checks force the prover to be honest about both the trace
and the codeword.
"""

from __future__ import annotations

from dataclasses import dataclass

from .arithmetization import AIR, evaluate_air, interpolate_trace
from .fri_full import FRIProof, fri_prove
from .lde import (
    COSET_SHIFT,
    DEFAULT_PRIME,
    LDE_GENERATOR,
    LDE_SIZE,
    TRACE_DOMAIN_GENERATOR,
    extend_polynomial,
    lde_domain,
    trace_domain,
)
from .transcript import Transcript


@dataclass
class STARKProof:
    """A toy STARK proof.

    ``trace`` is the public witness (pedagogical simplification; see
    module docstring). ``trace_commitment`` is the Merkle root of the
    LDE codeword. ``fri_proof`` is the FRI proximity proof. The FRI
    proof's per-round query openings double as the codeword openings
    the verifier uses to run consistency checks against the Lagrange
    interpolation of the trace, so no separate trace-query list is
    needed.
    """

    trace: list[int]
    trace_commitment: bytes
    fri_proof: FRIProof


def stark_prove(
    air: AIR,
    trace: list[int],
    num_queries: int,
    grinding_bits: int,
    prime: int = DEFAULT_PRIME,
    domain_sep: bytes = b"ch34-stark",
    lde_size: int = LDE_SIZE,
    trace_generator: int = TRACE_DOMAIN_GENERATOR,
    lde_generator: int = LDE_GENERATOR,
    coset_shift: int = COSET_SHIFT,
) -> STARKProof:
    """Produce a STARK proof for ``trace`` against ``air``.

    Steps:

    1. Verify ``trace`` satisfies every AIR constraint. Raises
       ``ValueError`` if not (the prover cannot produce a proof for a
       bogus witness).
    2. Interpolate the trace to a polynomial on the trace domain.
    3. Evaluate the polynomial on the LDE coset to produce the
       Reed-Solomon codeword.
    4. Merkle-commit the codeword.
    5. Run FRI on the codeword, binding to a Fiat-Shamir transcript
       seeded with the chapter domain separator, the AIR parameters,
       and the trace.

    Raises ``ValueError`` on invalid parameters or a non-satisfying
    trace.
    """
    # EXERCISE: implement this function.
    #
    # Assemble the four stages. Evaluate the AIR on the trace and refuse to
    # prove one with any nonzero residue, since a prover has no proof to
    # produce for a bogus witness. Interpolate the trace over the trace
    # domain, evaluate the resulting polynomial on the LDE coset for the
    # Reed-Solomon codeword, then seed a transcript with the domain
    # separator and absorb the prime, the trace length, the LDE size, and
    # every trace value before FRI starts, so every fold challenge is bound
    # to the public statement. Run fri_prove on the codeword and return the
    # trace, the FRI proof's round-0 root as the trace commitment, and the
    # proof itself. Reject num_queries below one and negative grinding bits.
    # The trace ships in the clear here: a production STARK hides it behind
    # a composition polynomial, and the toy drops that for compactness.
    #
    # Reference: Chapter 34, '4.5 Prover and verifier wiring' (Block 5)
    #
    # Proved by:
    #   tests/ch34/test_stark_roundtrip.py
    raise NotImplementedError("exercise: stark_prove")
