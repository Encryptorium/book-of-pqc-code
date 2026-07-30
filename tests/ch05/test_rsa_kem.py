"""The toy RSA-KEM: the chapter's printed round-trip and its exactness claim."""

import random

from kem_primitives.rsa_kem import TOY_E, TOY_P, TOY_Q, decap, encap, keygen


def test_chapter_block_round_trips_under_seed_7():
    """The chapter's block prints "True" then "True" for random.Random(7)."""
    pk, sk = keygen()
    rng = random.Random(7)
    c, K_alice = encap(pk, rng)
    K_bob = decap(sk, c)
    assert K_alice == K_bob
    assert 0 < K_bob < pk[0]


def test_round_trip_over_many_seeds():
    pk, sk = keygen()
    for seed in range(200):
        c, K = encap(pk, random.Random(seed))
        assert decap(sk, c) == K


def test_modulus_is_64_bits():
    """Two 32-bit primes, so n comes out 64 bits wide, as the chapter says."""
    pk, _ = keygen()
    n = pk[0]
    assert n == TOY_P * TOY_Q
    assert n.bit_length() == 64
    assert TOY_P.bit_length() == 32
    assert TOY_Q.bit_length() == 32


def test_public_exponent_is_65537():
    pk, _ = keygen()
    assert pk[1] == TOY_E == 65537


def test_private_exponent_inverts_the_public_one():
    _, sk = keygen()
    phi = (TOY_P - 1) * (TOY_Q - 1)
    assert (sk[1] * TOY_E) % phi == 1


def test_correctness_is_exact_for_non_coprime_keys():
    """The chapter claims decapsulation is exact for *every* K in [1, n-1].

    Textbook RSA recovers the residue mod pq for all inputs, not only those
    coprime to n, by Fermat's little theorem mod p and mod q separately
    (trivially when p divides K) and then CRT. These K all share a factor
    with n, so Euler's theorem alone does not cover them.
    """
    pk, sk = keygen()
    n, e = pk
    for K in (TOY_P, TOY_Q, 2 * TOY_P, 3 * TOY_Q, (TOY_Q - 1) * TOY_P):
        assert 1 <= K <= n - 1
        assert K % TOY_P == 0 or K % TOY_Q == 0
        assert decap(sk, pow(K, e, n)) == K


def test_correctness_at_the_range_endpoints():
    pk, sk = keygen()
    n, e = pk
    for K in (1, 2, n - 2, n - 1):
        assert decap(sk, pow(K, e, n)) == K


def test_encap_stays_inside_the_range():
    pk, _ = keygen()
    n = pk[0]
    for seed in range(50):
        _, K = encap(pk, random.Random(seed))
        assert 1 <= K <= n - 1


def test_encap_is_deterministic_given_the_rng_seed():
    """Two encapsulations from equally seeded generators agree.

    This is a statement about the seeded demo generator, not a security
    property: reusing randomness in a real KEM is a defect.
    """
    pk, _ = keygen()
    assert encap(pk, random.Random(11)) == encap(pk, random.Random(11))


def test_encap_output_is_a_valid_ciphertext_of_its_key():
    pk, _ = keygen()
    n, e = pk
    c, K = encap(pk, random.Random(3))
    assert c == pow(K, e, n)


def test_keygen_accepts_other_prime_pairs():
    pk, sk = keygen(p=1009, q=1013, e=17)
    n, e = pk
    assert n == 1009 * 1013
    for K in (1, 5, 1009, 1013, n - 1):
        assert decap(sk, pow(K, e, n)) == K
