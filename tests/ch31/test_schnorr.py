"""Tests for the Schnorr identification module of Chapter 31's opening."""

import pytest

from zk_layers.schnorr import G, N, P, extract, simulate, verify

X = 123
H_PUB = pow(G, X, P)


def respond(r, e):
    return (r + e * X) % N


def test_the_toy_group_has_prime_order_n():
    # N is prime and P = 2N + 1. G is not 1 and G^N = 1, so the order of G
    # divides the prime N and is N itself.
    assert all(N % d for d in range(2, int(N**0.5) + 1))
    assert P == 2 * N + 1
    assert G % P != 1
    assert pow(G, N, P) == 1


@pytest.mark.parametrize("r, e", [(789, 456), (0, 0), (1, N - 1)])
def test_an_honest_run_is_accepted(r, e):
    assert verify(H_PUB, pow(G, r, P), e, respond(r, e)) is True


def test_a_wrong_response_is_rejected():
    r, e = 789, 456
    assert verify(H_PUB, pow(G, r, P), e, (respond(r, e) + 1) % N) is False


@pytest.mark.parametrize("e1, e2", [(456, 31), (0, N - 1)])
def test_two_answers_to_one_commitment_give_away_the_secret(e1, e2):
    r = 789
    assert extract(e1, respond(r, e1), e2, respond(r, e2)) == X


def test_extraction_needs_two_different_challenges():
    r, e = 789, 456
    with pytest.raises(ValueError):
        extract(e, respond(r, e), e, respond(r, e))


@pytest.mark.parametrize("e, z", [(456, 500), (N - 1, 0)])
def test_a_simulated_transcript_is_accepted(e, z):
    assert verify(H_PUB, simulate(H_PUB, e, z), e, z) is True


@pytest.mark.parametrize("e", [0, 456, N - 1])
def test_real_and_simulated_transcripts_are_the_same_set(e):
    """The distributions agree, not only the acceptance.

    For a fixed challenge, r -> (r + e * x) mod N is a bijection of Z_N,
    so the N real transcripts over every nonce are N distinct triples,
    and the N simulated ones over every response are the same N. Each
    side, drawn uniformly, is the uniform distribution on that one set.
    """
    real = {(pow(G, r, P), e, respond(r, e)) for r in range(N)}
    simulated = {(simulate(H_PUB, e, z), e, z) for z in range(N)}
    assert len(real) == N
    assert real == simulated
