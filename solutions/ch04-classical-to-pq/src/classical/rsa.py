"""Textbook RSA over toy moduli.

This module implements keygen, encrypt, decrypt, sign, and verify for
textbook RSA with no padding, no hashing, and no input validation. It
is deliberately insecure. The chapter prose explains why each of these
shortcuts is wrong in production.

A "toy" modulus in this package is the product of two 32-bit primes,
generated with a deterministic Miller-Rabin primality test; the keygen
runs in milliseconds. That product is 63 or 64 bits wide, not always 64:
over 1,000 seeds it comes out 64 bits 598 times and 63 bits 402 times.
The worked example in the chapter, under ``random.Random(42)``, is one of
the 64-bit ones.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


# Public exponent. 65537 is the standard choice and is itself a Fermat
# prime (2^16 + 1), so it has Hamming weight 2 and fast exponentiation
# is particularly cheap. See FIPS 186-5.
PUBLIC_EXPONENT = 65537


@dataclass(frozen=True)
class PublicKey:
    n: int
    e: int


@dataclass(frozen=True)
class PrivateKey:
    n: int
    d: int
    p: int
    q: int


def _miller_rabin(n: int, witnesses: tuple[int, ...]) -> bool:
    """Deterministic Miller-Rabin for small n. The witness set
    [2, 3, 5, 7, 11, 13] is deterministic for every n < 3,474,749,660,383,
    which easily covers every 32-bit integer. The bound is Jaeschke's
    (Mathematics of Computation 61, 1993); OEIS A014233 tabulates the
    series.
    """
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13):
        if n == p:
            return True
        if n % p == 0:
            return False
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in witnesses:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def _random_prime(bits: int, rng: random.Random) -> int:
    """Sample a random odd integer with exactly ``bits`` bits and retry
    until it is prime. For the 32-bit toy primes used here this finishes
    in a handful of tries.
    """
    while True:
        candidate = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if _miller_rabin(candidate, (2, 3, 5, 7, 11, 13)):
            return candidate


def keygen(bits: int = 64, rng: random.Random | None = None) -> tuple[PublicKey, PrivateKey]:
    """Generate a toy RSA keypair with a modulus of roughly ``bits`` bits.

    ``bits`` should be even and at least 32, so that ``phi(n)``
    comfortably exceeds the public exponent 65537. That does not by
    itself make the two coprime, which is why the loop below retries
    whenever 65537 divides ``phi(n)``. Neither condition is enforced.
    The default ``bits=64`` keygens in milliseconds and yields a modulus
    of 63 or 64 bits, since two exactly-32-bit primes multiply to either.

    The caller supplies ``rng``; passing ``random.Random(42)`` is what
    reproduces the primes the chapter prints. With ``rng=None`` this
    seeds from the system entropy source and the primes differ per call.
    """
    if rng is None:
        rng = random.Random()
    half = bits // 2
    while True:
        p = _random_prime(half, rng)
        q = _random_prime(half, rng)
        if p == q:
            continue
        n = p * q
        phi = (p - 1) * (q - 1)
        if phi % PUBLIC_EXPONENT == 0:
            # 65537 must be coprime to phi(n). Retry on the rare collision.
            continue
        d = pow(PUBLIC_EXPONENT, -1, phi)
        return PublicKey(n=n, e=PUBLIC_EXPONENT), PrivateKey(n=n, d=d, p=p, q=q)


def encrypt(pk: PublicKey, m: int) -> int:
    """Textbook RSA encryption: ``c = m^e mod n``. No padding."""
    return pow(m, pk.e, pk.n)


def decrypt(sk: PrivateKey, c: int) -> int:
    """Textbook RSA decryption: ``m = c^d mod n``."""
    return pow(c, sk.d, sk.n)


def sign(sk: PrivateKey, m: int) -> int:
    """Textbook RSA signing: ``s = m^d mod n``. No hashing. Do not use."""
    return pow(m, sk.d, sk.n)


def verify(pk: PublicKey, m: int, s: int) -> bool:
    """Textbook RSA verification: check ``s^e mod n == m``."""
    return pow(s, pk.e, pk.n) == m
