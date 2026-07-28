"""Arithmetic in F_p[x] and its quotients: the second setting Chapter 2 defines.

A polynomial is a list of coefficients in ascending order, so ``[2, 1, 3]``
stands for 2 + x + 3x^2. That representation is the one the chapter prints and
the one the lattice chapters keep using: the index is the exponent, which makes
the reduction rule for x^n + 1 a slice-and-negate rather than a lookup.

``poly_mul`` is the textbook O(n^2) double loop. Chapter 9 replaces it with the
number theoretic transform for the specific rings ML-KEM works in; this is the
version the rest of Part II's exposition assumes the reader has in mind.

No routine here trims trailing zero coefficients. The zero polynomial comes
back at whatever length the operation produced, so ``poly_mod`` returns
``[0, 0, 0]`` rather than ``[0]`` or ``[]``. A caller wanting the shortest
representation trims it.
"""


def poly_mul(f: list[int], g: list[int], p: int) -> list[int]:
    """Return f * g in F_p[x], as a coefficient list in ascending order.

    The product of a degree-i term and a degree-j term lands at index i + j, so
    the result has length len(f) + len(g) - 1, which is degree
    deg(f) + deg(g). Every entry is reduced modulo p as it is accumulated
    rather than at the end, which keeps the intermediate integers small.
    """
    # EXERCISE: implement this function.
    #
    # Coefficients are ascending, so index i holds the coefficient of x**i
    # and the product of a degree-i term with a degree-j term lands at index
    # i + j. Allocate len(f) + len(g) - 1 zeros and accumulate the double
    # loop into them, reducing modulo p as you go rather than at the end so
    # the intermediate integers stay small. This is the textbook O(n^2)
    # form; Chapter 9 replaces it with the number theoretic transform.
    #
    # Reference: Chapter 2, 'Polynomials over a finite field'
    #
    # Proved by:
    #   tests/ch02/test_polynomials.py
    raise NotImplementedError("exercise: poly_mul")


def poly_mod(a: list[int], f: list[int], p: int) -> list[int]:
    """Return a mod f in F_p[x], for monic f.

    Long division, one leading term at a time: take the top coefficient of a,
    subtract that multiple of f from the matching tail, and drop the now-zero
    top coefficient. Because f is monic the leading coefficient needs no
    inversion, which is why the monic assumption buys the whole simplification.

    A general f would be handled by dividing through by its leading
    coefficient first, which is always possible over a field.

    Every incoming coefficient is reduced modulo p on the first line, so an
    unreduced input comes back with coefficients in {0, ..., p - 1}. That is
    short of a canonical representative: trailing zero coefficients are left
    in place, per the module docstring. The result is deg(f) long whenever a
    was at least that long to begin with; an input already below that degree
    is returned at its own length, reduced but otherwise untouched.
    """
    # EXERCISE: implement this function.
    #
    # Reduce every incoming coefficient modulo p first, otherwise an input
    # already below deg(f) skips the loop entirely and passes through
    # unreduced. Then long-divide, one leading term at a time: while the
    # working list is still at least as long as f, take its top coefficient,
    # subtract that multiple of f from the matching tail, then pop the
    # now-zero top entry. Because f is monic the leading coefficient needs
    # no inversion, which is the whole simplification the monic assumption
    # buys. Do not trim trailing zeros, so the zero polynomial comes back as
    # a list of zeros deg(f) long.
    #
    # Reference: Chapter 2, 'Polynomial reduction'
    #
    # Proved by:
    #   tests/ch02/test_polynomials.py
    raise NotImplementedError("exercise: poly_mod")


def poly_eval(coeffs: list[int], x: int, p: int) -> int:
    """Return f(x) mod p, where coeffs is f in ascending order.

    Direct evaluation of the sum of c_i * x^i. Horner's rule would use fewer
    multiplications; the direct form is written out because the root search
    below is about which values come back, not about how fast they arrive.
    """
    # EXERCISE: implement this function.
    #
    # Sum c * x**i over the ascending coefficient list, reduced modulo p.
    # Horner's rule would use fewer multiplications; the direct sum is
    # written out because the root search is about which values come back,
    # not about how fast they arrive.
    #
    # Reference: Chapter 2, exercise 3
    #
    # Proved by:
    #   tests/ch02/test_polynomials.py
    raise NotImplementedError("exercise: poly_eval")


def roots(coeffs: list[int], p: int) -> list[int]:
    """Return every element of F_p that is a root of coeffs, as a list.

    Exhaustive: evaluate at all p field elements and keep the zeros. That is
    only tractable because the chapter's primes are tiny, and it is the whole
    method exercise 3 asks for.

    An empty result is the useful case. For a polynomial of degree 2 or 3 over
    a field, having no root is equivalent to being irreducible, because any
    proper factorization of such a polynomial must contain a linear factor and
    a linear factor forces a root. The equivalence stops at degree 4: over F_3,
    (x^2 + 1)^2 is reducible and still has no root.
    """
    # EXERCISE: implement this function.
    #
    # Evaluate at every element of F_p and return the ones that give zero.
    # Exhaustive search is only tractable because the chapter's primes are
    # tiny, and it is exactly the method exercise 3 asks for. The empty
    # result is the useful case: for degree 2 or 3 over a field, no root is
    # equivalent to irreducible, because a proper factorization would have
    # to contain a linear factor and a linear factor forces a root.
    #
    # Reference: Chapter 2, exercise 3
    #
    # Proved by:
    #   tests/ch02/test_polynomials.py
    raise NotImplementedError("exercise: roots")
