"""The Fujisaki-Okamoto toy, the chapter's listing in its FO section."""

import random

import pytest

from kem_primitives.elgamal import TOY_G, TOY_P, TOY_Q, dec, enc
from kem_primitives.fo import G, H, decap, encap

SQUARES = sorted({pow(TOY_G, k, TOY_P) for k in range(TOY_Q)})


def chapter_keys(seed=5):
    """Bob's key, public key and rejection seed as the listing draws them."""
    rng = random.Random(seed)
    x = rng.randrange(1, TOY_Q)
    h = pow(TOY_G, x, TOY_P)
    z = pow(TOY_G, rng.randrange(TOY_Q), TOY_P)
    return rng, x, h, z


def passes_the_check(x, h, c):
    m_prime = dec(x, c)
    return enc(h, m_prime, G(m_prime)) == c


def test_chapter_listing_prints_its_three_lines():
    """True, then False, then True True True."""
    rng, x, h, z = chapter_keys()
    c, K = encap(h, rng)
    assert decap(x, z, h, c) == K
    c_mauled = (c[0], c[1] * 4 % TOY_P)
    assert not passes_the_check(x, h, c_mauled)
    k1 = decap(x, z, h, c_mauled)
    k2 = decap(x, z, h, c_mauled)
    k3 = decap(x, z, h, (c[0], c[1] * 9 % TOY_P))
    assert k1 == k2 and k1 != K and k1 != k3


def test_the_rejected_query_gets_the_fallback_of_its_own_ciphertext():
    rng, x, h, z = chapter_keys()
    c, _ = encap(h, rng)
    c_mauled = (c[0], c[1] * 4 % TOY_P)
    assert decap(x, z, h, c_mauled) == H(z, c_mauled)


def test_honest_encapsulations_decapsulate_under_many_keys():
    for seed in range(50):
        rng, x, h, z = chapter_keys(seed)
        for _ in range(5):
            c, K = encap(h, rng)
            assert passes_the_check(x, h, c)
            assert decap(x, z, h, c) == K


def test_multiplying_by_four_is_rejected_for_every_message():
    """It would pass only where G(4m) = G(m), and under this G that never happens."""
    _, x, h, z = chapter_keys()
    for m in SQUARES:
        assert G(4 * m % TOY_P) != G(m)
        c = enc(h, m, G(m))
        c_mauled = (c[0], c[1] * 4 % TOY_P)
        assert decap(x, z, h, c_mauled) == H(z, c_mauled)


def test_a_mauling_whose_coins_agree_passes():
    """The check tests consistency, not knowledge: G(2) = G(822) = 330."""
    assert G(2) == G(822) == 330
    assert 2 in SQUARES and 2 * 411 % TOY_P == 822
    _, x, h, z = chapter_keys()
    c = enc(h, 2, G(2))
    c_mauled = (c[0], c[1] * 411 % TOY_P)
    assert (c, c_mauled) == ((964, 1385), (964, 1910))
    assert passes_the_check(x, h, c_mauled)
    assert decap(x, z, h, c_mauled) == H(822, c_mauled)


def test_two_rejected_ciphertexts_can_share_a_fallback():
    """32-bit fallbacks behave like independent keys, so they can collide."""
    _, x, h, z = chapter_keys()
    a, b = (2, 1006), (6, 473)
    assert not passes_the_check(x, h, a) and not passes_the_check(x, h, b)
    assert decap(x, z, h, a) == decap(x, z, h, b) == 2905309644


def test_a_zero_first_component_raises():
    """No input checks: decap expects two subgroup elements."""
    _, x, h, z = chapter_keys()
    with pytest.raises(ValueError):
        decap(x, z, h, (0, 9))
