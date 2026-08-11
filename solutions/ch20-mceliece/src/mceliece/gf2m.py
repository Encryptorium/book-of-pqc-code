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
    n = len(f) + len(g) - 1
    result = [0] * n
    for i, fi in enumerate(f):
        for j, gj in enumerate(g):
            result[i + j] ^= gf2m_mul(fi, gj, m, irred)
    return _strip(result)


def poly_mod(f: list[int], g: list[int], m: int, irred: int) -> list[int]:
    """Compute f mod g over GF(2^m).  Returns remainder."""
    f = list(f)
    dg = len(g) - 1
    lg = g[-1]
    lg_inv = gf2m_inv(lg, m, irred)
    while len(f) - 1 >= dg and not (len(f) == 1 and f[0] == 0):
        coeff = gf2m_mul(f[-1], lg_inv, m, irred)
        shift = len(f) - 1 - dg
        for i in range(len(g)):
            f[shift + i] ^= gf2m_mul(coeff, g[i], m, irred)
        f = _strip(f)
    return f


def poly_gcd(f: list[int], g: list[int], m: int, irred: int
             ) -> tuple[list[int], list[int], list[int]]:
    """Extended GCD for polynomials over GF(2^m).

    Returns (gcd, s, t) such that gcd = s*f + t*g.
    """
    old_r, r = list(f), list(g)
    old_s, s = [1], [0]
    old_t, t = [0], [1]
    while not (len(r) == 1 and r[0] == 0):
        # quotient = old_r // r
        q = _poly_divmod(old_r, r, m, irred)[0]
        old_r, r = r, poly_mod(old_r, r, m, irred)
        old_s, s = s, _poly_sub(old_s, poly_mul(q, s, m, irred))
        old_t, t = t, _poly_sub(old_t, poly_mul(q, t, m, irred))
    return _strip(old_r), _strip(old_s), _strip(old_t)


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
    gcd, s, _ = poly_gcd(f, g, m, irred)
    if len(gcd) != 1 or gcd[0] == 0:
        raise ValueError("polynomial is not invertible modulo g")
    # normalize: gcd should be 1
    c_inv = gf2m_inv(gcd[0], m, irred)
    return _strip([gf2m_mul(c_inv, si, m, irred) for si in s])


def poly_sqrtmod(f: list[int], g: list[int], m: int, irred: int) -> list[int]:
    """Compute sqrt(f) mod g over GF(2^m).

    In GF(2^m), squaring is the Frobenius endomorphism.  The square root
    of an element a is a^{2^{m-1}}.  For a polynomial f mod g of degree t,
    we compute f^{2^{m*t - 1}} mod g, which is the unique square root in
    the quotient ring GF(2^m)[x] / g(x).

    For our toy sizes this is done by repeated squaring (compose-and-reduce).
    """
    # sqrt(f) = f^{2^{m*t - 1}} mod g, where t = deg(g)
    t = len(g) - 1
    result = list(f)
    for _ in range(m * t - 1):
        result = poly_mul(result, result, m, irred)
        result = poly_mod(result, g, m, irred)
    return _strip(result)


def poly_is_irreducible(coeffs: list[int], m: int, irred: int) -> bool:
    """Test if a polynomial over GF(2^m) is irreducible.

    For degree-2 polynomials: irreducible iff it has no roots in GF(2^m).
    For higher degrees: use the standard x^{q^i} mod f test.
    """
    deg = len(coeffs) - 1
    if deg <= 0:
        return False
    if deg == 1:
        return True
    q = 1 << m
    if deg == 2:
        return all(poly_eval(coeffs, a, m, irred) != 0 for a in range(q))
    # General test: gcd(x^{q^i} - x, f) == 1 for i = 1..deg//2
    # then gcd(x^{q^deg} - x, f) == f
    xpoly = [0, 1]  # x
    h = list(xpoly)
    for i in range(1, deg):
        # h = h^q mod f
        for _ in range(m):
            h = poly_mul(h, h, m, irred)
            h = poly_mod(h, coeffs, m, irred)
        # gcd(h - x, f)
        diff = _poly_sub(h, xpoly)
        g, _, _ = poly_gcd(diff, coeffs, m, irred)
        if i < deg:
            if len(g) != 1:
                return False
        else:
            if len(g) != len(coeffs):
                return False
    return True
