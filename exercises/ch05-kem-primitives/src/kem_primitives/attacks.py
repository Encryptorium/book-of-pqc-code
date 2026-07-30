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
    # EXERCISE: implement this function.
    #
    # Multiply the ciphertext by r^e modulo n. Because textbook RSA is
    # multiplicatively homomorphic, the result encrypts r times the original
    # plaintext. If it differs from the challenge ciphertext the CCA game
    # permits the query; decap itself performs no re-encryption or validity
    # check, so nothing in the toy implementation rejects it.
    #
    # Reference: Chapter 5, 'What breaks without the transforms'
    #
    # Proved by:
    #   tests/ch05/test_attacks.py
    raise NotImplementedError("exercise: maul")


def recover(pk, mauled_output, r):
    """Undo the blinding, returning the original encapsulated key.

    ``mauled_output`` is what the decapsulation oracle returned for the
    mauled ciphertext, namely ``r * K mod n``. Multiplying by ``r^-1``
    recovers ``K``, which is the whole attack.
    """
    # EXERCISE: implement this function.
    #
    # The oracle handed back r * K mod n, so multiply by the inverse of r
    # modulo n to strip the blinding. pow(r, -1, n) raises ValueError when r
    # is not invertible, which is why the attack needs a blinding factor
    # coprime to n.
    #
    # Reference: Chapter 5, 'What breaks without the transforms'
    #
    # Proved by:
    #   tests/ch05/test_attacks.py
    raise NotImplementedError("exercise: recover")


def coprime_failure_bound(p, q):
    """Return the exact fraction of ``K`` in ``[1, n-1]`` not coprime to ``n``.

    ``K`` fails to be coprime to ``n = pq`` exactly when ``p | K`` or
    ``q | K``. There are ``q - 1`` multiples of ``p`` and ``p - 1``
    multiples of ``q`` in the range, and no multiples of ``pq``, so
    inclusion-exclusion gives ``p + q - 2`` bad values out of ``n - 1``.
    """
    # EXERCISE: implement this function.
    #
    # Count the bad K by inclusion-exclusion: there are q - 1 multiples of p
    # in [1, n-1] and p - 1 multiples of q, and no multiples of pq in that
    # range, so the union has p + q - 2 elements. Divide by the n - 1
    # candidates. Return the exact fraction, not the 1/p + 1/q upper bound.
    #
    # Reference: Chapter 5, 'IND-CCA2 and the KEM correctness condition'
    #
    # Proved by:
    #   tests/ch05/test_attacks.py
    raise NotImplementedError("exercise: coprime_failure_bound")
