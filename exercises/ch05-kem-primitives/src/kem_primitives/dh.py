"""Toy Diffie-Hellman key agreement in the multiplicative group mod p.

The chapter's exchange runs on ``p = 23`` and ``g = 5``. Both parties
publish ``g`` raised to a secret exponent and then raise the other side's
public value to their own secret; the two results agree because
``(g^b)^a`` and ``(g^a)^b`` are both ``g^(ab)``.

The shared value is a group element, not a symmetric key. A real
deployment feeds it through a key-derivation function; this module stops
at the group element, which is where the chapter stops.
"""

# The chapter's toy parameters. 5 is a primitive root mod 23.
TOY_P = 23
TOY_G = 5


def public_value(g, secret, p):
    """Return the public value ``g^secret mod p`` that this party publishes."""
    # EXERCISE: implement this function.
    #
    # One three-argument pow: raise the base g to this party's secret
    # exponent modulo p. This is the value Alice publishes as A, and Bob as
    # B.
    #
    # Reference: Chapter 5, 'A shared key without a pre-shared secret'
    #
    # Proved by:
    #   tests/ch05/test_dh.py
    raise NotImplementedError("exercise: public_value")


def shared_value(other_public, secret, p):
    """Return this party's view of the shared value.

    Raising the other side's public value to our own secret exponent gives
    ``g^(ab) mod p`` from either side.
    """
    # EXERCISE: implement this function.
    #
    # Raise the OTHER party's public value to our own secret exponent modulo
    # p. Substituting the other side's value shows both parties land on
    # g^(ab), which is why the two results agree without either side sending
    # a secret.
    #
    # Reference: Chapter 5, 'A shared key without a pre-shared secret'
    #
    # Proved by:
    #   tests/ch05/test_dh.py
    raise NotImplementedError("exercise: shared_value")


def exchange(p, g, a, b):
    """Run both halves of the exchange and return ``(A, B, K_A, K_B)``.

    ``A`` and ``B`` are the published values; ``K_A`` and ``K_B`` are the
    two parties' independently computed shared values, which agree.
    """
    # EXERCISE: implement this function.
    #
    # Compose the two routines above into the full exchange. Publish A from
    # a and B from b, then compute each party's view of the shared value
    # from the other's public value, and return the four in the order (A, B,
    # K_A, K_B).
    #
    # Reference: Chapter 5, 'A shared key without a pre-shared secret'
    #
    # Proved by:
    #   tests/ch05/test_dh.py
    raise NotImplementedError("exercise: exchange")


def multiplicative_order(g, p):
    """Return the multiplicative order of ``g`` in ``(Z/pZ)^*``.

    The order divides ``p - 1`` by Lagrange's theorem, so only the
    divisors of ``p - 1`` are candidates and the smallest one that sends
    ``g`` to 1 is the order. ``p`` is assumed prime and ``g`` a non-zero
    residue.
    """
    # EXERCISE: implement this function.
    #
    # The order divides p - 1 by Lagrange's theorem, so collect the divisors
    # of p - 1 by trial division up to the square root (adding both i and n
    # // i), then walk them in increasing order and return the first one
    # that sends g to 1. Raise ValueError if none does, which means p was
    # not prime or g was zero.
    #
    # Reference: Chapter 5, 'A shared key without a pre-shared secret'
    #
    # Proved by:
    #   tests/ch05/test_dh.py
    raise NotImplementedError("exercise: multiplicative_order")


def is_primitive_root(g, p):
    """Return True when ``g`` generates all of ``(Z/pZ)^*``.

    That is exactly the condition that its order is ``p - 1`` rather than
    a proper divisor, which would confine the exchange to a subgroup.
    """
    # EXERCISE: implement this function.
    #
    # g generates the whole group exactly when its order is p - 1 rather
    # than a proper divisor of it. One comparison against the order.
    #
    # Reference: Chapter 5, 'A shared key without a pre-shared secret'
    #
    # Proved by:
    #   tests/ch05/test_dh.py
    raise NotImplementedError("exercise: is_primitive_root")
