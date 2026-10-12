"""Toy ElGamal: the chapter's Diffie-Hellman used to encrypt.

Bob's public key is a Diffie-Hellman share ``h = g^x``. To encrypt a group
element ``m``, Alice makes a fresh share ``g^r`` and multiplies ``m`` by the
shared value ``h^r``, which Bob recomputes as ``(g^r)^x`` and divides out.

The group is the subgroup of squares modulo the safe prime
``p = 2063 = 2 * 1031 + 1``. It has prime order ``q = 1031`` and ``g = 4``
generates it, so a message must be a square mod ``p``: the chapter's is
``9 = 3^2``.

The scheme resists the test that breaks textbook RSA, encrypting a guess and
comparing, because each encryption draws a fresh ``r``. It does not resist a
decryption oracle: ``(c1, 4 * c2)`` is a different ciphertext whose
decryption is ``4m``, so one query on it, divided by 4, recovers ``m``.
``tests/ch05/test_elgamal.py`` pins both, and ``kem_primitives.fo`` puts the
same scheme through the Fujisaki-Okamoto pattern that stops the second.

A group this small has no security, since a laptop takes discrete logarithms
in it instantly. These functions show the mechanism only.
"""

# The chapter's toy group. 4 = 2^2 is a square other than 1, so in the
# subgroup of squares, whose order 1031 is prime, it generates everything.
TOY_P = 2063
TOY_Q = 1031
TOY_G = 4


def enc(h, m, r):
    """Encrypt the group element ``m`` under public key ``h`` with coins ``r``.

    Returns ``(g^r, m * h^r)`` mod ``p``: Alice's fresh share, and ``m``
    masked by the shared value.
    """
    return (pow(TOY_G, r, TOY_P), m * pow(h, r, TOY_P) % TOY_P)


def dec(x, c):
    """Decrypt ``c = (c1, c2)`` with private key ``x``.

    Bob recomputes the shared value ``h^r`` as ``c1^x`` and divides it out.
    The toy checks no inputs and expects two subgroup elements: ``c1 = 0``
    has no inverse, and ``pow`` raises ``ValueError``.
    """
    c1, c2 = c
    shared = pow(c1, x, TOY_P)
    return c2 * pow(shared, -1, TOY_P) % TOY_P
