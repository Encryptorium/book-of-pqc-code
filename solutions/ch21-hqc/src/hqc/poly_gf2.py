"""Polynomial arithmetic in GF(2)[x]/(x^n - 1).

Polynomials are represented as ``list[int]`` of length *n*, where index *i*
holds the coefficient of x^i.  All coefficients are 0 or 1.
"""


def poly_add(a: list[int], b: list[int]) -> list[int]:
    """Componentwise XOR (addition in GF(2))."""
    return [ai ^ bi for ai, bi in zip(a, b)]


def poly_mul(a: list[int], b: list[int], n: int) -> list[int]:
    """Polynomial multiplication mod x^n - 1 over GF(2).

    This is circulant convolution: c[k] = sum_{i} a[i]*b[(k-i) mod n] mod 2.
    Naive O(n^2), which is fine for toy parameters.
    """
    c = [0] * n
    for i in range(n):
        if a[i] == 0:
            continue
        for j in range(n):
            if b[j]:
                c[(i + j) % n] ^= 1
    return c


def poly_weight(a: list[int]) -> int:
    """Hamming weight (number of nonzero coefficients)."""
    return sum(a)
