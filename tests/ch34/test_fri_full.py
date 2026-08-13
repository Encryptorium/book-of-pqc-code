"""Tests for starks.fri_full."""

from __future__ import annotations

import random

import pytest

from starks.arithmetization import (
    DEFAULT_PRIME,
    TRACE_LENGTH,
    fibonacci_trace,
    interpolate_trace,
)
from starks.fri_full import (
    QueryOpening,
    _fold_codeword,
    commit_codeword,
    fri_prove,
    fri_verify,
)
from starks.lde import extend_polynomial, lde_domain, mod_inv, trace_domain
from starks.transcript import Transcript


def _honest_codeword():
    prime = DEFAULT_PRIME
    coeffs = interpolate_trace(fibonacci_trace(), trace_domain(), prime)
    return extend_polynomial(coeffs, lde_domain(), prime), lde_domain()


def test_merkle_digests_are_256_bit():
    """Pin the Merkle digest width the eps_bind term is priced against.

    Table 34.2 tells the reader that Merkle hash width governs the BHT
    and CNPS bounds on eps_bind, so the width is a security parameter
    and not an implementation detail. Every other test here checks that
    roots compare equal or unequal, which is true at any width. The
    module carried a DIGEST_BYTES = 32 constant that nothing read, so
    the number a reader would have trusted was decorative; this asserts
    the width the code actually produces.
    """
    codeword, _ = _honest_codeword()
    root, levels = commit_codeword(codeword, DEFAULT_PRIME)
    assert len(root) == 32
    assert all(len(node) == 32 for level in levels for node in level)


def test_commit_codeword_deterministic():
    codeword = [1, 2, 3, 4]
    r1, _ = commit_codeword(codeword, DEFAULT_PRIME)
    r2, _ = commit_codeword(codeword, DEFAULT_PRIME)
    assert r1 == r2


def test_commit_codeword_different_on_change():
    codeword = [1, 2, 3, 4]
    r1, _ = commit_codeword(codeword, DEFAULT_PRIME)
    r2, _ = commit_codeword([1, 2, 3, 5], DEFAULT_PRIME)
    assert r1 != r2


def test_commit_codeword_non_power_of_two_raises():
    with pytest.raises(ValueError):
        commit_codeword([1, 2, 3], DEFAULT_PRIME)


def test_commit_codeword_empty_raises():
    with pytest.raises(ValueError):
        commit_codeword([], DEFAULT_PRIME)


def test_fri_roundtrip_honest_codeword_accepts():
    codeword, dom = _honest_codeword()
    prime = DEFAULT_PRIME
    prover_transcript = Transcript(b"fri-test")
    proof = fri_prove(
        initial_codeword=codeword,
        initial_domain=dom,
        prime=prime,
        transcript=prover_transcript,
        num_queries=6,
        grinding_bits=4,
    )
    verifier_transcript = Transcript(b"fri-test")
    assert fri_verify(
        proof=proof,
        initial_domain=dom,
        prime=prime,
        transcript=verifier_transcript,
        num_queries=6,
        grinding_bits=4,
    )


def test_fri_rejects_corrupted_final_codeword():
    codeword, dom = _honest_codeword()
    prime = DEFAULT_PRIME
    prover_transcript = Transcript(b"fri-test")
    proof = fri_prove(
        initial_codeword=codeword,
        initial_domain=dom,
        prime=prime,
        transcript=prover_transcript,
        num_queries=4,
        grinding_bits=0,
    )
    proof.final_codeword[0] = (proof.final_codeword[0] + 1) % prime
    verifier_transcript = Transcript(b"fri-test")
    assert not fri_verify(
        proof=proof,
        initial_domain=dom,
        prime=prime,
        transcript=verifier_transcript,
        num_queries=4,
        grinding_bits=0,
    )


def test_fri_rejects_corrupted_query_leaf():
    codeword, dom = _honest_codeword()
    prime = DEFAULT_PRIME
    prover_transcript = Transcript(b"fri-test")
    proof = fri_prove(
        initial_codeword=codeword,
        initial_domain=dom,
        prime=prime,
        transcript=prover_transcript,
        num_queries=4,
        grinding_bits=0,
    )
    # Corrupt the first query opening at round 0.
    opening = proof.query_openings[0][0]
    proof.query_openings[0][0] = QueryOpening(
        leaf_index=opening.leaf_index,
        leaf_value=(opening.leaf_value + 1) % prime,
        sibling_value=opening.sibling_value,
        merkle_path=opening.merkle_path,
    )
    verifier_transcript = Transcript(b"fri-test")
    assert not fri_verify(
        proof=proof,
        initial_domain=dom,
        prime=prime,
        transcript=verifier_transcript,
        num_queries=4,
        grinding_bits=0,
    )


def test_fri_rejects_wrong_grinding_nonce():
    codeword, dom = _honest_codeword()
    prime = DEFAULT_PRIME
    prover_transcript = Transcript(b"fri-test")
    proof = fri_prove(
        initial_codeword=codeword,
        initial_domain=dom,
        prime=prime,
        transcript=prover_transcript,
        num_queries=4,
        grinding_bits=6,
    )
    proof.grinding_nonce = proof.grinding_nonce + 1
    verifier_transcript = Transcript(b"fri-test")
    assert not fri_verify(
        proof=proof,
        initial_domain=dom,
        prime=prime,
        transcript=verifier_transcript,
        num_queries=4,
        grinding_bits=6,
    )


def test_fri_rejects_adversarial_random_codeword():
    # A random codeword is extremely unlikely to be close to any
    # degree-8 polynomial; FRI should reject with near certainty on the
    # toy parameters. We allow a few trials; all should reject.
    prime = DEFAULT_PRIME
    dom = lde_domain()
    random.seed(0)
    rejected = 0
    trials = 5
    for _ in range(trials):
        codeword = [random.randint(0, prime - 1) for _ in dom]
        prover_transcript = Transcript(b"fri-test")
        proof = fri_prove(
            initial_codeword=codeword,
            initial_domain=dom,
            prime=prime,
            transcript=prover_transcript,
            num_queries=6,
            grinding_bits=0,
        )
        verifier_transcript = Transcript(b"fri-test")
        ok = fri_verify(
            proof=proof,
            initial_domain=dom,
            prime=prime,
            transcript=verifier_transcript,
            num_queries=6,
            grinding_bits=0,
        )
        # A random codeword may by chance pass if it happens to be
        # close to a low-degree polynomial, but with 6 queries the
        # catch probability is high. Most trials reject.
        if not ok:
            rejected += 1
    assert rejected >= trials - 1


def test_fri_grinding_zero_bits_accepts_any_nonce():
    codeword, dom = _honest_codeword()
    prime = DEFAULT_PRIME
    prover_transcript = Transcript(b"fri-test")
    proof = fri_prove(
        initial_codeword=codeword,
        initial_domain=dom,
        prime=prime,
        transcript=prover_transcript,
        num_queries=4,
        grinding_bits=0,
    )
    # With 0 grinding bits, nonce == 0 is sufficient.
    assert proof.grinding_nonce == 0


def test_fri_prove_num_queries_zero_raises():
    codeword, dom = _honest_codeword()
    prime = DEFAULT_PRIME
    with pytest.raises(ValueError):
        fri_prove(
            initial_codeword=codeword,
            initial_domain=dom,
            prime=prime,
            transcript=Transcript(b"fri-test"),
            num_queries=0,
            grinding_bits=0,
        )


def test_fri_prove_negative_grinding_raises():
    codeword, dom = _honest_codeword()
    prime = DEFAULT_PRIME
    with pytest.raises(ValueError):
        fri_prove(
            initial_codeword=codeword,
            initial_domain=dom,
            prime=prime,
            transcript=Transcript(b"fri-test"),
            num_queries=4,
            grinding_bits=-1,
        )


def test_fri_prove_mismatched_lengths_raises():
    codeword = [1, 2, 3, 4]
    dom = [1, 2, 3, 4, 5, 6, 7, 8]
    with pytest.raises(ValueError):
        fri_prove(
            initial_codeword=codeword,
            initial_domain=dom,
            prime=DEFAULT_PRIME,
            transcript=Transcript(b"fri-test"),
            num_queries=1,
            grinding_bits=0,
        )


def test_mod_inv_zero_raises_from_fri_context():
    with pytest.raises(ValueError):
        mod_inv(0, DEFAULT_PRIME)


def test_fold_codeword_length_mismatch_raises():
    with pytest.raises(ValueError):
        _fold_codeword([1, 2, 3, 4], [1, 2], 3, DEFAULT_PRIME)


def test_fold_codeword_non_power_of_two_raises():
    with pytest.raises(ValueError):
        _fold_codeword([1, 2, 3], [1, 2, 3], 5, DEFAULT_PRIME)


def test_fri_verify_structural_checks():
    codeword, dom = _honest_codeword()
    prime = DEFAULT_PRIME
    prover_transcript = Transcript(b"fri-test")
    proof = fri_prove(
        initial_codeword=codeword,
        initial_domain=dom,
        prime=prime,
        transcript=prover_transcript,
        num_queries=4,
        grinding_bits=0,
    )
    # Malformed: drop a commitment.
    proof.commitments.pop()
    verifier_transcript = Transcript(b"fri-test")
    with pytest.raises(ValueError):
        fri_verify(
            proof=proof,
            initial_domain=dom,
            prime=prime,
            transcript=verifier_transcript,
            num_queries=4,
            grinding_bits=0,
        )
