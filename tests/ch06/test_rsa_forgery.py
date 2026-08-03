"""Textbook RSA: the chapter's forgery, and the full-domain-hash repair."""

from math import lcm

import pytest

from signature_attacks.rsa_forgery import (
    TOY_E,
    TOY_P,
    TOY_Q,
    fdh_sign,
    fdh_verify,
    forge,
    full_domain_hash,
    keygen,
    sign,
    verify,
)

CHAPTER_M1 = 0x1111222233334444
CHAPTER_M2 = 0x5555666677778888


def test_chapter_block_prints_true():
    """The chapter's block prints "True": the forged pair verifies."""
    pk, sk = keygen()
    s1, s2 = sign(sk, CHAPTER_M1), sign(sk, CHAPTER_M2)
    m_forged, s_forged = forge(pk, CHAPTER_M1, s1, CHAPTER_M2, s2)
    assert verify(pk, m_forged, s_forged)


def test_chapter_modulus_is_64_bits():
    """The chapter calls it a 64-bit modulus, and Chapter 5 used the same one."""
    assert (TOY_P * TOY_Q).bit_length() == 64
    assert TOY_E == 65537


def test_forged_message_is_one_the_signer_never_signed():
    """The chapter asserts m_forged is fresh, which is the EUF-CMA win condition."""
    pk, sk = keygen()
    s1, s2 = sign(sk, CHAPTER_M1), sign(sk, CHAPTER_M2)
    m_forged, _ = forge(pk, CHAPTER_M1, s1, CHAPTER_M2, s2)
    assert m_forged not in {CHAPTER_M1, CHAPTER_M2}


def test_forgery_needs_neither_the_private_key_nor_the_factorization():
    """forge reads only the public modulus and the two signature pairs."""
    pk, sk = keygen()
    s1, s2 = sign(sk, CHAPTER_M1), sign(sk, CHAPTER_M2)
    n, _ = pk
    m_forged, s_forged = forge((n, TOY_E), CHAPTER_M1, s1, CHAPTER_M2, s2)
    assert verify(pk, m_forged, s_forged)


def test_homomorphism_holds_across_many_pairs():
    """s1 s2 = (m1 m2)^d mod n is an identity, not a property of the chapter's pair."""
    pk, sk = keygen()
    n, _ = pk
    for m1 in (2, 3, 7, 65537, 2**31, TOY_P):
        for m2 in (5, 11, 2**17 + 1, 2**40):
            _, s_forged = forge(pk, m1, sign(sk, m1), m2, sign(sk, m2))
            assert s_forged == sign(sk, (m1 * m2) % n)


def test_honest_signature_verifies_and_a_tampered_one_does_not():
    pk, sk = keygen()
    s = sign(sk, CHAPTER_M1)
    assert verify(pk, CHAPTER_M1, s)
    assert not verify(pk, CHAPTER_M1, s + 1)


def test_keygen_inverts_e_modulo_phi():
    _, sk = keygen()
    _, d = sk
    assert (TOY_E * d) % ((TOY_P - 1) * (TOY_Q - 1)) == 1


def test_fdh_signature_verifies():
    pk, sk = keygen()
    assert fdh_verify(pk, CHAPTER_M1, fdh_sign(sk, CHAPTER_M1))


def test_fdh_kills_the_message_level_forgery():
    """The chapter's central claim: the product no longer verifies on m1 m2."""
    pk, sk = keygen()
    n, _ = pk
    f1, f2 = fdh_sign(sk, CHAPTER_M1), fdh_sign(sk, CHAPTER_M2)
    product = (f1 * f2) % n
    assert not fdh_verify(pk, (CHAPTER_M1 * CHAPTER_M2) % n, product)


def test_fdh_exponentiation_is_still_multiplicative():
    """RSA stays homomorphic; what the product loses is a message it signs.

    The chapter is careful about this: the attacker can still form the
    product, and the product's e-th power is exactly H(m1) H(m2) mod n. It
    is a signature only on an m* with H(m*) = H(m1) H(m2), and finding one
    means inverting the random oracle at a chosen point.
    """
    pk, sk = keygen()
    n, e = pk
    f1, f2 = fdh_sign(sk, CHAPTER_M1), fdh_sign(sk, CHAPTER_M2)
    product = (f1 * f2) % n
    target = (full_domain_hash(CHAPTER_M1, n) * full_domain_hash(CHAPTER_M2, n)) % n
    assert pow(product, e, n) == target


def test_full_domain_hash_lands_inside_the_modulus():
    pk, _ = keygen()
    n, _ = pk
    for m in (0, 1, CHAPTER_M1, CHAPTER_M2, n - 1):
        assert 0 <= full_domain_hash(m, n) < n


def test_full_domain_hash_is_not_multiplicative():
    """H(m1 m2) != H(m1) H(m2) is what the forgery needed and does not get."""
    pk, _ = keygen()
    n, _ = pk
    lhs = full_domain_hash((CHAPTER_M1 * CHAPTER_M2) % n, n)
    rhs = (full_domain_hash(CHAPTER_M1, n) * full_domain_hash(CHAPTER_M2, n)) % n
    assert lhs != rhs


def test_appendix_d_exercise_1_block_prints_true_and_1366():
    """Appendix D's Exercise 1 block on the 12-bit toy modulus n = 53 * 61."""
    pk, sk = (3233, 17), (3233, 413)
    s1, s2 = sign(sk, 100), sign(sk, 200)
    combined = (s1 * s2) % 3233
    expected = pow(100 * 200, 413, 3233)
    assert combined == expected
    assert combined == 1366


def test_appendix_d_exercise_1_uses_the_carmichael_exponent():
    """413 inverts 17 modulo lambda(3233) = 780, not modulo phi(3233) = 3120.

    Both are valid RSA private exponents, so the block is correct; keygen
    returns the phi-based one, which is why the test above passes d in
    explicitly rather than calling keygen(53, 61, 17).
    """
    assert (17 * 413) % lcm(52, 60) == 1
    assert (17 * 413) % (52 * 60) != 1
    _, sk = keygen(53, 61, 17)
    assert sk == (3233, 2753)


def test_appendix_d_exercise_1_forgery_matches_the_package_routine():
    pk, sk = (3233, 17), (3233, 413)
    m_forged, s_forged = forge(pk, 100, sign(sk, 100), 200, sign(sk, 200))
    assert (m_forged, s_forged) == (20000 % 3233, 1366)
    assert verify(pk, m_forged, s_forged)


def test_signing_a_message_at_or_above_the_modulus_wraps():
    """Textbook RSA signs residues; there is no encoding step to reject input."""
    pk, sk = keygen()
    n, _ = pk
    assert sign(sk, n + 5) == sign(sk, 5)
    assert verify(pk, n + 5, sign(sk, 5))


def test_verify_rejects_a_signature_on_a_different_message():
    pk, sk = keygen()
    assert not verify(pk, CHAPTER_M2, sign(sk, CHAPTER_M1))


def test_zero_and_one_are_fixed_points_of_textbook_rsa():
    """Two messages every unpadded RSA signer signs to themselves."""
    pk, sk = keygen()
    for m in (0, 1):
        assert sign(sk, m) == m
        assert verify(pk, m, m)


def test_fdh_verify_rejects_a_textbook_signature():
    """The two schemes are not interchangeable, which the repair depends on."""
    pk, sk = keygen()
    assert not fdh_verify(pk, CHAPTER_M1, sign(sk, CHAPTER_M1))


def test_keygen_rejects_an_e_that_is_not_invertible():
    """No retry loop: a bad exponent raises rather than being silently fixed."""
    with pytest.raises(ValueError):
        keygen(53, 61, 3)
