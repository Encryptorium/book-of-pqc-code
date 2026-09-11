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
    FRIProof,
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
        sibling_path=opening.sibling_path,
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
    # toy parameters. Five trials, and the threshold below is four of
    # five; five trials support no stronger statistical claim than that.
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


def test_zero_bit_grinding_prover_chooses_zero_nonce():
    """At zero difficulty the prover stops at the first nonce it tries.

    This is about the prover, not the verifier, which is never called
    here. The work predicate does accept any nonce at zero difficulty,
    but the nonce also enters the transcript and determines the query
    positions, so swapping it after the fact is not something a proof
    survives in general.
    """
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


def _monomial_codeword(degree: int):
    prime = DEFAULT_PRIME
    coeffs = [0] * degree + [1]
    return extend_polynomial(coeffs, lde_domain(), prime), lde_domain()


def _fri_accepts(codeword, dom, **kwargs) -> bool:
    prime = DEFAULT_PRIME
    proof = fri_prove(
        initial_codeword=codeword,
        initial_domain=dom,
        prime=prime,
        transcript=Transcript(b"fri-degree"),
        num_queries=32,
        grinding_bits=0,
        **kwargs,
    )
    return fri_verify(
        proof=proof,
        initial_domain=dom,
        prime=prime,
        transcript=Transcript(b"fri-degree"),
        num_queries=32,
        grinding_bits=0,
        **kwargs,
    )


def test_fri_round_count_enforces_the_trace_length_degree_bound():
    # Track 2 round 10, R10-P1-03. Each fold halves the degree bound. The
    # pair below pins the monomial boundary: x^7 must pass three folds and
    # x^8 must not. "r folds then a constancy check accept exactly
    # degree < 2^r" is the intent, not a theorem: a bad fold challenge can
    # flatten a higher-degree polynomial anyway. Over F_97 with beta = 3,
    # x^9 - 3x^8 folds to zero. Soundness is what bounds how often that
    # happens, and these two fixtures are witnesses for the round-count
    # regression rather than a deterministic equivalence.
    # The STARK claims degree < TRACE_LENGTH = 8 on the 32-point LDE, so
    # the round count must be log_2(8) = 3: x^7 is the highest honest
    # degree and must pass, x^8 is the first dishonest one and must fail.
    # A fourth fold also flattens x^8 (degree < 16 becomes constant), so
    # the old default of log_2(N) - 1 = 4 accepted a rate-1/2 code where
    # the chapter claims rate 1/4. 32 query draws are made, with
    # replacement, so this is not a statement about query luck at these
    # fixtures; it is not exhaustive coverage either, since x^7 yields
    # only 23 distinct initial positions among the 32 draws.
    x7, dom = _monomial_codeword(7)
    x8, _ = _monomial_codeword(8)

    assert _fri_accepts(x7, dom, num_rounds=3)
    assert not _fri_accepts(x8, dom, num_rounds=3)
    # One fold too many erases the distinction: this is the defect.
    assert _fri_accepts(x8, dom, num_rounds=4)

    # The defaults must behave as three rounds, not four.
    assert _fri_accepts(x7, dom)
    assert not _fri_accepts(x8, dom)
    assert _fri_accepts(x7, dom, degree_bound=TRACE_LENGTH)
    assert not _fri_accepts(x8, dom, degree_bound=TRACE_LENGTH)


def test_fri_degree_bound_validation():
    codeword, dom = _honest_codeword()
    for bad in (0, 1, 3, 32, 64):
        with pytest.raises(ValueError):
            _fri_accepts(codeword, dom, degree_bound=bad)
    # num_rounds and degree_bound are two ways of saying one thing.
    with pytest.raises(ValueError):
        _fri_accepts(codeword, dom, degree_bound=8, num_rounds=3)


def test_fri_default_degree_bound_on_four_point_domain():
    # The smallest domain the package accepts is four points, where the
    # rate-1/4 default would be a degree bound of 1 and zero folds; the
    # default floors at 2, one fold, so a default call still proves.
    prime = DEFAULT_PRIME
    dom = [1, 22, 96, 75]  # order-4 subgroup of F_97: 22^2 = -1, dom[i + 2] = -dom[i]
    line = [(7 + 3 * x) % prime for x in dom]
    assert _fri_accepts(line, dom)
    quadratic = [(x * x) % prime for x in dom]
    assert not _fri_accepts(quadratic, dom)


def _fri_kwargs(num_queries, grinding_bits, **extra):
    return dict(num_queries=num_queries, grinding_bits=grinding_bits, **extra)


def test_fri_rejects_corrupted_sibling_value():
    # Track 2 round 12, P1-01. The fold equation reads two values per
    # query, and the verifier authenticated only one of them: the
    # sibling was trusted because "the next round's commitment binds
    # it", which is false, since a prover who picks the sibling picks
    # the folded value and then commits to whatever that produces.
    # An honest proof with one sibling value nudged must fail. This
    # test does not pin the sibling path check on its own: a lone
    # nudge also breaks the fold equation, so a verifier without the
    # path check rejects it too (round 13). The pin is the degree
    # forgery below, whose siblings satisfy the fold equation.
    codeword, dom = _honest_codeword()
    prime = DEFAULT_PRIME
    proof = fri_prove(codeword, dom, prime, Transcript(b"fri-test"), 4, 0)
    opening = proof.query_openings[0][0]
    proof.query_openings[0][0] = QueryOpening(
        leaf_index=opening.leaf_index,
        leaf_value=opening.leaf_value,
        sibling_value=(opening.sibling_value + 1) % prime,
        merkle_path=opening.merkle_path,
        sibling_path=opening.sibling_path,
    )
    assert not fri_verify(proof, dom, prime, Transcript(b"fri-test"), 4, 0)


def test_fri_rejects_unbound_sibling_forgery_of_degree_claim():
    # Track 2 round 12, P1-01, the reviewer's counterexample. Commit
    # the evaluations of x^8 + c (degree 8) under a degree-below-8
    # claim with the corrected three-fold schedule. Every queried leaf
    # and every leaf path is genuine; every later codeword is the zero
    # vector, honestly committed; and each round's sibling value is
    # CHOSEN so that the fold lands on zero. Before the fix the
    # verifier accepted this over 32 query draws. The forged
    # openings carry the genuine path of the position the fake value
    # claims to sit at, which is the strongest form the forgery can
    # take: the value is wrong and everything around it is right.
    from starks.fri_full import FRIProof, _merkle_path, _squeeze_beta

    prime = DEFAULT_PRIME
    dom = lde_domain()
    n = len(dom)
    rounds = 3
    queries = 32
    two_inv = mod_inv(2, prime)

    for shift in range(prime):
        codewords = [[(pow(x, 8, prime) + shift) % prime for x in dom]]
        codewords += [[0] * (n >> (j + 1)) for j in range(rounds)]
        domains = [list(dom)]
        transcript = Transcript(b"fri-forge")
        commitments, trees, betas = [], [], []
        for j, cw in enumerate(codewords):
            root, tree = commit_codeword(cw, prime)
            commitments.append(root)
            trees.append(tree)
            # Round 0 is labelled with the ASCII "0", later rounds with a
            # four-byte index; the verifier does the same. Round 13 found
            # this forgery labelling round 0 with four bytes, which made
            # the verifier reject it at the position check, before the
            # sibling check it exists to exercise.
            label = b"fri-commit-0" if j == 0 else b"fri-commit-" + j.to_bytes(4, "big")
            transcript.absorb(label, root)
            if j < rounds:
                betas.append(_squeeze_beta(transcript, prime, j))
                domains.append([x * x % prime for x in domains[-1][: len(cw) // 2]])
        if betas[0] in set(dom):
            continue  # degenerate beta: a fold coefficient vanishes
        # Grinding at g = 0 is the nonce 0, absorbed before the queries.
        transcript.absorb_int(b"fri-grinding", 0, num_bytes=8)
        positions = [
            transcript.squeeze_index(b"fri-query-" + k.to_bytes(4, "big"), n)
            for k in range(queries)
        ]
        openings = []
        for j, cw in enumerate(codewords):
            size = len(cw)
            half = size // 2
            row = []
            for q in positions:
                idx = q % size
                sib = (idx + half) % size
                leaf, sibling = cw[idx], cw[sib]
                if j < rounds:
                    x = domains[j][idx % half]
                    ratio = betas[j] * mod_inv(x, prime) % prime
                    a = (1 + ratio) * two_inv % prime
                    b = (1 - ratio) * two_inv % prime
                    # Solve a * f(x) + b * f(-x) = 0 for the free input.
                    if idx < half:
                        sibling = (-a * leaf * mod_inv(b, prime)) % prime
                    else:
                        sibling = (-b * leaf * mod_inv(a, prime)) % prime
                row.append(
                    QueryOpening(
                        leaf_index=idx,
                        leaf_value=leaf,
                        sibling_value=sibling,
                        merkle_path=_merkle_path(trees[j], idx),
                        sibling_path=_merkle_path(trees[j], sib),
                    )
                )
            openings.append(row)
        forged = FRIProof(commitments, openings, codewords[-1], 0)
        assert not fri_verify(
            forged, dom, prime, Transcript(b"fri-forge"), queries, 0, degree_bound=8
        )
        break
    else:  # pragma: no cover
        raise AssertionError("no non-degenerate beta found")


def test_fri_grinding_nonce_decides_the_query_positions():
    # Track 2 round 12, P1-02. Grinding is priced as 2^g work per
    # query set a forger gets to see, which is only true if the nonce
    # is absorbed BEFORE the positions are squeezed. The old order
    # squeezed the positions first and ground last, so proofs at g = 0
    # and g = 12 carried identical openings and differed in the nonce
    # alone: a forger could search for a favourable query set for free
    # and pay the proof of work once at the end.
    codeword, dom = _honest_codeword()
    prime = DEFAULT_PRIME
    p0 = fri_prove(codeword, dom, prime, Transcript(b"fri-test"), 8, 0)
    p12 = fri_prove(codeword, dom, prime, Transcript(b"fri-test"), 8, 12)
    assert p0.grinding_nonce == 0 and p12.grinding_nonce != 0
    assert fri_verify(p0, dom, prime, Transcript(b"fri-test"), 8, 0)
    assert fri_verify(p12, dom, prime, Transcript(b"fri-test"), 8, 12)
    positions0 = [o.leaf_index for o in p0.query_openings[0]]
    positions12 = [o.leaf_index for o in p12.query_openings[0]]
    assert positions0 != positions12
    # And a nonce that did not pay for these positions is refused even
    # when it satisfies the trailing-zero test on some other state.
    p12.grinding_nonce = p0.grinding_nonce
    assert not fri_verify(p12, dom, prime, Transcript(b"fri-test"), 8, 12)


def test_fri_malformed_proof_shapes_raise():
    # Round 13. The docstring promises ValueError for a structurally
    # malformed proof; a resized final layer and a wrong-length Merkle
    # path were rejected by value instead, and an out-of-range nonce
    # surfaced as OverflowError. None accepted anything; the contract
    # is what changed.
    codeword, dom = _honest_codeword()
    prime = DEFAULT_PRIME
    proof = fri_prove(codeword, dom, prime, Transcript(b"fri-test"), 4, 4)
    assert fri_verify(proof, dom, prime, Transcript(b"fri-test"), 4, 4)

    resized = FRIProof(
        proof.commitments, proof.query_openings,
        proof.final_codeword * 2, proof.grinding_nonce,
    )
    with pytest.raises(ValueError):
        fri_verify(resized, dom, prime, Transcript(b"fri-test"), 4, 4)

    opening = proof.query_openings[0][0]
    short = [row[:] for row in proof.query_openings]
    short[0][0] = QueryOpening(
        leaf_index=opening.leaf_index,
        leaf_value=opening.leaf_value,
        sibling_value=opening.sibling_value,
        merkle_path=opening.merkle_path[:-1],
        sibling_path=opening.sibling_path,
    )
    with pytest.raises(ValueError):
        fri_verify(FRIProof(proof.commitments, short, proof.final_codeword,
                            proof.grinding_nonce),
                   dom, prime, Transcript(b"fri-test"), 4, 4)

    for bad_nonce in (-1, 1 << 64):
        with pytest.raises(ValueError):
            fri_verify(FRIProof(proof.commitments, proof.query_openings,
                                proof.final_codeword, bad_nonce),
                       dom, prime, Transcript(b"fri-test"), 4, 4)
