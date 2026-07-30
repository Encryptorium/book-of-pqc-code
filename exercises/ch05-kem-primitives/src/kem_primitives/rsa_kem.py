"""The toy RSA-KEM the chapter builds on textbook RSA.

``encap`` samples a random ``K`` in ``[1, n-1]`` and sets the ciphertext
to ``K^e mod n``. ``decap`` raises the ciphertext to the private exponent,
which is textbook RSA decryption.

Correctness is exact for every ``K`` in ``[1, n-1]``, including the ``K``
that share a factor with ``n``: textbook RSA recovers the original residue
mod ``pq`` for all inputs, by Fermat's little theorem mod ``p`` and mod
``q`` separately (trivially when ``p | K`` or ``q | K``) and then the
Chinese remainder theorem. Coprimality of ``K`` is not needed anywhere in
this package. The mauling attack in ``kem_primitives.attacks`` needs its
own blinding factor to be invertible, which is a different quantity and
one the attacker picks.

This KEM is correct and is *not* IND-CCA2-secure. Textbook RSA is
multiplicatively malleable, and it is not even IND-CPA-secure, which is
why the chapter uses it as a deliberately weak starting point rather than
as a scheme the Fujisaki-Okamoto transform could be applied to as-is.
"""

# The chapter's toy modulus: two 32-bit primes, so n is 64 bits wide.
TOY_P = 3184935163
TOY_Q = 3199286161
TOY_E = 65537


def keygen(p=TOY_P, q=TOY_Q, e=TOY_E):
    """Return ``(public_key, private_key)`` for the toy modulus ``p * q``.

    Each key is the pair ``(n, exponent)``. The private exponent is the
    inverse of ``e`` modulo ``(p-1)(q-1)``.
    """
    # EXERCISE: implement this function.
    #
    # Set n = p q, invert e modulo (p-1)(q-1) with pow(e, -1, phi), and
    # return the public key (n, e) and the private key (n, d). No primality
    # testing and no retry loop: the toy primes are fixed and known good.
    #
    # Reference: Chapter 5, 'The KEM API and a toy RSA-KEM'
    #
    # Proved by:
    #   tests/ch05/test_rsa_kem.py
    raise NotImplementedError("exercise: keygen")


def encap(pk, rng):
    """Sample a fresh ``K`` and encapsulate it, returning ``(c, K)``.

    ``rng`` supplies the randomness. The chapter's snippet passes a seeded
    ``random.Random`` for reproducibility, which is deterministic and not
    cryptographically secure; real encapsulation uses
    ``secrets.SystemRandom`` and feeds the output through a KDF.
    """
    # EXERCISE: implement this function.
    #
    # Unpack the public key, draw K uniformly from [1, n-1] with
    # rng.randint, encrypt it as pow(K, e, n), and return the pair (c, K) in
    # that order. Note that encapsulation returns the key as well as the
    # ciphertext: neither party chose K, which is the whole distinction from
    # public-key encryption.
    #
    # Reference: Chapter 5, 'The KEM API and a toy RSA-KEM'
    #
    # Proved by:
    #   tests/ch05/test_rsa_kem.py
    raise NotImplementedError("exercise: encap")


def decap(sk, c):
    """Recover the encapsulated key from the ciphertext.

    This is raw RSA decryption. There is no re-encryption check and no
    rejection branch, which is precisely what the mauling attack exploits.
    """
    # EXERCISE: implement this function.
    #
    # Raise the ciphertext to the private exponent modulo n. That is raw RSA
    # decryption, with no re-encryption check and no rejection branch, which
    # is exactly what the mauling attack exploits.
    #
    # Reference: Chapter 5, 'The KEM API and a toy RSA-KEM'
    #
    # Proved by:
    #   tests/ch05/test_rsa_kem.py
    raise NotImplementedError("exercise: decap")
