"""Tests for GF(2^m) element and polynomial arithmetic."""

from mceliece.gf2m import (
    gf2m_add, gf2m_mul, gf2m_inv,
    poly_eval, poly_mul, poly_mod, poly_inv_mod, poly_is_irreducible,
    poly_sqrtmod,
)

# GF(2^4) with x^4 + x + 1
M = 4
IRRED = 0b10011


def test_gf16_mul_identity():
    """Multiplying by 1 is the identity."""
    for a in range(16):
        assert gf2m_mul(a, 1, M, IRRED) == a


def test_gf16_mul_zero():
    """Multiplying by 0 gives 0."""
    for a in range(16):
        assert gf2m_mul(a, 0, M, IRRED) == 0


def test_gf16_mul_inverse():
    """a * inv(a) = 1 for all nonzero a."""
    for a in range(1, 16):
        inv_a = gf2m_inv(a, M, IRRED)
        assert gf2m_mul(a, inv_a, M, IRRED) == 1


def test_gf16_mul_commutative():
    """Multiplication is commutative."""
    for a in range(16):
        for b in range(16):
            assert gf2m_mul(a, b, M, IRRED) == gf2m_mul(b, a, M, IRRED)


def test_gf16_mul_associative():
    """Multiplication is associative for a sample of triples."""
    for a in range(1, 8):
        for b in range(1, 8):
            for c in range(1, 8):
                ab_c = gf2m_mul(gf2m_mul(a, b, M, IRRED), c, M, IRRED)
                a_bc = gf2m_mul(a, gf2m_mul(b, c, M, IRRED), M, IRRED)
                assert ab_c == a_bc


def test_gf8_backward_compat():
    """GF(8) with x^3+x+1 matches Chapter 19 values."""
    m8, irred8 = 3, 0b1011
    assert gf2m_mul(3, 5, m8, irred8) == 4
    for a in range(1, 8):
        assert gf2m_mul(a, gf2m_inv(a, m8, irred8), m8, irred8) == 1


def test_poly_eval_constant():
    """Evaluating a constant polynomial returns that constant."""
    assert poly_eval([7], 3, M, IRRED) == 7


def test_poly_eval_linear():
    """Evaluating c0 + c1*x at x=a gives c0 XOR c1*a."""
    c0, c1, a = 5, 3, 7
    expected = gf2m_add(c0, gf2m_mul(c1, a, M, IRRED))
    assert poly_eval([c0, c1], a, M, IRRED) == expected


def test_poly_mul_degree():
    """deg(f*g) = deg(f) + deg(g) for nonzero polynomials."""
    f = [1, 0, 1]  # 1 + x^2
    g = [3, 1]     # 3 + x
    fg = poly_mul(f, g, M, IRRED)
    assert len(fg) - 1 == (len(f) - 1) + (len(g) - 1)


def test_poly_mod_reduces_degree():
    """f mod g has degree < deg(g)."""
    f = [1, 2, 3, 4, 5]  # degree 4
    g = [8, 7, 1]         # degree 2
    r = poly_mod(f, g, M, IRRED)
    assert len(r) - 1 < len(g) - 1 or (len(r) == 1 and r[0] == 0)


def test_poly_inv_mod_roundtrip():
    """f * f^{-1} mod g = 1."""
    g = [8, 7, 1]  # degree-2 irreducible over GF(16)
    f = [3, 1]     # 3 + x
    f_inv = poly_inv_mod(f, g, M, IRRED)
    product = poly_mod(poly_mul(f, f_inv, M, IRRED), g, M, IRRED)
    assert product == [1]


def test_poly_is_irreducible_degree1():
    """All degree-1 polynomials are irreducible."""
    for c in range(16):
        assert poly_is_irreducible([c, 1], M, IRRED)


def test_poly_is_irreducible_with_root():
    """A polynomial with a root in GF(16) is reducible (for degree >= 2)."""
    # (x - 3)(x - 5) = x^2 + (3 XOR 5)*x + 3*5  in GF(2) arithmetic
    # subtraction = addition = XOR, so (x + 3)(x + 5)
    c0 = gf2m_mul(3, 5, M, IRRED)
    c1 = 3 ^ 5
    poly = [c0, c1, 1]
    assert not poly_is_irreducible(poly, M, IRRED)
    assert poly_eval(poly, 3, M, IRRED) == 0
    assert poly_eval(poly, 5, M, IRRED) == 0


def test_poly_sqrtmod_squares_back():
    """sqrt(f)^2 == f mod g, for every f in a degree-2 quotient ring.

    Squaring is the Frobenius map and therefore a bijection, so every
    element of GF(2^m)[x]/g(x) has exactly one square root.  This walks
    all 256 residues modulo an irreducible g and checks the round trip;
    nothing else in the suite reaches poly_sqrtmod directly, and a wrong
    implementation would otherwise surface only as a Patterson failure.
    """
    g = [8, 7, 1]  # x^2 + 7x + 8, the chapter's irreducible Goppa polynomial
    assert poly_is_irreducible(g, M, IRRED)
    seen = set()
    for c1 in range(16):
        for c0 in range(16):
            f = [c0, c1]
            root = poly_sqrtmod(f, g, M, IRRED)
            back = poly_mod(poly_mul(root, root, M, IRRED), g, M, IRRED)
            padded = back + [0] * (2 - len(back))
            assert padded == f, f"sqrt round trip failed for {f}"
            seen.add(tuple(root + [0] * (2 - len(root))))
    assert len(seen) == 256, "squaring is a bijection, so roots must be distinct"
