"""Textbook RSA signatures, the multiplicative forgery, and the FDH repair.

Textbook RSA signing raises the message to the private exponent modulo the
public modulus. Raw modular exponentiation is a group homomorphism on
``(Z/nZ)^*``, so the product of two signatures is a valid signature on the
product of the two messages, and the attacker needs neither ``d`` nor the
factorization of ``n``. ``forge`` is that one line.

``fdh_sign`` and ``fdh_verify`` are the pedagogical repair: sign ``H(m)``
rather than ``m``. Exponentiation is still multiplicative, so the attacker
can still form the product; what the product no longer is, is a signature
on any message the attacker can name. See the package README.
"""

from __future__ import annotations

import hashlib

# The chapter's 64-bit modulus, which is the one Chapter 5 used for its toy
# RSA-KEM. Two 32-bit primes, so n is 64 bits wide.
TOY_P = 3184935163
TOY_Q = 3199286161
TOY_E = 65537


def keygen(
    p: int = TOY_P, q: int = TOY_Q, e: int = TOY_E
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Return the public key ``(n, e)`` and the private key ``(n, d)``.

    No primality test and no retry loop: the toy primes are fixed and known
    good. ``d`` inverts ``e`` modulo ``(p-1)(q-1)``. Any ``d`` inverting ``e``
    modulo the Carmichael function ``lcm(p-1, q-1)`` is an equally valid
    private exponent, and Appendix D's Exercise 1 uses one.
    """
    n = p * q
    d = pow(e, -1, (p - 1) * (q - 1))
    return (n, e), (n, d)


def sign(sk: tuple[int, int], m: int) -> int:
    """Textbook RSA signing: ``s = m^d mod n``.

    The message itself is the algebraic object being signed, with no hash
    and no encoding in front of it. That is the whole defect.
    """
    n, d = sk
    return pow(m, d, n)


def verify(pk: tuple[int, int], m: int, s: int) -> bool:
    """Textbook RSA verification: accept iff ``s^e == m mod n``."""
    n, e = pk
    return pow(s, e, n) == m % n


def forge(pk: tuple[int, int], m1: int, s1: int, m2: int, s2: int) -> tuple[int, int]:
    """Multiply two signatures into a third, and return ``(m, s)``.

    ``s1 s2 = (m1 m2)^d mod n`` by exponent arithmetic in the group, so the
    product verifies as a signature on ``m1 m2 mod n``. The signer was never
    asked for that message.
    """
    n, _ = pk
    return (m1 * m2) % n, (s1 * s2) % n


def full_domain_hash(m: int, n: int) -> int:
    """Hash an integer message into ``Z/nZ``.

    SHA-256 of the message's big-endian byte encoding, reduced modulo ``n``.
    For a 64-bit ``n`` the reduction of a 256-bit digest is uniform enough on
    ``Z/nZ`` to stand in for a full-domain hash; a real FDH-RSA at a real
    modulus size needs a construction that fills the domain rather than a
    single fixed-width digest.
    """
    width = (max(m.bit_length(), 1) + 7) // 8
    digest = hashlib.sha256(m.to_bytes(width, "big")).digest()
    return int.from_bytes(digest, "big") % n


def fdh_sign(sk: tuple[int, int], m: int) -> int:
    """FDH-RSA signing: ``sigma = H(m)^d mod n``."""
    n, d = sk
    return pow(full_domain_hash(m, n), d, n)


def fdh_verify(pk: tuple[int, int], m: int, s: int) -> bool:
    """FDH-RSA verification: accept iff ``sigma^e == H(m) mod n``."""
    n, e = pk
    return pow(s, e, n) == full_domain_hash(m, n)
