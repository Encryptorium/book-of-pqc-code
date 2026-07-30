"""The attack side of Chapter 5: mauling the toy RSA-KEM, and one bound.

``maul`` and ``recover`` together are the chosen-ciphertext attack the
chapter walks: blind the challenge ciphertext by ``r^e``, send the result
to the decapsulation oracle, and divide the oracle's answer by ``r``. The
toy KEM has no re-encryption check, so nothing in ``decap`` rejects a
mauled ciphertext.

The *game* still rejects one thing, and the chapter's choice of ``r = 2``
is what avoids it. A CCA adversary may not query the challenge ciphertext
itself, so the attack needs ``c' != c``, and an invertible ``r != 1`` does
not guarantee that. With ``K = p`` and ``r`` chosen by CRT as ``2 mod p``
and ``1 mod q``, that ``r`` is coprime to ``n`` and is not ``1 mod n``, yet
``maul`` returns ``c`` unchanged: modulo ``p`` both are zero, and modulo
``q`` the factor ``r^e`` is one. ``r = 2`` is collision-free for every ``K`` in
``[1, n-1]`` under any valid two-prime RSA key, not just this one. Since ``d`` exists,
``e`` is invertible mod ``(p-1)(q-1)``, so ``gcd(e, p-1) = gcd(e, q-1) = 1``;
if ``2^e = 1 mod p`` then ``ord_p(2)`` divides both ``e`` and ``p-1``, hence
divides 1, forcing ``2 = 1 mod p``, which no prime allows. See
``tests/ch05/test_attacks.py``, which pins both directions.

``coprime_failure_bound`` is the second half of the chapter's Exercise 3:
how often a uniform ``K`` in ``[1, n-1]`` shares a factor with ``n``.

That fraction governs neither of the two things it looks like it should.
Decapsulation correctness is exact on the whole range, by Fermat plus CRT,
so it is not a correctness bound. And it is not the mauling attack's
failure rate: ``recover`` needs the blinding factor ``r`` to be
invertible, not ``K``, and ``r`` is chosen rather than sampled. For an
odd RSA modulus ``r = 2`` is invertible with no test at all. The count is
here because Exercise 3 asks for it and because knowing which quantity a
bound applies to is part of reading one.
"""


def maul(pk, c, r):
    """Blind a ciphertext by ``r``, returning ``c * r^e mod n``.

    Textbook RSA is multiplicatively homomorphic, so this is a valid
    encryption of ``r`` times the original plaintext. ``r`` must be
    invertible mod ``n`` for ``recover`` to undo the blinding.
    """
    n, e = pk
    return (c * pow(r, e, n)) % n


def recover(pk, mauled_output, r):
    """Undo the blinding, returning the original encapsulated key.

    ``mauled_output`` is what the decapsulation oracle returned for the
    mauled ciphertext, namely ``r * K mod n``. Multiplying by ``r^-1``
    recovers ``K``, which is the whole attack.
    """
    n, _ = pk
    return (mauled_output * pow(r, -1, n)) % n


def coprime_failure_bound(p, q):
    """Return the exact fraction of ``K`` in ``[1, n-1]`` not coprime to ``n``.

    ``K`` fails to be coprime to ``n = pq`` exactly when ``p | K`` or
    ``q | K``. There are ``q - 1`` multiples of ``p`` and ``p - 1``
    multiples of ``q`` in the range, and no multiples of ``pq``, so
    inclusion-exclusion gives ``p + q - 2`` bad values out of ``n - 1``.
    """
    n = p * q
    return (p + q - 2) / (n - 1)
