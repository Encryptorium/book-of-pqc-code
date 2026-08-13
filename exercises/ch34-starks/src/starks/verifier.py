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
    # EXERCISE: implement this function.
    #
    # Three checks over a transcript rebuilt from scratch. Check the AIR
    # directly on the sent trace. Reconstruct the trace polynomial and the
    # LDE domain, seed a transcript with exactly the material the prover
    # absorbed in exactly that order, and run fri_verify for proximity. Then
    # check consistency: at every round-0 query position the opened codeword
    # value must equal the trace polynomial evaluated at that LDE point,
    # which is what binds the sent trace to the committed codeword in the
    # absence of a composition polynomial. Two distinct polynomials of
    # degree below L agree at no more than L - 1 of the N LDE points, so
    # each query misses with probability at most (L - 1) / N and mu
    # independent queries miss with at most that to the mu. Return False for
    # a proof that is well formed but wrong, including a trace_commitment
    # that does not match the FRI proof's first root; raise ValueError only
    # for structural malformation.
    #
    # Reference: Chapter 34, '4.5 Prover and verifier wiring' (Block 5)
    #
    # Proved by:
    #   tests/ch34/test_stark_roundtrip.py
    raise NotImplementedError("exercise: stark_verify")
