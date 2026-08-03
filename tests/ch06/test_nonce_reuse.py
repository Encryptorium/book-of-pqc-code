"""ECDSA nonce reuse: the chapter's toy group, and the key recovery."""

import pytest

from signature_attacks.nonce_reuse import (
    TOY_G,
    TOY_N,
    TOY_P,
    public_key,
    r_from_nonce,
    recover_and_check,
    recover_from_two_signatures,
    recover_key,
    recover_nonce,
    sign,
    verify,
)

CHAPTER_D = 7
CHAPTER_K = 6
CHAPTER_Z1 = 3
CHAPTER_Z2 = 5


def chapter_signatures():
    r = r_from_nonce(CHAPTER_K)
    s1 = sign(CHAPTER_Z1, CHAPTER_D, CHAPTER_K, r)
    s2 = sign(CHAPTER_Z2, CHAPTER_D, CHAPTER_K, r)
    return r, s1, s2


def test_chapter_block_prints_7_7_true():
    """The chapter's block prints "7 7 True": the recovered key is the real one."""
    r, s1, s2 = chapter_signatures()
    _, d_rec = recover_from_two_signatures(CHAPTER_Z1, s1, CHAPTER_Z2, s2, r)
    assert d_rec == CHAPTER_D


def test_chapter_block_intermediate_values():
    """r = 2, s1 = 1, s2 = 5 on the chapter's constants, and k recovers as 6."""
    r, s1, s2 = chapter_signatures()
    assert (r, s1, s2) == (2, 1, 5)
    assert recover_nonce(CHAPTER_Z1, CHAPTER_Z2, s1, s2) == CHAPTER_K


def test_chapter_block_assertions_hold():
    """The block asserts r != 0 and s1 != s2 before running the recovery."""
    r, s1, s2 = chapter_signatures()
    assert r != 0
    assert s1 != s2


def test_g_has_order_eleven_modulo_twenty_three():
    """The chapter's comment: 4 = 2^2 and (Z/23Z)^* has order 22, so ord(4) = 11."""
    assert pow(TOY_G, TOY_N, TOY_P) == 1
    assert [x for x in range(1, TOY_N + 1) if pow(TOY_G, x, TOY_P) == 1] == [TOY_N]


def test_the_scalar_order_is_prime():
    """Primality of N is what makes every nonzero difference invertible."""
    assert all(TOY_N % f for f in range(2, TOY_N))


def test_honest_signatures_verify():
    r, s1, s2 = chapter_signatures()
    y = public_key(CHAPTER_D)
    assert verify(CHAPTER_Z1, r, s1, y)
    assert verify(CHAPTER_Z2, r, s2, y)


def test_verify_rejects_a_signature_on_a_different_hash():
    r, s1, _ = chapter_signatures()
    y = public_key(CHAPTER_D)
    assert not verify(CHAPTER_Z2, r, s1, y)


def test_recovery_is_a_full_euf_cma_win():
    """The recovered key signs a fresh hash, and that signature verifies."""
    r, s1, s2 = chapter_signatures()
    _, d_rec = recover_from_two_signatures(CHAPTER_Z1, s1, CHAPTER_Z2, s2, r)
    fresh_z = 9
    fresh_r = r_from_nonce(4)
    forged = sign(fresh_z, d_rec, 4, fresh_r)
    assert verify(fresh_z, fresh_r, forged, public_key(CHAPTER_D))


def test_recovery_works_for_every_key_nonce_and_hash_pair():
    """Not a property of the chapter's constants: it is the algebra."""
    checked = 0
    for d in range(1, TOY_N):
        for k in range(1, TOY_N):
            r = r_from_nonce(k)
            if r == 0:
                continue
            for z1 in range(TOY_N):
                for z2 in range(TOY_N):
                    if z1 == z2:
                        continue
                    try:
                        s1 = sign(z1, d, k, r)
                        s2 = sign(z2, d, k, r)
                    except ValueError:
                        continue  # a conforming signer never emits this pair
                    k_rec, d_rec = recover_from_two_signatures(z1, s1, z2, s2, r)
                    assert (k_rec, d_rec) == (k, d)
                    checked += 1
    assert checked > 500


def test_recovery_uses_neither_the_generator_nor_the_public_key():
    """The chapter says so explicitly; the signatures alone are enough."""
    r, s1, s2 = chapter_signatures()
    assert recover_nonce(CHAPTER_Z1, CHAPTER_Z2, s1, s2, TOY_N) == CHAPTER_K
    assert recover_key(s1, CHAPTER_K, CHAPTER_Z1, r, TOY_N) == CHAPTER_D


def test_equal_hashes_defeat_the_recovery():
    """Exercise 2's second half: z1 == z2 collapses the two equations to one."""
    r = r_from_nonce(CHAPTER_K)
    s1 = sign(CHAPTER_Z1, CHAPTER_D, CHAPTER_K, r)
    s2 = sign(CHAPTER_Z1, CHAPTER_D, CHAPTER_K, r)
    assert s1 == s2
    with pytest.raises(ValueError):
        recover_nonce(CHAPTER_Z1, CHAPTER_Z1, s1, s2)


def test_distinct_hashes_give_distinct_signatures_under_a_shared_nonce():
    """s1 != s2 iff z1 != z2, which is the condition the chapter derives."""
    r = r_from_nonce(CHAPTER_K)
    seen = {}
    for z in range(TOY_N):
        seen[z] = sign(z, CHAPTER_D, CHAPTER_K, r) if z != 8 else None
    signatures = [s for s in seen.values() if s is not None]
    assert len(signatures) == len(set(signatures))


def test_sign_rejects_a_zero_r():
    with pytest.raises(ValueError, match="r is zero"):
        sign(CHAPTER_Z1, CHAPTER_D, CHAPTER_K, 0)


def test_sign_rejects_a_zero_s():
    """z + r d = 0 mod N makes s zero, and FIPS 186-5 rejects that signature."""
    r = r_from_nonce(CHAPTER_K)
    bad_z = (-r * CHAPTER_D) % TOY_N
    with pytest.raises(ValueError, match="s is zero"):
        sign(bad_z, CHAPTER_D, CHAPTER_K, r)


def test_public_key_is_the_toy_stand_in_for_dG():
    assert public_key(CHAPTER_D) == pow(TOY_G, CHAPTER_D, TOY_P)


def test_r_is_the_same_for_both_signatures_under_a_shared_nonce():
    """The repeated r is the observable that tells the attacker to try at all."""
    assert r_from_nonce(CHAPTER_K) == r_from_nonce(CHAPTER_K)
    assert r_from_nonce(CHAPTER_K) != r_from_nonce(CHAPTER_K + 1)


def test_r_from_nonce_is_not_injective_in_the_toy_group():
    """k = 6 and k = 9 collide, and 6 is the chapter's own nonce.

    This is why a shared r is a signal rather than a proof. The toy
    collides because it reduces the group element; real ECDSA collides
    on k and N - k because those points share an x-coordinate.
    """
    assert r_from_nonce(6) == r_from_nonce(9) == 2
    images = [r_from_nonce(k) for k in range(1, TOY_N)]
    assert len(set(images)) < len(images)


def test_secp256k1_has_four_nonces_at_r_equals_two():
    """The chapter's aside claims four candidates at r = 2 on secp256k1.

    r is the curve x-coordinate reduced modulo N, and N < P, so when
    r + N is still below P both x = r and x = r + N can sit on the curve.
    Each valid x carries two points, one per sign of y, so each is one
    nonce. This is also why Bitcoin's public-key recovery id runs 0 to 3
    rather than 0 to 1. Standard library only, per Appendix C.
    """
    P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

    def on_curve(x):  # y^2 = x^3 + 7, tested by Euler's criterion
        return pow((pow(x, 3, P) + 7) % P, (P - 1) // 2, P) == 1

    assert N < P
    assert on_curve(2) and on_curve(2 + N) and 2 + N < P
    assert 2 * sum(on_curve(x) for x in (2, 2 + N)) == 4

    # And it is rare: only r below P - N can have the second coordinate.
    assert (P - N) .bit_length() == 129


def test_a_shared_r_from_two_different_nonces_defeats_the_naive_recovery():
    """Two honest signatures, different nonces, same r: the algebra lies."""
    r = r_from_nonce(6)
    assert r == r_from_nonce(9)
    s1 = sign(CHAPTER_Z1, CHAPTER_D, 6, r)
    s2 = sign(CHAPTER_Z2, CHAPTER_D, 9, r)
    y = public_key(CHAPTER_D)
    assert verify(CHAPTER_Z1, r, s1, y) and verify(CHAPTER_Z2, r, s2, y)
    wrong = recover_from_two_signatures(CHAPTER_Z1, s1, CHAPTER_Z2, s2, r)
    assert wrong != (6, CHAPTER_D)


def test_checking_against_the_public_key_catches_it():
    """recover_and_check returns None where the bare algebra returned a key."""
    r = r_from_nonce(6)
    s1 = sign(CHAPTER_Z1, CHAPTER_D, 6, r)
    s2 = sign(CHAPTER_Z2, CHAPTER_D, 9, r)
    assert recover_and_check(CHAPTER_Z1, s1, CHAPTER_Z2, s2, r, public_key(CHAPTER_D)) is None


def test_recover_and_check_returns_the_key_on_a_genuine_reuse():
    r, s1, s2 = chapter_signatures()
    got = recover_and_check(CHAPTER_Z1, s1, CHAPTER_Z2, s2, r, public_key(CHAPTER_D))
    assert got == (CHAPTER_K, CHAPTER_D)


def test_a_negated_nonce_is_recovered_by_the_same_algebra_with_one_sign_flipped():
    """Real ECDSA sends k and N - k to the same r; that case is still fatal.

    The toy's r comes from reducing the group element, so it does not
    reproduce the k/-k collision on its own. The algebra does not care how
    r arose, so r is passed in directly here, which is exactly the
    situation the chapter's aside describes.
    """
    d, k, r = CHAPTER_D, 4, 5
    z1, z2 = 1, 2
    s1 = sign(z1, d, k, r)
    s2 = sign(z2, d, (TOY_N - k) % TOY_N, r)
    k_rec = ((z1 - z2) * pow(s1 + s2, -1, TOY_N)) % TOY_N
    assert k_rec == k
    assert recover_key(s1, k_rec, z1, r) == d


def test_appendix_d_exercise_2_block_prints_9_6_2_8_4():
    """Appendix D's Exercise 2 block: d = 4, k = 8, in the chapter's group."""
    d, k = 4, 8
    r = r_from_nonce(k)
    z1, z2 = 1, 2
    s1, s2 = sign(z1, d, k, r), sign(z2, d, k, r)
    assert (r, s1, s2) == (9, 6, 2)
    assert recover_from_two_signatures(z1, s1, z2, s2, r) == (8, 4)


def test_appendix_d_exercise_2_changes_what_the_exercise_asks_it_to():
    """Exercise 2 says to pick a different private key and a different nonce."""
    assert (4, 8) != (CHAPTER_D, CHAPTER_K)
    assert 4 != CHAPTER_D and 8 != CHAPTER_K


def test_the_superseded_exercise_2_constants_produced_a_rejected_signature():
    """The block used to read d = 7, k = 3, r = 5, z1 = 4, z2 = 9.

    Its second signature was s2 = 0, which FIPS 186-5 rejects, so the pair
    was not one a conforming signer could have emitted. The arithmetic was
    correct and the recovery worked; the pair was the problem. Pinned so
    the old constants cannot drift back in.
    """
    with pytest.raises(ValueError, match="s is zero"):
        sign(9, 7, 3, 5, 11)
