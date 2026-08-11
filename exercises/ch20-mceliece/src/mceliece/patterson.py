"""Patterson's decoding algorithm for binary Goppa codes.

Given a received word r, the secret Goppa polynomial g(x), and the
support set L, Patterson's algorithm finds and corrects up to t errors
where t = deg(g).

Steps:
1. Compute syndrome polynomial S(x) = sum_i r_i / (x - L_i) mod g(x)
2. If S(x) = 0, no errors.
3. Compute T(x) = S(x)^{-1} + x mod g(x)
4. Compute tau(x) = sqrt(T(x)) mod g(x)
5. Run extended GCD on (g(x), tau(x)) stopping when the partial
   remainder has degree <= t/2.  Extract sigma(x) = a(x)^2 + x*b(x)^2.
6. Find roots of sigma(x) by exhaustive evaluation over the support.
7. Flip the corresponding bits of r.
"""

from mceliece.gf2m import (
    gf2m_add, gf2m_mul, gf2m_inv,
    poly_eval, poly_mul, poly_mod, poly_inv_mod, poly_sqrtmod,
    _strip, _poly_sub,
)


def _syndrome_poly(
    received: list[int],
    g_coeffs: list[int],
    support: list[int],
    m: int, irred: int,
) -> list[int]:
    """Compute S(x) = sum_{i: r_i=1} 1/(x - L_i) mod g(x).

    We build the rational function numerator/denominator and reduce mod g.
    For small n this is tractable by accumulating partial fractions.
    """
    # EXERCISE: implement this function.
    #
    # Patterson's step 1. For every position where the received word is 1,
    # the term 1/(x - L_i) is the inverse modulo g of the linear polynomial
    # [L_i, 1], since subtraction is XOR and the sign vanishes. Accumulate
    # those inverses with _poly_sub, which is also XOR, and reduce modulo g
    # on the way out. A zero result means the received word is already a
    # codeword. Summing term by term is the transparent route rather than
    # the fast one; production decoders build a single rational function
    # instead.
    #
    # Reference: Chapter 20, 'Patterson's decoding algorithm'
    #
    # Proved by:
    #   tests/ch20/test_patterson.py
    raise NotImplementedError("exercise: _syndrome_poly")


def patterson_decode(
    received: list[int],
    g_coeffs: list[int],
    support: list[int],
    m: int, irred: int,
) -> list[int]:
    """Decode a received word using Patterson's algorithm.

    Returns the corrected codeword (list of n bits).
    Raises ValueError if decoding fails.
    """
    # EXERCISE: implement this function.
    #
    # Follow the chapter's steps in order. Compute S(x) with _syndrome_poly
    # and return the received word unchanged when it is zero. Compute T(x) =
    # S(x)^{-1} + x mod g, take tau = sqrt(T) mod g with poly_sqrtmod, and
    # hand tau to _error_locator_from_sqrt for sigma. Find the error
    # positions by evaluating sigma at every support element and collecting
    # the indices where it vanishes. Raise ValueError when there are none or
    # more than t: that means the word carried more errors than the code can
    # correct, not that sigma was computed wrongly. Otherwise flip those
    # bits of a copy and return it. The support list must already be in the
    # same coordinate order as the received word.
    #
    # Reference: Chapter 20, 'Patterson's decoding algorithm'
    #
    # Proved by:
    #   tests/ch20/test_patterson.py
    #   tests/ch20/test_mceliece_roundtrip.py
    raise NotImplementedError("exercise: patterson_decode")


def _error_locator_from_sqrt(
    tau: list[int],
    g_coeffs: list[int],
    t: int, m: int, irred: int,
) -> list[int]:
    """Extract the error locator polynomial sigma(x) from tau(x).

    sigma(x) = a(x)^2 + x * b(x)^2
    where a(x), b(x) come from the partial GCD of g(x) and tau(x),
    stopping when the remainder degree drops to <= floor(t/2).

    Uses the standard partial-GCD approach from Patterson's algorithm.
    """
    # EXERCISE: implement this function.
    #
    # Patterson's step 4. Run the extended Euclidean algorithm on g and tau
    # but stop early: keep dividing while the current remainder still has
    # degree above floor(t/2), carrying the Bezout coefficient for tau
    # alongside the remainders. At the stopping point a is the remainder and
    # b is its coefficient, and the error locator is sigma = a^2 + x*b^2,
    # where multiplying by x is prepending a zero coefficient. Normalize
    # sigma to monic with the field inverse of its leading coefficient so
    # the caller's root-finding and degree check see a canonical polynomial.
    # The early stop is what makes decoding polynomial in t: a full GCD
    # would run down to a constant and discard the a and b that carry the
    # error positions.
    #
    # Reference: Chapter 20, 'Patterson's decoding algorithm'
    #
    # Proved by:
    #   tests/ch20/test_patterson.py
    #   tests/ch20/test_mceliece_roundtrip.py
    raise NotImplementedError("exercise: _error_locator_from_sqrt")


def _poly_divmod_local(
    f: list[int], g: list[int], m: int, irred: int
) -> tuple[list[int], list[int]]:
    """Polynomial division over GF(2^m): returns (quotient, remainder)."""
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
