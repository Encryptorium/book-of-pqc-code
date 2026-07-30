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
    return pow(g, secret, p)


def shared_value(other_public, secret, p):
    """Return this party's view of the shared value.

    Raising the other side's public value to our own secret exponent gives
    ``g^(ab) mod p`` from either side.
    """
    return pow(other_public, secret, p)


def exchange(p, g, a, b):
    """Run both halves of the exchange and return ``(A, B, K_A, K_B)``.

    ``A`` and ``B`` are the published values; ``K_A`` and ``K_B`` are the
    two parties' independently computed shared values, which agree.
    """
    A = public_value(g, a, p)
    B = public_value(g, b, p)
    return A, B, shared_value(B, a, p), shared_value(A, b, p)


def multiplicative_order(g, p):
    """Return the multiplicative order of ``g`` in ``(Z/pZ)^*``.

    The order divides ``p - 1`` by Lagrange's theorem, so only the
    divisors of ``p - 1`` are candidates and the smallest one that sends
    ``g`` to 1 is the order. ``p`` is assumed prime and ``g`` a non-zero
    residue.
    """
    n = p - 1
    divisors = set()
    i = 1
    while i * i <= n:
        if n % i == 0:
            divisors.add(i)
            divisors.add(n // i)
        i += 1
    for candidate in sorted(divisors):
        if pow(g, candidate, p) == 1:
            return candidate
    raise ValueError(f"{g} has no order mod {p}: is {p} prime and g nonzero?")


def is_primitive_root(g, p):
    """Return True when ``g`` generates all of ``(Z/pZ)^*``.

    That is exactly the condition that its order is ``p - 1`` rather than
    a proper divisor, which would confine the exchange to a subgroup.
    """
    return multiplicative_order(g, p) == p - 1
