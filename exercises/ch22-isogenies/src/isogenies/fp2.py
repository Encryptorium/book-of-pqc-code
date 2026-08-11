"""Arithmetic in F_{p^2} = F_p[i] / (i^2 + 1).

Elements are tuples ``(a, b)`` representing ``a + b*i``.  The
irreducible polynomial ``x^2 + 1`` splits only when ``-1`` is a
quadratic residue mod *p*, which fails for any prime ``p = 3 mod 4``.
All primes used in this package satisfy that congruence.
"""

from __future__ import annotations


def fp2_zero() -> tuple[int, int]:
    return (0, 0)


def fp2_one() -> tuple[int, int]:
    return (1, 0)


def fp2_add(x: tuple[int, int], y: tuple[int, int], p: int) -> tuple[int, int]:
    return ((x[0] + y[0]) % p, (x[1] + y[1]) % p)


def fp2_sub(x: tuple[int, int], y: tuple[int, int], p: int) -> tuple[int, int]:
    return ((x[0] - y[0]) % p, (x[1] - y[1]) % p)


def fp2_neg(x: tuple[int, int], p: int) -> tuple[int, int]:
    return ((-x[0]) % p, (-x[1]) % p)


def fp2_mul(x: tuple[int, int], y: tuple[int, int], p: int) -> tuple[int, int]:
    # (a + bi)(c + di) = (ac - bd) + (ad + bc)i
    return (
        (x[0] * y[0] - x[1] * y[1]) % p,
        (x[0] * y[1] + x[1] * y[0]) % p,
    )


def fp2_sqr(x: tuple[int, int], p: int) -> tuple[int, int]:
    # (a + bi)^2 = (a^2 - b^2) + 2ab*i
    return (
        (x[0] * x[0] - x[1] * x[1]) % p,
        (2 * x[0] * x[1]) % p,
    )


def fp2_inv(x: tuple[int, int], p: int) -> tuple[int, int]:
    """Invert a nonzero element: (a + bi)^{-1} = (a - bi) / (a^2 + b^2)."""
    # EXERCISE: implement this function.
    #
    # Multiply numerator and denominator by the conjugate: (a + b*i)^{-1} =
    # (a - b*i) / (a^2 + b^2). The denominator is the field norm and lies in
    # F_p, so invert it once with pow(norm, -1, p) and scale both components
    # by that. Raise ZeroDivisionError when the norm is zero. For p = 3 mod
    # 4 that happens only for the zero element, because a^2 + b^2 = 0 with b
    # nonzero would make -1 a square mod p.
    #
    # Reference: Chapter 22, 'Why F_p^2?'
    #
    # Proved by:
    #   tests/ch22/test_fp2_arithmetic.py
    raise NotImplementedError("exercise: fp2_inv")


def fp2_eq(x: tuple[int, int], y: tuple[int, int], p: int) -> bool:
    return x[0] % p == y[0] % p and x[1] % p == y[1] % p


def fp2_scalar(c: int, p: int) -> tuple[int, int]:
    """Embed a scalar from F_p into F_{p^2}."""
    return (c % p, 0)


def fp2_int_mul(c: int, x: tuple[int, int], p: int) -> tuple[int, int]:
    """Multiply an F_{p^2} element by an integer."""
    return ((c * x[0]) % p, (c * x[1]) % p)


def fp2_pow(x: tuple[int, int], n: int, p: int) -> tuple[int, int]:
    """Compute x^n in F_{p^2} by repeated squaring."""
    if n == 0:
        return fp2_one()
    if n < 0:
        x = fp2_inv(x, p)
        n = -n
    result = fp2_one()
    base = x
    while n:
        if n & 1:
            result = fp2_mul(result, base, p)
        base = fp2_mul(base, base, p)
        n >>= 1
    return result


def fp2_is_square(z: tuple[int, int], p: int) -> bool:
    """Test whether z is a quadratic residue in F_{p^2}*."""
    if z == fp2_zero():
        return True
    exp = (p * p - 1) // 2
    return fp2_eq(fp2_pow(z, exp, p), fp2_one(), p)


def fp2_sqrt(z: tuple[int, int], p: int) -> tuple[int, int] | None:
    """Square root in F_{p^2} via Tonelli-Shanks.

    Returns one square root if *z* is a QR, or None otherwise.
    """
    if z == fp2_zero():
        return fp2_zero()
    if not fp2_is_square(z, p):
        return None

    # Write p^2 - 1 = 2^s * q with q odd.
    n = p * p - 1
    s = 0
    q = n
    while q % 2 == 0:
        q //= 2
        s += 1

    # Find a non-residue in F_{p^2}.
    # (0, 1) = i might work; if not, try (1, 1), (2, 1), ...
    nr = (0, 1)
    for a in range(p):
        nr = (a, 1)
        if not fp2_is_square(nr, p):
            break

    m = s
    c = fp2_pow(nr, q, p)
    t = fp2_pow(z, q, p)
    r = fp2_pow(z, (q + 1) // 2, p)

    while True:
        if fp2_eq(t, fp2_one(), p):
            return r
        # Find the smallest i such that t^{2^i} = 1.
        i = 0
        tmp = t
        while not fp2_eq(tmp, fp2_one(), p):
            tmp = fp2_mul(tmp, tmp, p)
            i += 1
        if i == m:
            return None  # not a square (should not happen)
        b = c
        for _ in range(m - i - 1):
            b = fp2_mul(b, b, p)
        m = i
        c = fp2_mul(b, b, p)
        t = fp2_mul(t, c, p)
        r = fp2_mul(r, b, p)
