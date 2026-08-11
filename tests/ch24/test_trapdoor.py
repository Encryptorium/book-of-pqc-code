"""The Oil-Vinegar trapdoor: what is zero in secret coordinates, and what is not."""

import random

from multivariate.gf import matmul, transpose, quadratic_eval, mat_vec
from multivariate.uov import (
    TOY,
    UOVParams,
    keygen,
    oil_oil_block,
    public_map,
    sample_central_map,
    sample_secret_transformation,
    collapse_to_linear_system,
)


def test_secret_oil_oil_block_is_zero():
    """Every secret form vanishes on oil-oil monomials, by construction."""
    F = sample_central_map(random.Random(0), TOY)
    assert len(F) == TOY.m
    for F_i in F:
        block = oil_oil_block(F_i, TOY)
        assert block == [[0] * TOY.n_o for _ in range(TOY.n_o)]


def test_public_oil_oil_block_is_generally_nonzero():
    """Mixing by T destroys the visible structure for at least one form."""
    secret = keygen(random.Random(0), TOY)
    blocks = [oil_oil_block(P_i, TOY) for P_i in secret.public.P]
    assert any(any(entry != 0 for row in block for entry in row) for block in blocks)


def test_public_map_is_the_congruence_transform():
    """P_i equals T^T F_i T entrywise, not some other composition order."""
    rng = random.Random(3)
    T = sample_secret_transformation(rng, TOY)
    F = sample_central_map(rng, TOY)
    P = public_map(F, T, TOY)
    T_t = transpose(T)
    for F_i, P_i in zip(F, P):
        assert P_i == matmul(matmul(T_t, F_i, TOY.q), T, TOY.q)


def test_public_form_at_x_equals_central_form_at_Tx():
    """The congruence transform is exactly the substitution P(x) = F(Tx)."""
    rng = random.Random(11)
    secret = keygen(rng, TOY)
    for _ in range(20):
        x = [rng.randrange(TOY.q) for _ in range(TOY.n)]
        y = mat_vec(secret.T, x, TOY.q)
        for F_i, P_i in zip(secret.F, secret.public.P):
            assert quadratic_eval(P_i, x, TOY.q) == quadratic_eval(F_i, y, TOY.q)


def test_collapse_reproduces_the_central_map_on_a_full_vector():
    """L . oil + c must equal F(vinegar || oil) for any oil values."""
    rng = random.Random(5)
    F = sample_central_map(rng, TOY)
    vinegar = [rng.randrange(TOY.q) for _ in range(TOY.n_v)]
    zero_target = [0] * TOY.m
    L, rhs = collapse_to_linear_system(F, vinegar, zero_target, TOY)
    # rhs = -c, so c = -rhs.
    c = [(-value) % TOY.q for value in rhs]
    for _ in range(20):
        oil = [rng.randrange(TOY.q) for _ in range(TOY.n_o)]
        y = list(vinegar) + oil
        for i, F_i in enumerate(F):
            linear = sum(L[i][l] * oil[l] for l in range(TOY.m)) % TOY.q
            assert (linear + c[i]) % TOY.q == quadratic_eval(F_i, y, TOY.q)


def test_toy_parameters_are_unbalanced():
    assert TOY.is_unbalanced()
    assert TOY.n_v == 3
    assert TOY.n_o == 2


def test_balanced_parameters_are_rejected_by_the_predicate():
    """n = 2m is the Kipnis-Shamir 1998 case, and the predicate says so."""
    assert UOVParams(n=4, m=2, q=7).is_unbalanced() is False
