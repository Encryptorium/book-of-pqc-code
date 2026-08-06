"""The negacyclic number theoretic transform for R_q = Z_q[x]/(x^n + 1).

Let q be a prime with 2n | q - 1 and let psi in Z_q be a primitive
2n-th root of unity. The negacyclic NTT is the map

    fhat[k] = sum_{i=0}^{n-1} f[i] * psi^(i * (2k + 1))   mod q

for k = 0, 1, ..., n - 1. Equivalently fhat[k] = f(psi^(2k + 1)),
the evaluation of the polynomial f at the odd powers of psi, which
are the roots of x^n + 1 over Z_q (because psi^(2n) = 1 and psi^n
= -1, so the 2n roots of unity split into x^n - 1 and x^n + 1,
and the odd powers of psi land on the second factor).

The inverse is derived by the orthogonality relation

    sum_{k=0}^{n-1} psi^((i - j)(2k + 1)) = n * [i == j]    mod q

(proof: the outer factor psi^(i - j) is constant in k, the inner
sum over psi^(2k(i - j)) is a geometric series in omega = psi^2,
which has order n, so the sum is n when i = j and 0 otherwise).
Rearranging gives

    f[j] = n^(-1) * sum_{k=0}^{n-1} fhat[k] * psi^(-j * (2k + 1))  mod q.

The NTT turns multiplication in R_q into pointwise multiplication
in Z_q^n: fhat * ghat pointwise equals the NTT of f * g in R_q.
The asymptotic cost of the direct-definition implementation below
is O(n^2), the same as the schoolbook convolution. Production
implementations (Longa-Naehrig 2016, Seiler 2018) use an iterative
Cooley-Tukey decimation layered with the negacyclic pre-twist to
reach O(n log n) and fit the resulting butterflies into constant
time. The chapter slice stays with the direct definition for
clarity; the iterative form can be dropped in later.
"""

from __future__ import annotations

import numpy as np

from .params import RingParams


# Cache keyed by (n, q) so repeated NTT calls don't re-find psi.
_PSI_CACHE: dict[tuple[int, int], int] = {}


def primitive_2n_root(n: int, q: int) -> int:
    """Return a primitive 2n-th root of unity in Z_q.

    Brute-force search over psi = 2, 3, ..., q - 1. For each
    candidate, check psi^(2n) = 1 and psi^(2n / p) != 1 for every
    prime p dividing 2n. At the toy scale used by Chapter 9 this is
    a handful of modular exponentiations.
    """
    # EXERCISE: implement this function.
    #
    # Set order = 2n and assert that order divides q - 1, naming order in
    # the message, because Z_q has an element of that order only then.
    # Return the cached value for (n, q) if one is there. Otherwise collect
    # the distinct primes dividing order, then try psi = 2, 3, ..., q - 1 in
    # turn and keep the first psi with pow(psi, order, q) == 1 and pow(psi,
    # order // p, q) != 1 for every such prime p. The second condition is
    # what forces the order to be exactly 2n rather than a proper divisor of
    # it. Cache the hit before returning.
    #
    # Reference: Chapter 9, 'The number theoretic transform'
    #
    # Proved by:
    #   tests/ch09/test_ntt.py
    raise NotImplementedError("exercise: primitive_2n_root")


def ntt_forward(f: np.ndarray, params: RingParams) -> np.ndarray:
    """Negacyclic NTT of f in R_q, using the direct definition.

    Returns a length-n int64 array fhat with fhat[k] =
    sum_i f[i] * psi^(i * (2k + 1)) mod q.
    """
    f = np.asarray(f, dtype=np.int64) % params.q
    assert f.shape == (params.n,), (
        f"ntt_forward: expected length-{params.n}, got shape {f.shape}"
    )
    n, q = params.n, params.q
    psi = primitive_2n_root(n, q)
    fhat = np.zeros(n, dtype=np.int64)
    for k in range(n):
        acc = 0
        for i in range(n):
            acc += int(f[i]) * pow(psi, i * (2 * k + 1), q)
        fhat[k] = acc % q
    return fhat


def ntt_inverse(fhat: np.ndarray, params: RingParams) -> np.ndarray:
    """Negacyclic inverse NTT, using the direct definition.

    Returns a length-n int64 array f with f[j] =
    n^(-1) * sum_k fhat[k] * psi^(-j * (2k + 1)) mod q.
    """
    fhat = np.asarray(fhat, dtype=np.int64) % params.q
    assert fhat.shape == (params.n,), (
        f"ntt_inverse: expected length-{params.n}, got shape {fhat.shape}"
    )
    n, q = params.n, params.q
    psi = primitive_2n_root(n, q)
    psi_inv = pow(psi, -1, q)
    n_inv = pow(n, -1, q)
    f = np.zeros(n, dtype=np.int64)
    for j in range(n):
        acc = 0
        for k in range(n):
            acc += int(fhat[k]) * pow(psi_inv, j * (2 * k + 1), q)
        f[j] = (n_inv * acc) % q
    return f


def ring_mul_ntt(
    f: np.ndarray, g: np.ndarray, params: RingParams
) -> np.ndarray:
    """Multiply two elements of R_q via the NTT.

    Forward-transforms both inputs, pointwise-multiplies in the NTT
    domain, inverse-transforms the product. Output agrees with
    ring_mul_naive(f, g, q) for every (f, g) at any params admitting
    a negacyclic NTT.
    """
    # EXERCISE: implement this function.
    #
    # Forward-transform f and g, multiply the two transforms entry by entry
    # modulo q, and inverse-transform the product. Evaluation at the n roots
    # of x^n + 1 is a ring isomorphism from R_q onto Z_q^n, so a
    # coefficient-domain ring product becomes a coordinate-wise product on
    # the other side. The result must agree with ring_mul_naive on every
    # input.
    #
    # Reference: Chapter 9, 'The number theoretic transform'
    #
    # Proved by:
    #   tests/ch09/test_ntt.py
    raise NotImplementedError("exercise: ring_mul_ntt")
