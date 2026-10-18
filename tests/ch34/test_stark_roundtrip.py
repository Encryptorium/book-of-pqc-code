"""End-to-end STARK prover/verifier tests."""

from __future__ import annotations

import pytest

from starks.arithmetization import (
    DEFAULT_PRIME,
    evaluate_air,
    fibonacci_air,
    fibonacci_trace,
    interpolate_trace,
)
from starks.fri_full import fri_prove, fri_verify
from starks.lde import eval_poly, extend_polynomial, lde_domain, trace_domain
from starks.prover import STARKProof, stark_prove
from starks.transcript import Transcript
from starks.verifier import stark_verify


def test_honest_proof_accepts():
    air = fibonacci_air()
    trace = fibonacci_trace()
    proof = stark_prove(air, trace, num_queries=6, grinding_bits=4)
    assert stark_verify(air, proof, num_queries=6, grinding_bits=4)


def test_honest_proof_accepts_with_zero_grinding():
    air = fibonacci_air()
    trace = fibonacci_trace()
    proof = stark_prove(air, trace, num_queries=4, grinding_bits=0)
    assert stark_verify(air, proof, num_queries=4, grinding_bits=0)


def test_prover_rejects_bogus_trace():
    air = fibonacci_air()
    bad_trace = [1, 1, 2, 3, 5, 8, 13, 22]  # last entry wrong
    with pytest.raises(ValueError):
        stark_prove(air, bad_trace, num_queries=4, grinding_bits=0)


def test_verifier_rejects_trace_tampering():
    air = fibonacci_air()
    trace = fibonacci_trace()
    proof = stark_prove(air, trace, num_queries=6, grinding_bits=0)
    # Tamper with the trace in the proof (still Fibonacci-satisfying?
    # No: flipping one value breaks the recurrence).
    proof.trace[4] = (proof.trace[4] + 1) % DEFAULT_PRIME
    assert not stark_verify(air, proof, num_queries=6, grinding_bits=0)


def test_consistency_check_rejects_the_lde_of_another_trace():
    # Chapter 34's Block 6. The proof sends the honest trace but commits the
    # LDE of a trace with one value changed. The sent trace satisfies the
    # AIR and the committed word is a genuine low-degree codeword, so FRI
    # accepts it, and only the consistency check can reject the proof. The
    # two interpolants differ by a multiple of one Lagrange basis
    # polynomial, whose roots lie on the trace domain and so off the LDE
    # coset, so the check fails at every query position.
    air = fibonacci_air()
    trace = fibonacci_trace()
    other = list(trace)
    other[4] = (other[4] + 1) % DEFAULT_PRIME
    t_dom, l_dom = trace_domain(), lde_domain()
    honest_word = extend_polynomial(
        interpolate_trace(trace, t_dom, DEFAULT_PRIME), l_dom, DEFAULT_PRIME
    )
    swapped_word = extend_polynomial(
        interpolate_trace(other, t_dom, DEFAULT_PRIME), l_dom, DEFAULT_PRIME
    )
    assert all(a != b for a, b in zip(honest_word, swapped_word))

    def seeded_transcript():
        # The material stark_prove and stark_verify absorb before FRI.
        tx = Transcript(domain_sep=b"ch34-stark")
        tx.absorb_int(b"prime", DEFAULT_PRIME, num_bytes=8)
        tx.absorb_int(b"trace-length", air.trace_length, num_bytes=8)
        tx.absorb_int(b"lde-size", len(l_dom), num_bytes=8)
        for v in trace:
            tx.absorb_int(b"trace-value", v, num_bytes=8)
        return tx

    fri = fri_prove(
        initial_codeword=swapped_word,
        initial_domain=l_dom,
        prime=DEFAULT_PRIME,
        transcript=seeded_transcript(),
        num_queries=6,
        grinding_bits=4,
        degree_bound=air.trace_length,
    )
    proof = STARKProof(
        trace=list(trace), trace_commitment=fri.commitments[0], fri_proof=fri
    )
    assert not any(evaluate_air(air, proof.trace))
    assert fri_verify(
        proof=fri,
        initial_domain=l_dom,
        prime=DEFAULT_PRIME,
        transcript=seeded_transcript(),
        num_queries=6,
        grinding_bits=4,
        degree_bound=air.trace_length,
    )
    coeffs = interpolate_trace(trace, t_dom, DEFAULT_PRIME)
    assert all(
        eval_poly(coeffs, l_dom[o.leaf_index], DEFAULT_PRIME) != o.leaf_value
        for o in fri.query_openings[0]
    )
    assert not stark_verify(air, proof, num_queries=6, grinding_bits=4)


def test_verifier_rejects_mismatched_commitment():
    air = fibonacci_air()
    trace = fibonacci_trace()
    proof = stark_prove(air, trace, num_queries=4, grinding_bits=0)
    # Tamper with the trace_commitment so it no longer matches
    # fri_proof.commitments[0]. The verifier should reject at the
    # structural check (not raise).
    proof.trace_commitment = b"\x00" * 32
    assert not stark_verify(air, proof, num_queries=4, grinding_bits=0)


def test_verifier_rejects_corrupted_grinding_nonce():
    air = fibonacci_air()
    trace = fibonacci_trace()
    proof = stark_prove(air, trace, num_queries=4, grinding_bits=6)
    proof.fri_proof.grinding_nonce = proof.fri_proof.grinding_nonce + 1
    assert not stark_verify(air, proof, num_queries=4, grinding_bits=6)


def test_verifier_rejects_trace_length_mismatch_structurally():
    air = fibonacci_air()
    trace = fibonacci_trace()
    proof = stark_prove(air, trace, num_queries=4, grinding_bits=0)
    proof.trace = proof.trace + [0]
    with pytest.raises(ValueError):
        stark_verify(air, proof, num_queries=4, grinding_bits=0)


def test_different_num_queries_raise_structural_error():
    # Prover and verifier must agree on num_queries. A mismatch is a
    # structural malformation of the proof from the verifier's view:
    # the query opening lists have the wrong length, which the
    # verifier catches in the structural check and signals by raising.
    air = fibonacci_air()
    trace = fibonacci_trace()
    proof = stark_prove(air, trace, num_queries=6, grinding_bits=0)
    with pytest.raises(ValueError):
        stark_verify(air, proof, num_queries=4, grinding_bits=0)


def test_domain_separation_binding():
    air = fibonacci_air()
    trace = fibonacci_trace()
    proof = stark_prove(
        air, trace, num_queries=4, grinding_bits=0, domain_sep=b"ctxA"
    )
    # Verifier using a different domain_sep diverges the transcript
    # from the first absorb; rejection is guaranteed.
    assert not stark_verify(
        air, proof, num_queries=4, grinding_bits=0, domain_sep=b"ctxB"
    )


def test_stark_prove_invalid_params_raise():
    air = fibonacci_air()
    trace = fibonacci_trace()
    with pytest.raises(ValueError):
        stark_prove(air, trace, num_queries=0, grinding_bits=0)
    with pytest.raises(ValueError):
        stark_prove(air, trace, num_queries=4, grinding_bits=-1)


def test_stark_verify_invalid_params_raise():
    air = fibonacci_air()
    trace = fibonacci_trace()
    proof = stark_prove(air, trace, num_queries=4, grinding_bits=0)
    with pytest.raises(ValueError):
        stark_verify(air, proof, num_queries=0, grinding_bits=0)
    with pytest.raises(ValueError):
        stark_verify(air, proof, num_queries=4, grinding_bits=-1)
