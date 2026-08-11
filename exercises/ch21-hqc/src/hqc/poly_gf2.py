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
    # EXERCISE: implement this function.
    #
    # Hamming weight, the number of nonzero coefficients. Coefficients are 0
    # or 1, so summing the list gives it directly. The whole noise budget is
    # stated in this unit: decryption succeeds when the weight of r2*x +
    # r1*y + e spreads thinly enough across the repetition blocks, and the
    # tests use it to confirm the sampled secrets carry exactly w ones.
    #
    # Reference: Chapter 21, 'Noise budget'
    #
    # Proved by:
    #   tests/ch21/test_poly_gf2.py
    #   tests/ch21/test_hqc_noise_budget.py
    raise NotImplementedError("exercise: poly_weight")
