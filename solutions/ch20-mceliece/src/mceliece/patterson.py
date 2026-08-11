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
    t = len(g_coeffs) - 1
    # S(x) = sum_{i: r_i=1} g(L_i)^{-1} * prod_{j!=i, r_j=1} (x - L_j)
    # Simpler approach for toy sizes: evaluate coefficient by coefficient.
    # Build S(x) = sum_{i: r_i=1} 1/(x - L_i) mod g(x)
    # = sum_{i: r_i=1} inv_of_(x - L_i) mod g(x)

    # For each error position, compute (x - L_i)^{-1} mod g(x) and add.
    S = [0]
    for i, ri in enumerate(received):
        if ri == 0:
            continue
        # (x - L_i) = [L_i, 1] since subtraction in GF(2) is addition
        linear = [support[i], 1]
        inv_linear = poly_inv_mod(linear, g_coeffs, m, irred)
        S = _poly_sub(S, inv_linear)
        # note: _poly_sub is XOR, same as addition in GF(2)
    return poly_mod(S, g_coeffs, m, irred)


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
    t = len(g_coeffs) - 1
    n = len(support)

    # Step 1: syndrome
    S = _syndrome_poly(received, g_coeffs, support, m, irred)

    # Step 2: zero syndrome means no errors
    if len(S) == 1 and S[0] == 0:
        return list(received)

    # Step 3: T(x) = S(x)^{-1} + x mod g(x)
    S_inv = poly_inv_mod(S, g_coeffs, m, irred)
    # x = [0, 1]
    T = _poly_sub(S_inv, [0, 1])
    T = poly_mod(T, g_coeffs, m, irred)

    # Step 4: tau(x) = sqrt(T(x)) mod g(x)
    tau = poly_sqrtmod(T, g_coeffs, m, irred)

    # Step 5: partial GCD to find error locator
    # Run extended GCD on g(x) and tau(x), stopping when the remainder
    # has degree <= t // 2.
    sigma = _error_locator_from_sqrt(tau, g_coeffs, t, m, irred)

    # Step 6: find roots by exhaustive evaluation
    error_positions = []
    for i, lj in enumerate(support):
        if poly_eval(sigma, lj, m, irred) == 0:
            error_positions.append(i)

    if len(error_positions) == 0 or len(error_positions) > t:
        raise ValueError(
            f"decoding failed: found {len(error_positions)} error positions, "
            f"expected 1..{t}"
        )

    # Step 7: correct errors
    corrected = list(received)
    for pos in error_positions:
        corrected[pos] ^= 1
    return corrected


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
    # Partial extended GCD: start with r0 = g, r1 = tau
    # Track: r_old, r, s_old, s (we need s for b)
    r_old = list(g_coeffs)
    r_cur = list(tau)
    s_old = [0]
    s_cur = [1]

    threshold = t // 2

    while len(r_cur) - 1 > threshold:
        # one step of the euclidean algorithm
        q, rem = _poly_divmod_local(r_old, r_cur, m, irred)
        r_old, r_cur = r_cur, rem
        s_old, s_cur = s_cur, _poly_sub(s_old, poly_mul(q, s_cur, m, irred))

    # a(x) = r_cur, b(x) = s_cur
    a = r_cur
    b = s_cur

    # sigma(x) = a(x)^2 + x * b(x)^2
    a_sq = poly_mul(a, a, m, irred)
    b_sq = poly_mul(b, b, m, irred)
    x_b_sq = [0] + b_sq  # multiply by x
    sigma = _poly_sub(a_sq, x_b_sq)

    # normalize to monic
    if sigma[-1] != 1:
        lc_inv = gf2m_inv(sigma[-1], m, irred)
        sigma = [gf2m_mul(c, lc_inv, m, irred) for c in sigma]

    return _strip(sigma)


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
