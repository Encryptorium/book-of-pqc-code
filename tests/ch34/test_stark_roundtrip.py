"""End-to-end STARK prover/verifier tests."""

from __future__ import annotations

import pytest

from starks.arithmetization import DEFAULT_PRIME, fibonacci_air, fibonacci_trace
from starks.prover import stark_prove
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
