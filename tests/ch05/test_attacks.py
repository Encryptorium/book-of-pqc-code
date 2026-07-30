"""The mauling attack, and the non-coprime bound from Exercise 3."""

import math
import random

import pytest

from kem_primitives.attacks import coprime_failure_bound, maul, recover
from kem_primitives.rsa_kem import TOY_P, TOY_Q, decap, encap, keygen


def test_mauling_recovers_the_encapsulated_key():
    """Exercise 2: blind, query the oracle, divide by r, read back K."""
    pk, sk = keygen()
    n, _ = pk
    c, K = encap(pk, random.Random(7))
    r = 12345
    assert math.gcd(r, n) == 1
    oracle_answer = decap(sk, maul(pk, c, r))
    assert recover(pk, oracle_answer, r) == K


def test_the_oracle_answer_is_r_times_the_key():
    """The decapsulation oracle returns r * K mod n, a function of K."""
    pk, sk = keygen()
    n, _ = pk
    c, K = encap(pk, random.Random(7))
    r = 12345
    assert decap(sk, maul(pk, c, r)) == (r * K) % n


def test_mauling_works_for_many_blinding_factors():
    pk, sk = keygen()
    n, _ = pk
    c, K = encap(pk, random.Random(31))
    for r in (2, 3, 7, 65537, 2**31 - 1, n - 2):
        if math.gcd(r, n) != 1 or r == 1:
            continue
        assert recover(pk, decap(sk, maul(pk, c, r)), r) == K


def test_the_mauled_ciphertext_differs_from_the_original():
    pk, _ = keygen()
    c, _ = encap(pk, random.Random(7))
    assert maul(pk, c, 12345) != c


def test_maul_is_a_valid_encryption_of_r_times_the_key():
    """Textbook RSA is multiplicatively homomorphic, which is the whole flaw."""
    pk, _ = keygen()
    n, e = pk
    c, K = encap(pk, random.Random(7))
    r = 999
    assert maul(pk, c, r) == pow((K * r) % n, e, n)


def test_recover_needs_an_invertible_blinding_factor():
    """A non-invertible r has no inverse mod n, so recovery cannot run.

    Note which quantity this is about: the attacker-chosen blinding factor
    r, not the encapsulated key K. Decapsulation correctness needs neither.
    And the attacker picks r, so this is a precondition rather than a
    failure rate; see test_two_is_always_an_invertible_choice.
    """
    pk, _ = keygen()
    n, _ = pk
    p = 3184935163
    assert math.gcd(p, n) != 1
    with pytest.raises(ValueError):
        recover(pk, 42, p)


def test_an_invertible_r_can_still_produce_a_forbidden_query():
    """"Any invertible r != 1" does not guarantee an admissible CCA query.

    The CCA oracle refuses the challenge ciphertext, so the attack needs
    c' != c. Take K = p and choose r by CRT as 2 mod p and 1 mod q: that r
    is coprime to n and is not 1 mod n, yet mauling returns c unchanged,
    because c is 0 mod p and r^e is 1 mod q. The query is forbidden.
    """
    pk, _ = keygen()
    n, e = pk
    p, q = TOY_P, TOY_Q
    r = (2 * q * pow(q, -1, p) + 1 * p * pow(p, -1, q)) % n
    assert r % p == 2 and r % q == 1
    assert math.gcd(r, n) == 1
    assert r % n != 1
    c = pow(p, e, n)          # the challenge ciphertext for K = p
    assert maul(pk, c, r) == c


def test_r_equals_two_never_collides_under_any_valid_rsa_key():
    """r = 2 keeps c' != c for every K, under every valid two-prime RSA key.

    This is a theorem, not a property of the chapter's modulus. A collision
    needs c*(2^e - 1) = 0 mod n. c is never 0 mod n for K in [1, n-1], so
    some prime l does not divide c and the collision would need
    2^e = 1 mod l. Because d exists, e is invertible mod (p-1)(q-1), so
    gcd(e, l-1) = 1; then ord_l(2) divides both e and l-1, hence divides 1,
    forcing 2 = 1 mod l, which no prime allows.
    """
    pk, _ = keygen()
    n, e = pk
    assert math.gcd(e, TOY_P - 1) == 1 and math.gcd(e, TOY_Q - 1) == 1
    assert pow(2, e, TOY_P) != 1 and pow(2, e, TOY_Q) != 1
    for K in (1, 2, TOY_P, TOY_Q, 2 * TOY_P, 3 * TOY_Q, n - 1, 12345):
        c = pow(K, e, n)
        assert maul(pk, c, 2) != c


def test_r_equals_two_is_collision_free_across_many_rsa_keys():
    """The generality claim, checked exhaustively on small keys.

    For every valid (p, q, e) below, gcd(e, p-1) = gcd(e, q-1) = 1 implies
    2^e != 1 mod either prime, and r = 2 collides for no K at all.
    """
    small_primes = [n for n in range(3, 120, 2)
                    if all(n % d for d in range(3, int(n**0.5) + 1, 2))]
    seen = 0
    for p in small_primes:
        for q in small_primes:
            if p == q:
                continue
            phi = (p - 1) * (q - 1)
            for e in (3, 5, 17, 257):
                if math.gcd(e, phi) != 1:
                    continue
                seen += 1
                assert pow(2, e, p) != 1 and pow(2, e, q) != 1
                n = p * q
                pk = (n, e)
                for K in range(1, n):
                    c = pow(K, e, n)
                    assert maul(pk, c, 2) != c
    assert seen > 100, f"expected a broad sample, checked only {seen}"


def test_the_attack_recovers_non_coprime_keys_too():
    """K = p and K = q are recovered exactly, with r = 2.

    Coprimality of K is irrelevant to the attack; only the blinding factor
    has to be invertible.
    """
    pk, sk = keygen()
    n, e = pk
    for K in (TOY_P, TOY_Q, 2 * TOY_P):
        c = pow(K, e, n)
        assert recover(pk, decap(sk, maul(pk, c, 2)), 2) == K


def test_two_is_always_an_invertible_choice():
    """The attacker never has to search for an invertible r.

    An RSA modulus is a product of two odd primes, so 2 is coprime to it,
    so r = 2 is invertible with no test. This is why the non-coprime
    fraction of K is not the attack's failure rate: the attack has none.
    """
    pk, sk = keygen()
    n, _ = pk
    assert n % 2 == 1
    assert math.gcd(2, n) == 1
    c, K = encap(pk, random.Random(7))
    assert recover(pk, decap(sk, maul(pk, c, 2)), 2) == K


def test_coprime_failure_bound_matches_the_appendix_rows():
    """Appendix D prints these three rows to three significant figures."""
    assert f"{coprime_failure_bound(53, 61):.3e}" == "3.465e-02"
    assert f"{coprime_failure_bound(1009, 1013):.3e}" == "1.976e-03"
    assert f"{coprime_failure_bound(3184935163, 3199286161):.3e}" == "6.265e-10"


def test_the_old_appendix_row_did_not_support_its_claim():
    """Appendix D's third row used to be (2^31-1, 2^31-19) and claimed the
    result was below 2^-30. It is not: those primes give 9.313225785e-10
    against 2^-30 = 9.313225746e-10, so the fraction EXCEEDS the bound. The
    row now uses the chapter's own primes, which do satisfy it. This test
    pins the reason the row changed so it cannot drift back.
    """
    assert coprime_failure_bound(2**31 - 1, 2**31 - 19) > 2.0**-30
    assert coprime_failure_bound(3184935163, 3199286161) < 2.0**-30


def test_coprime_failure_bound_is_exact_by_enumeration():
    """The closed form agrees with counting the bad K directly."""
    for p, q in [(5, 7), (11, 13), (53, 61)]:
        n = p * q
        bad = sum(1 for K in range(1, n) if math.gcd(K, n) != 1)
        assert bad == p + q - 2
        assert coprime_failure_bound(p, q) == bad / (n - 1)


def test_coprime_failure_bound_is_below_the_union_bound():
    """(p+q-2)/(n-1) < 1/p + 1/q, since p + q < 2n."""
    for p, q in [(5, 7), (1009, 1013), (3184935163, 3199286161)]:
        assert coprime_failure_bound(p, q) < 1 / p + 1 / q


def test_the_chapter_primes_land_below_2_to_the_minus_30():
    """The chapter's claim is about its own 32-bit primes, and holds for them."""
    p, q = 3184935163, 3199286161
    assert coprime_failure_bound(p, q) < 2.0**-30
    assert 1 / p + 1 / q < 2.0**-30
