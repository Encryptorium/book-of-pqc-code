"""The chapter's toy ElGamal put through the Fujisaki-Okamoto pattern.

Encapsulation draws a random group element ``m``, encrypts it with coins
``G(m)`` derived from the message, and outputs the key ``H(m, c)``.
Decapsulation decrypts, re-encrypts with ``G(m')``, and compares. On a
mismatch it returns ``H(z, c)``, computed from a secret group element ``z``
stored beside the private key, so the caller receives a key-shaped value
either way. That is implicit rejection.

Deriving the coins from the message is what gives the comparison meaning: a
ciphertext is then a fixed function of its plaintext and the public key, so
Bob can recompute it. The check tests consistency, not whether the sender
knew ``m``. Under this ``G`` the ElGamal attack's multiplication by 4 is
rejected for every message in the group, and a mauling whose two coins happen
to agree passes: for ``m = 2`` and the factor 411, ``G(2) = G(822) = 330``.
``tests/ch05/test_fo.py`` pins both, and that two 32-bit fallbacks can
collide.

``H`` truncates its SHA-256 output to 32 bits to keep the chapter's listing
short, and the message set has 1031 elements, so an attacker can guess ``m``
outright. The toy shows the mechanism and proves nothing about security.
"""

import hashlib

from kem_primitives.elgamal import TOY_G, TOY_P, TOY_Q, dec, enc


def hash_to_int(tag, *parts):
    """Hash a domain tag and the decimal forms of ``parts`` to an integer.

    The tag is the first byte hashed, so ``G`` and ``H`` never hash the same
    input, even on the same parts.
    """
    data = tag.encode() + b"|" + b"|".join(str(v).encode() for v in parts)
    return int.from_bytes(hashlib.sha256(data).digest(), "big")


def G(m):
    """Derive encryption coins in ``[0, q)`` from the message ``m``."""
    return hash_to_int("G", m) % TOY_Q


def H(*parts):
    """Derive a 32-bit key: ``H(m, c)`` on success, ``H(z, c)`` on rejection."""
    return hash_to_int("H", *parts) % 2**32


def encap(h, rng):
    """Encapsulate under public key ``h``, returning ``(c, K)``.

    The chapter's listing draws ``m`` from a module-level ``rng``; this
    version takes the generator as an argument, as ``rsa_kem.encap`` does.
    The coins come from ``G(m)``, never from ``rng``.
    """
    m = pow(TOY_G, rng.randrange(TOY_Q), TOY_P)
    c = enc(h, m, G(m))
    return c, H(m, c)


def decap(x, z, h, c):
    """Decapsulate ``c``: re-encrypt and compare, with implicit rejection.

    Returns ``H(m', c)`` when ``c`` is the encryption of its own decryption
    ``m'`` under the coins ``G(m')``, and ``H(z, c)`` otherwise. The fallback
    is the same on every call with the same ``c`` and depends on the secret
    ``z``, so the output alone does not tell a caller which branch ran. No
    input checks: ``c1 = 0`` raises, as in ``elgamal.dec``.
    """
    m_prime = dec(x, c)
    if enc(h, m_prime, G(m_prime)) == c:
        return H(m_prime, c)
    return H(z, c)
