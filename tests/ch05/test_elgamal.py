"""Toy ElGamal, the chapter's first listing in 'Correct is not secure'."""

import random

import pytest

from kem_primitives.elgamal import TOY_G, TOY_P, TOY_Q, dec, enc

SQUARES = sorted({pow(TOY_G, k, TOY_P) for k in range(TOY_Q)})


def is_prime(n):
    return n > 1 and all(n % d for d in range(2, int(n**0.5) + 1))


def chapter_keys():
    """Bob's key pair as the chapter's listing draws it, and the rng after it."""
    rng = random.Random(5)
    x = rng.randrange(1, TOY_Q)
    return rng, x, pow(TOY_G, x, TOY_P)


def test_p_is_a_safe_prime_and_four_has_prime_order_q():
    assert TOY_P == 2 * TOY_Q + 1
    assert is_prime(TOY_P) and is_prime(TOY_Q)
    assert TOY_G != 1 and pow(TOY_G, TOY_Q, TOY_P) == 1


def test_four_generates_exactly_the_squares():
    """The group the chapter calls the subgroup of squares, with 9 in it."""
    squares = {a * a % TOY_P for a in range(1, TOY_P)}
    assert set(SQUARES) == squares
    assert len(SQUARES) == TOY_Q
    assert 9 in squares


def test_chapter_listing_prints_its_two_ciphertexts():
    """The listing's first line: (1664, 1910) (1803, 412) True."""
    rng, x, h = chapter_keys()
    c_first = enc(h, 9, rng.randrange(1, TOY_Q))
    c_second = enc(h, 9, rng.randrange(1, TOY_Q))
    assert (c_first, c_second) == ((1664, 1910), (1803, 412))
    assert dec(x, c_first) == dec(x, c_second) == 9


def test_chapter_listing_mauling_recovers_the_message():
    """The listing's second line: a different ciphertext, and m recovered."""
    rng, x, h = chapter_keys()
    rng.randrange(1, TOY_Q)
    rng.randrange(1, TOY_Q)
    c = enc(h, 9, rng.randrange(1, TOY_Q))
    c_mauled = (c[0], c[1] * 4 % TOY_P)
    assert c_mauled != c
    assert dec(x, c_mauled) * pow(4, -1, TOY_P) % TOY_P == 9


def test_every_message_in_the_group_round_trips():
    rng, x, h = chapter_keys()
    for m in SQUARES:
        assert dec(x, enc(h, m, rng.randrange(1, TOY_Q))) == m


def test_fresh_coins_defeat_encrypt_and_compare():
    """One message has a different ciphertext for every r in [1, q-1]."""
    _, _, h = chapter_keys()
    assert len({enc(h, 9, r) for r in range(1, TOY_Q)}) == TOY_Q - 1


def test_mauling_multiplies_the_plaintext_by_any_factor():
    rng, x, h = chapter_keys()
    for factor in (2, 4, 9, 411, TOY_P - 1):
        for m in SQUARES[:50]:
            c = enc(h, m, rng.randrange(1, TOY_Q))
            assert dec(x, (c[0], c[1] * factor % TOY_P)) == m * factor % TOY_P


def test_a_zero_first_component_raises():
    """The toy checks no inputs: c1 = 0 has no inverse mod p."""
    _, x, _ = chapter_keys()
    with pytest.raises(ValueError):
        dec(x, (0, 9))
