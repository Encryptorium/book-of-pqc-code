"""A toy Unbalanced Oil and Vinegar signature scheme over GF(q).

This is the scheme Chapter 24 builds at (n, m, q) = (5, 2, 7), written so that
the parameters are arguments rather than module globals. The structure is the
one the chapter describes:

    keygen   sample an invertible T; sample m central quadratic forms whose
             oil-oil block is zero; publish P_i = T^T F_i T
    sign     fix the vinegar variables, which collapses each F_i to an affine
             function of the oil variables; solve the resulting m x m linear
             system; map back through T^{-1}
    verify   evaluate every public form at the signature and compare to the
             target componentwise

It is a toy. The parameters are several orders of magnitude too small to
resist MinRank or Grobner-basis attacks, the field is prime rather than an
extension field, and there is no message hashing, no salt, and no EUF-CMA
argument. It exists to make the oil-vinegar collapse visible, not to sign
anything.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .gf import matmul, transpose, mat_vec, quadratic_eval
from .linalg import is_invertible, invert_mat, solve_linear

Matrix = list[list[int]]
Vector = list[int]


@dataclass(frozen=True)
class UOVParams:
    """One UOV parameter set.

    ``n`` is the total number of variables, ``m`` the number of equations, and
    ``q`` the field size. The number of oil variables equals ``m``, so the
    number of vinegar variables is ``n - m``. Unbalanced means ``n > 2m``; the
    chapter's toy takes n = 5, m = 2, which satisfies it with one variable to
    spare.
    """

    n: int
    m: int
    q: int

    @property
    def n_v(self) -> int:
        """Number of vinegar variables, n - m."""
        return self.n - self.m

    @property
    def n_o(self) -> int:
        """Number of oil variables, which UOV sets equal to m."""
        return self.m

    def is_unbalanced(self) -> bool:
        """True when n > 2m, the condition Kipnis-Shamir 1998 forces."""
        # EXERCISE: implement this function.
        #
        # Return whether n > 2m. Balanced Oil-Vinegar takes n = 2m and is
        # broken in polynomial time by Kipnis-Shamir 1998; the unbalanced
        # choice is the whole response to that attack, and the attack cost
        # grows as q^(n - 2m), so the strict inequality is the security
        # condition rather than a style preference. Note that n >= 2m is
        # required for the scheme to make sense at all, since there are m
        # oil variables.
        #
        # Reference: Chapter 24, 'The MQ problem and the Oil-Vinegar trapdoor'
        #
        # Proved by:
        #   tests/ch24/test_trapdoor.py
        raise NotImplementedError("exercise: UOVParams.is_unbalanced")


TOY = UOVParams(n=5, m=2, q=7)
"""The chapter's toy parameters: three vinegar variables, two oil, over GF(7)."""


@dataclass(frozen=True)
class PublicKey:
    """The m public quadratic forms, each an n x n matrix over GF(q)."""

    params: UOVParams
    P: list[Matrix]


@dataclass(frozen=True)
class SecretKey:
    """The secret central map F and transformation T, plus the public key."""

    params: UOVParams
    F: list[Matrix]
    T: Matrix
    public: PublicKey


def sample_secret_transformation(rng: random.Random, params: UOVParams) -> Matrix:
    """Sample a uniformly random invertible n x n matrix over GF(q).

    Resamples until invertible. Over GF(q) a random square matrix is singular
    with probability roughly 1/q, so the loop is short.
    """
    while True:
        T = [[rng.randrange(params.q) for _ in range(params.n)] for _ in range(params.n)]
        if is_invertible(T, params.q):
            return T


def sample_central_map(rng: random.Random, params: UOVParams) -> list[Matrix]:
    """Sample m quadratic forms whose oil-oil block is zero.

    Every entry is uniform, then the bottom-right ``m x m`` block, the one
    indexing oil against oil, is overwritten with zeros. That single erasure is
    the entire trapdoor: it is what makes each form affine in the oil variables
    once the vinegar variables are fixed.
    """
    n, n_v = params.n, params.n_v
    F = []
    for _ in range(params.m):
        F_i = [[rng.randrange(params.q) for _ in range(n)] for _ in range(n)]
        for r in range(n_v, n):
            for c in range(n_v, n):
                F_i[r][c] = 0
        F.append(F_i)
    return F


def oil_oil_block(Mat: Matrix, params: UOVParams) -> Matrix:
    """Return the oil-oil sub-block of one quadratic form.

    Rows and columns ``n_v`` through ``n - 1``, the monomials that multiply two
    oil variables. Zero for every secret form by construction, and in general
    nonzero for every public form.
    """
    # EXERCISE: implement this function.
    #
    # Slice out rows and columns n_v through n-1 of the matrix, the entries
    # indexing an oil variable against an oil variable, and return them as a
    # list of rows. Keep the row and column order of the parent matrix so
    # the block reads as a sub-block rather than a set. This is the block
    # Oil-Vinegar forces to zero in every secret form, and the one that is
    # in general nonzero in every public form; Chapter 24's Exercise 2 asks
    # you to print both and compare.
    #
    # Reference: Chapter 24, 'The MQ problem and the Oil-Vinegar trapdoor'
    #
    # Proved by:
    #   tests/ch24/test_trapdoor.py
    raise NotImplementedError("exercise: oil_oil_block")


def public_map(F: list[Matrix], T: Matrix, params: UOVParams) -> list[Matrix]:
    """Mix the central map by T: P_i = T^T . F_i . T.

    This is the composition P(x) = F(Tx) written in quadratic-form notation,
    since x^T (T^T F_i T) x = (Tx)^T F_i (Tx).
    """
    T_t = transpose(T)
    return [matmul(matmul(T_t, F_i, params.q), T, params.q) for F_i in F]


def keygen(rng: random.Random, params: UOVParams = TOY) -> SecretKey:
    """Generate a UOV keypair.

    Samples T first, then the central map, so that a caller seeding ``rng``
    reproduces the chapter's printed key exactly.
    """
    T = sample_secret_transformation(rng, params)
    F = sample_central_map(rng, params)
    P = public_map(F, T, params)
    return SecretKey(params=params, F=F, T=T, public=PublicKey(params=params, P=P))


def collapse_to_linear_system(
    F: list[Matrix], vinegar: Vector, target: Vector, params: UOVParams
) -> tuple[Matrix, Vector]:
    """Fix the vinegar variables and return the linear system in the oil ones.

    For each central form, the vinegar-only monomials contribute a constant and
    the vinegar-oil monomials contribute a coefficient on each oil variable.
    Both the ``F_i[j][oil]`` and ``F_i[oil][j]`` entries multiply the same
    monomial ``y_j * y_oil``, so the coefficient is their sum.

    Returns ``(L, rhs)`` with ``L`` an m x m matrix and ``rhs = target - c``.
    """
    n_v, m, q = params.n_v, params.m, params.q
    L: Matrix = []
    rhs: Vector = []
    for i, F_i in enumerate(F):
        c_i = sum(
            F_i[j][k] * vinegar[j] * vinegar[k] for j in range(n_v) for k in range(n_v)
        ) % q
        row = [
            sum((F_i[j][n_v + l] + F_i[n_v + l][j]) * vinegar[j] for j in range(n_v)) % q
            for l in range(m)
        ]
        L.append(row)
        rhs.append((target[i] - c_i) % q)
    return L, rhs


def sign(
    secret: SecretKey, target: Vector, rng: random.Random, max_attempts: int = 100
) -> Vector:
    """Sign a target vector, returning a signature in public coordinates.

    Resamples the vinegar variables whenever the collapsed system is singular.
    Raises RuntimeError after ``max_attempts``; at sane parameters that never
    fires, since a random m x m matrix over GF(q) is invertible with
    probability bounded below by a constant.
    """
    params = secret.params
    if len(target) != params.m:
        raise ValueError(f"target must have {params.m} entries, got {len(target)}")
    for _ in range(max_attempts):
        vinegar = [rng.randrange(params.q) for _ in range(params.n_v)]
        L, rhs = collapse_to_linear_system(secret.F, vinegar, target, params)
        oil = solve_linear(L, rhs, params.q)
        if oil is None:
            continue
        y = list(vinegar) + list(oil)
        return mat_vec(invert_mat(secret.T, params.q), y, params.q)
    raise RuntimeError(f"no invertible oil system in {max_attempts} attempts")


def verify(public: PublicKey, target: Vector, signature: Vector) -> bool:
    """Evaluate every public form at the signature and compare to the target.

    The verifier never sees F, T, or the vinegar-oil split.
    """
    params = public.params
    if len(signature) != params.n:
        return False
    evaluated = [quadratic_eval(P_i, signature, params.q) for P_i in public.P]
    return evaluated == list(target)
