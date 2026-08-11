"""GF(2^m) element and polynomial arithmetic.

Elements of GF(2^m) are integers in 0..2^m-1, representing polynomials
over GF(2) via their bit pattern.  The irreducible polynomial *irred*
is also an integer (degree-m polynomial, so bit m is set).

Polynomials over GF(2^m) are lists of coefficients, index = degree:
    [c0, c1, c2] represents c0 + c1*x + c2*x^2
"""


# ── element arithmetic ───────────────────────────────────────────────

def gf2m_add(a: int, b: int) -> int:
    """Add two GF(2^m) elements (XOR)."""
    return a ^ b


def gf2m_mul(a: int, b: int, m: int, irred: int) -> int:
    """Multiply two GF(2^m) elements modulo *irred*."""
    result = 0
    for _ in range(m):
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & (1 << m):
            a ^= irred
    return result


def gf2m_inv(a: int, m: int, irred: int) -> int:
    """Multiplicative inverse in GF(2^m) by brute force.

    Raises ValueError for a == 0.
    """
    if a == 0:
        raise ValueError("zero has no inverse")
    for x in range(1, 1 << m):
        if gf2m_mul(a, x, m, irred) == 1:
            return x
    raise AssertionError("unreachable for valid field")


# ── polynomial arithmetic over GF(2^m) ──────────────────────────────

def _strip(p: list[int]) -> list[int]:
    """Remove trailing zero coefficients."""
    while len(p) > 1 and p[-1] == 0:
        p = p[:-1]
    return p


def poly_eval(coeffs: list[int], x: int, m: int, irred: int) -> int:
    """Evaluate a polynomial at *x* in GF(2^m) via Horner's method."""
    result = 0
    for c in reversed(coeffs):
        result = gf2m_add(gf2m_mul(result, x, m, irred), c)
    return result


def poly_mul(f: list[int], g: list[int], m: int, irred: int) -> list[int]:
    """Multiply two polynomials over GF(2^m)."""
    # EXERCISE: implement this function.
    #
    # Schoolbook convolution. The product has degree deg(f) + deg(g), so
    # allocate len(f) + len(g) - 1 slots and XOR gf2m_mul(f_i, g_j) into
    # slot i + j. Accumulate with XOR rather than assignment, because
    # several term pairs land in the same slot. Strip trailing zeros before
    # returning, so that the degree comparisons the Euclidean routines make
    # stay honest.
    #
    # Reference: Chapter 20, 'Patterson decoding'
    #
    # Proved by:
    #   tests/ch20/test_gf2m.py
    raise NotImplementedError("exercise: poly_mul")


def poly_mod(f: list[int], g: list[int], m: int, irred: int) -> list[int]:
    """Compute f mod g over GF(2^m).  Returns remainder."""
    # EXERCISE: implement this function.
    #
    # Repeated leading-term cancellation. Invert g's leading coefficient
    # once up front, then while the working polynomial's degree is at least
    # deg(g), scale g by f's leading coefficient times that inverse, shift
    # it up by the degree difference, and XOR it in. Strip trailing zeros
    # each pass, which is what actually makes the degree fall. Work on a
    # copy so the caller's list is not mutated, and let the loop guard also
    # stop on the zero polynomial, which _strip leaves as [0] with nominal
    # degree 0.
    #
    # Reference: Chapter 20, 'Patterson decoding'
    #
    # Proved by:
    #   tests/ch20/test_gf2m.py
    raise NotImplementedError("exercise: poly_mod")


def poly_gcd(f: list[int], g: list[int], m: int, irred: int
             ) -> tuple[list[int], list[int], list[int]]:
    """Extended GCD for polynomials over GF(2^m).

    Returns (gcd, s, t) such that gcd = s*f + t*g.
    """
    # EXERCISE: implement this function.
    #
    # Extended Euclid over GF(2^m)[x], carrying three pairs: remainders
    # starting at (f, g), and Bezout coefficients starting at ([1], [0]) and
    # ([0], [1]). Each round takes the quotient from _poly_divmod, advances
    # the remainder pair to (r, old_r mod r), and advances each coefficient
    # pair by subtracting quotient times the current value. Stop when the
    # remainder is the zero polynomial and return the previous remainder
    # with its two coefficients, so that gcd = s*f + t*g. Subtraction and
    # addition are the same XOR in characteristic 2, which is why _poly_sub
    # serves for both.
    #
    # Reference: Chapter 20, 'Patterson decoding'
    #
    # Proved by:
    #   tests/ch20/test_gf2m.py
    raise NotImplementedError("exercise: poly_gcd")


def _poly_sub(f: list[int], g: list[int]) -> list[int]:
    """Subtract (XOR) two polynomials over GF(2^m)."""
    n = max(len(f), len(g))
    result = [0] * n
    for i in range(len(f)):
        result[i] ^= f[i]
    for i in range(len(g)):
        result[i] ^= g[i]
    return _strip(result)


def _poly_divmod(f: list[int], g: list[int], m: int, irred: int
                 ) -> tuple[list[int], list[int]]:
    """Polynomial division: returns (quotient, remainder)."""
    f = list(f)
    dg = len(g) - 1
    lg_inv = gf2m_inv(g[-1], m, irred)
    q = [0] * max(len(f) - dg, 1)
    while len(f) - 1 >= dg and not (len(f) == 1 and f[0] == 0):
        coeff = gf2m_mul(f[-1], lg_inv, m, irred)
        shift = len(f) - 1 - dg
        q[shift] = coeff
        for i in range(len(g)):
            f[shift + i] ^= gf2m_mul(coeff, g[i], m, irred)
        f = _strip(f)
    return _strip(q), _strip(f)


def poly_inv_mod(f: list[int], g: list[int], m: int, irred: int) -> list[int]:
    """Compute f^{-1} mod g over GF(2^m).

    Raises ValueError if f is not invertible modulo g.
    """
    # EXERCISE: implement this function.
    #
    # Run the extended GCD of f and g. If the gcd is not a nonzero constant
    # then f shares a factor with g and has no inverse, so raise ValueError.
    # Otherwise the Bezout coefficient s satisfies s*f = gcd mod g, so scale
    # every coefficient of s by the field inverse of that constant to
    # normalize the gcd to 1. Patterson's step 2 rests on this: modulo an
    # irreducible g every nonzero polynomial is invertible, which is one of
    # the two reasons the Goppa polynomial has to be irreducible.
    #
    # Reference: Chapter 20, 'Patterson decoding'
    #
    # Proved by:
    #   tests/ch20/test_gf2m.py
    raise NotImplementedError("exercise: poly_inv_mod")


def poly_sqrtmod(f: list[int], g: list[int], m: int, irred: int) -> list[int]:
    """Compute sqrt(f) mod g over GF(2^m).

    In GF(2^m), squaring is the Frobenius endomorphism.  The square root
    of an element a is a^{2^{m-1}}.  For a polynomial f mod g of degree t,
    we compute f^{2^{m*t - 1}} mod g, which is the unique square root in
    the quotient ring GF(2^m)[x] / g(x).

    For our toy sizes this is done by repeated squaring (compose-and-reduce).
    """
    # EXERCISE: implement this function.
    #
    # Squaring is the Frobenius map, a bijection, so every element has
    # exactly one square root and there is no sign ambiguity to resolve.
    # When g is irreducible of degree t the quotient ring GF(2^m)[x]/g(x) is
    # isomorphic to GF(2^(m*t)), whose multiplicative order makes the square
    # root of f equal to f^(2^(m*t - 1)). Compute that by squaring with
    # poly_mul and reducing with poly_mod exactly m*t - 1 times rather than
    # by materializing the exponent, and strip the result.
    #
    # Reference: Chapter 20, 'Patterson's decoding algorithm'
    #
    # Proved by:
    #   tests/ch20/test_patterson.py
    raise NotImplementedError("exercise: poly_sqrtmod")


def poly_is_irreducible(coeffs: list[int], m: int, irred: int) -> bool:
    """Test if a polynomial over GF(2^m) is irreducible.

    For degree-2 polynomials: irreducible iff it has no roots in GF(2^m).
    For higher degrees: use the standard x^{q^i} mod f test.
    """
    # EXERCISE: implement this function.
    #
    # Degree 0 or below is not irreducible; degree 1 always is. At degree 2
    # a polynomial is irreducible exactly when it has no root in GF(2^m),
    # because the only possible factorization is into two linear factors, so
    # evaluate at all 2^m elements and require every value nonzero. Above
    # degree 2 that shortcut fails, since a quartic can split into two
    # irreducible quadratics with no roots at all, so the general branch
    # runs the distinct-degree test instead: raise h from x to h^q mod f by
    # m successive squarings per step, and check gcd(h - x, f) at each
    # degree.
    #
    # Reference: Chapter 20, 'Goppa code construction'
    #
    # Proved by:
    #   tests/ch20/test_gf2m.py
    #   tests/ch20/test_goppa_construction.py
    raise NotImplementedError("exercise: poly_is_irreducible")
