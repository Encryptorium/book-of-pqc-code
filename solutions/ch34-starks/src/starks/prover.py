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
    if num_queries < 1:
        raise ValueError("num_queries must be at least one")
    if grinding_bits < 0:
        raise ValueError("grinding_bits must be non-negative")

    residues = evaluate_air(air, trace)
    if any(r != 0 for r in residues):
        raise ValueError("trace does not satisfy AIR constraints")

    t_domain = trace_domain(
        generator=trace_generator, length=air.trace_length, prime=prime
    )
    coeffs = interpolate_trace(trace, t_domain, prime)
    l_domain = lde_domain(
        size=lde_size,
        generator=lde_generator,
        coset_shift=coset_shift,
        prime=prime,
    )
    codeword = extend_polynomial(coeffs, l_domain, prime)

    transcript = Transcript(domain_sep=domain_sep)
    transcript.absorb_int(b"prime", prime, num_bytes=8)
    transcript.absorb_int(b"trace-length", air.trace_length, num_bytes=8)
    transcript.absorb_int(b"lde-size", lde_size, num_bytes=8)
    for v in trace:
        transcript.absorb_int(b"trace-value", v, num_bytes=8)

    fri = fri_prove(
        initial_codeword=codeword,
        initial_domain=l_domain,
        prime=prime,
        transcript=transcript,
        num_queries=num_queries,
        grinding_bits=grinding_bits,
    )

    return STARKProof(
        trace=list(trace),
        trace_commitment=fri.commitments[0],
        fri_proof=fri,
    )
