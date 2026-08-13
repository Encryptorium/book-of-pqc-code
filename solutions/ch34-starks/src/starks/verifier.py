"""End-to-end STARK verifier for Chapter 34.

Accepts a STARK proof plus the AIR the trace claims to satisfy, and
replays the three checks that bind the four stages of the pipeline:

1. AIR constraints hold on the sent trace (L1 check).
2. The Lagrange interpolation of the trace agrees with the committed
   codeword at every FRI query position (L1-to-L2 consistency).
3. The codeword is close to a polynomial of degree less than the
   trace length (L2 FRI proximity).

The Fiat-Shamir transcript is reconstructed from scratch: the verifier
seeds with the same domain separator, the AIR parameters, and the
trace, then replays the FRI transcript interactions. This is the L4
non-interactivity check.

The verifier returns ``True`` on accept and ``False`` on any soundly-
formed-but-incorrect proof. It raises ``ValueError`` only on
structurally malformed proofs (wrong list lengths, non-matching domain
sizes), following Chapter 34's error contract.
"""

from __future__ import annotations

from .arithmetization import AIR, evaluate_air, interpolate_trace
from .fri_full import fri_verify
from .lde import (
    COSET_SHIFT,
    DEFAULT_PRIME,
    LDE_GENERATOR,
    LDE_SIZE,
    TRACE_DOMAIN_GENERATOR,
    eval_poly,
    lde_domain,
    trace_domain,
)
from .prover import STARKProof
from .transcript import Transcript


def stark_verify(
    air: AIR,
    proof: STARKProof,
    num_queries: int,
    grinding_bits: int,
    prime: int = DEFAULT_PRIME,
    domain_sep: bytes = b"ch34-stark",
    lde_size: int = LDE_SIZE,
    trace_generator: int = TRACE_DOMAIN_GENERATOR,
    lde_generator: int = LDE_GENERATOR,
    coset_shift: int = COSET_SHIFT,
) -> bool:
    """Verify a STARK proof against ``air``.

    Returns ``True`` on accept and ``False`` on any correctness failure.
    Raises ``ValueError`` for structurally malformed proofs.
    """
    if num_queries < 1:
        raise ValueError("num_queries must be at least one")
    if grinding_bits < 0:
        raise ValueError("grinding_bits must be non-negative")
    if len(proof.trace) != air.trace_length:
        raise ValueError("proof trace length does not match AIR")
    if proof.trace_commitment != proof.fri_proof.commitments[0]:
        return False

    # Stage 1: AIR check directly on the trace.
    residues = evaluate_air(air, proof.trace)
    if any(r != 0 for r in residues):
        return False

    # Rebuild the trace polynomial and the LDE domain.
    t_domain = trace_domain(
        generator=trace_generator, length=air.trace_length, prime=prime
    )
    coeffs = interpolate_trace(proof.trace, t_domain, prime)
    l_domain = lde_domain(
        size=lde_size,
        generator=lde_generator,
        coset_shift=coset_shift,
        prime=prime,
    )

    # Rebuild the verifier transcript with the exact same seed material.
    transcript = Transcript(domain_sep=domain_sep)
    transcript.absorb_int(b"prime", prime, num_bytes=8)
    transcript.absorb_int(b"trace-length", air.trace_length, num_bytes=8)
    transcript.absorb_int(b"lde-size", lde_size, num_bytes=8)
    for v in proof.trace:
        transcript.absorb_int(b"trace-value", v, num_bytes=8)

    # Stage 3: verify the FRI proximity proof. This replays the FRI
    # transcript and checks every fold-consistency and Merkle opening.
    fri_ok = fri_verify(
        proof=proof.fri_proof,
        initial_domain=l_domain,
        prime=prime,
        transcript=transcript,
        num_queries=num_queries,
        grinding_bits=grinding_bits,
    )
    if not fri_ok:
        return False

    # Stage 2: consistency between the Lagrange-interpolated trace
    # polynomial and the opened codeword values at every query position.
    initial_openings = proof.fri_proof.query_openings[0]
    if len(initial_openings) != num_queries:
        raise ValueError("FRI proof query count does not match num_queries")
    for opening in initial_openings:
        q = opening.leaf_index
        if q < 0 or q >= lde_size:
            raise ValueError("query index out of LDE range")
        expected = eval_poly(coeffs, l_domain[q], prime)
        if expected != opening.leaf_value:
            return False

    return True
