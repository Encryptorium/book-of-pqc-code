"""Arithmetic in Z/nZ: the first algebraic setting Chapter 2 defines.

Four of these five routines are what the chapter's own code blocks print.
``order`` and ``find_generator`` are the searches exercise 2 asks the reader to
run by hand for p = 17.

None of this is how the later chapters compute. Python's built-in
``pow(base, exponent, modulus)`` does the same job as ``mod_pow`` in C, and
that is what Chapter 4 and Chapter 9 call. ``mod_pow`` exists so the reader can
see what the built-in is doing inside.
"""


def mod_pow(base: int, exponent: int, modulus: int) -> int:
    """Return base ** exponent mod modulus by repeated squaring.

    The loop walks the exponent from low bit to high bit, squaring the running
    base each step and multiplying it into the result whenever the current bit
    is 1. That is O(log exponent) modular multiplications rather than the
    exponent-many an iterated product would take, which is the whole reason
    exponentiation modulo a large n is cheap while its inverse, the discrete
    logarithm, is not.

    ``result`` starts at ``1 % modulus`` rather than ``1`` so that a modulus of
    1 returns 0, which is the only element of the zero ring.
    """
    assert exponent >= 0, "exponent must be non-negative"
    assert modulus >= 1, "modulus must be at least 1"
    result = 1 % modulus
    base = base % modulus
    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent //= 2
    return result


def ext_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (g, x, y) with g == gcd(a, b) and a * x + b * y == g.

    Both arguments must be non-negative. That is a real precondition rather
    than a formality: on a negative argument the recursion can bottom out on a
    negative value and return a negative g, which is a Bezout pair for -gcd
    rather than for gcd. ``mod_inv`` is unaffected, since it reduces its
    argument modulo n before calling.

    The recursion is the Euclidean algorithm carrying its coefficients along.
    When b is 0 the gcd is a and (1, 0) works. Otherwise solve on
    (b, a mod b) and repackage: if b * x1 + (a mod b) * y1 == g, then
    substituting a mod b == a - (a // b) * b gives
    a * y1 + b * (x1 - (a // b) * y1) == g.
    """
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_inv(a: int, modulus: int) -> int:
    """Return the inverse of a modulo modulus.

    An element of Z/nZ is a unit exactly when it is coprime to n, so the assert
    on the gcd is the whole existence condition rather than a defensive check.
    The Bezout coefficient x from a * x + n * y == 1 is the inverse once
    reduced modulo n, because the n * y term vanishes.
    """
    assert modulus > 1, "modulus must be greater than 1"
    g, x, _ = ext_gcd(a % modulus, modulus)
    assert g == 1, "inverse does not exist: a and modulus share a factor"
    return x % modulus


def order(g: int, p: int) -> int:
    """Return the multiplicative order of g modulo p: the least k > 0 with g**k == 1.

    Walks the powers of g one multiplication at a time and stops at the first
    return to 1. That is the definition rather than an algorithm anyone would
    ship, but for the small primes the chapter uses it is instant and it makes
    the group structure visible.

    The order divides p - 1 by Lagrange's theorem, so g is a generator of
    F_p^* exactly when the order equals p - 1. For p = 17, ``order(2, 17)`` is
    8, which is why 2 fails as a generator: its orbit is half the group.
    """
    # EXERCISE: implement this function.
    #
    # Return the least k > 0 with g**k congruent to 1 modulo p. Multiply by
    # g one step at a time and count until the running value is 1. This is
    # the definition rather than an algorithm anyone would ship, and for the
    # chapter's small primes it is instant. The order always divides p - 1
    # by Lagrange's theorem, which is what makes the generator test below a
    # single comparison.
    #
    # Reference: Chapter 2, exercise 2
    #
    # Proved by:
    #   tests/ch02/test_modular.py
    raise NotImplementedError("exercise: order")


def find_generator(p: int) -> int:
    """Return the smallest generator of F_p^*, found by trial.

    Exercise 2's search, written out. Try each candidate upward from 2 and
    keep the first whose order is p - 1. F_p^* is cyclic for every prime p, so
    a generator always exists and the loop always terminates.

    Trial is genuinely the method here, not a shortcut. There is no known way
    to write down a generator of F_p^* for a general prime p without searching,
    and no explicit small base is known unconditionally to be a generator for
    infinitely many primes.
    """
    # EXERCISE: implement this function.
    #
    # Exercise 2's search, written out: try each candidate upward from 2 and
    # return the first whose order is p - 1. F_p^* is cyclic for every prime
    # p, so a generator exists and the loop terminates. Trial really is the
    # method here; no formula gives a generator of F_p^* for a general
    # prime, and no explicit small base is known unconditionally to be a
    # generator for infinitely many primes.
    #
    # Reference: Chapter 2, exercise 2
    #
    # Proved by:
    #   tests/ch02/test_modular.py
    raise NotImplementedError("exercise: find_generator")
