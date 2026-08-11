"""Toy SIDH key exchange at p = 431 = 2^4 * 3^3 - 1.

The starting curve is E_0: y^2 = x^3 + x over F_{431^2}, which is
supersingular with #E_0(F_p) = 432 = 2^4 * 3^3.  Alice walks 4 steps
of degree-2 isogenies (kernel order 16) and Bob walks 3 steps of
degree-3 isogenies (kernel order 27).  The shared secret is the
j-invariant of the curve reached by both parties.

SIDH was broken by Castryck and Decru in 2022.  This implementation
is for pedagogical purposes only.
"""

from __future__ import annotations

from isogenies.fp2 import fp2_scalar, fp2_zero
from isogenies.curve import (
    Fp2,
    Point,
    j_invariant,
    point_add,
    point_order,
    scalar_mul,
)
from isogenies.velu import velu_isogeny


# ---- Fixed parameters ------------------------------------------------

P = 431  # prime, 431 = 2^4 * 3^3 - 1
E_A = 4  # Alice: 4 steps of degree-2 isogenies
E_B = 3  # Bob:   3 steps of degree-3 isogenies
L_A = 2  # Alice's isogeny prime
L_B = 3  # Bob's isogeny prime

# Starting curve E_0: y^2 = x^3 + x, i.e., a = 1, b = 0 in F_{p^2}.
A0: Fp2 = (1, 0)
B0: Fp2 = (0, 0)

# Torsion bases (precomputed and verified).
# P_A, Q_A generate E_0[16] over F_{p^2}.
# P_B, Q_B generate E_0[27] over F_{p^2}.
PA: Point = ((372, 0), (48, 0))
QA: Point = ((178, 168), (190, 428))
PB: Point = ((123, 0), (396, 0))
QB: Point = ((128, 133), (47, 6))


# ---- Isogeny chain walk ---------------------------------------------

def _walk_isogeny_chain(
    kernel_gen: Point,
    l: int,
    e: int,
    a: Fp2,
    b: Fp2,
    aux: list[Point],
) -> tuple[Fp2, Fp2, list[Point]]:
    """Walk an l^e isogeny as e steps of degree-l isogenies.

    At each step, the current kernel generator has order l^(remaining).
    We scale it by l^(remaining-1) to get a point of order l, apply
    Velu to get the next curve, and push the remaining kernel generator
    and auxiliary points through the isogeny.

    Returns (a', b', aux_images) for the final codomain curve.
    """
    current_gen = kernel_gen
    current_a = a
    current_b = b
    current_aux = list(aux)

    for step in range(e):
        remaining = e - step
        # Scale kernel_gen by l^{remaining-1} to get order-l point.
        scale = l ** (remaining - 1)
        step_kernel = scalar_mul(scale, current_gen, current_a, P)

        # Points to push through: the kernel gen itself + aux points.
        push = [current_gen] + current_aux
        new_a, new_b, _kernel, images = velu_isogeny(
            step_kernel, l, current_a, current_b, P, aux_points=push,
        )

        current_gen = images[0]
        current_aux = images[1:]
        current_a = new_a
        current_b = new_b

    return current_a, current_b, current_aux


# ---- SIDH protocol ---------------------------------------------------

def sidh_params() -> dict:
    """Return the fixed SIDH parameter set."""
    return {
        "p": P,
        "a": A0, "b": B0,
        "e_A": E_A, "e_B": E_B,
        "l_A": L_A, "l_B": L_B,
        "PA": PA, "QA": QA,
        "PB": PB, "QB": QB,
    }


def keygen_alice(
    alpha: int,
) -> tuple[Fp2, Fp2, Point, Point]:
    """Alice generates her public key.

    Computes the kernel generator R_A = P_A + alpha * Q_A (order 16),
    walks the 2-isogeny chain E_0 -> E_A, and pushes Bob's torsion
    basis {P_B, Q_B} through.

    Returns (a_A, b_A, phi_A(P_B), phi_A(Q_B)).
    """
    RA = point_add(PA, scalar_mul(alpha % (L_A ** E_A), QA, A0, P), A0, P)
    a_A, b_A, aux_images = _walk_isogeny_chain(
        RA, L_A, E_A, A0, B0, [PB, QB],
    )
    return a_A, b_A, aux_images[0], aux_images[1]


def keygen_bob(
    beta: int,
) -> tuple[Fp2, Fp2, Point, Point]:
    """Bob generates his public key.

    Computes the kernel generator R_B = P_B + beta * Q_B (order 27),
    walks the 3-isogeny chain E_0 -> E_B, and pushes Alice's torsion
    basis {P_A, Q_A} through.

    Returns (a_B, b_B, phi_B(P_A), phi_B(Q_A)).
    """
    RB = point_add(PB, scalar_mul(beta % (L_B ** E_B), QB, A0, P), A0, P)
    a_B, b_B, aux_images = _walk_isogeny_chain(
        RB, L_B, E_B, A0, B0, [PA, QA],
    )
    return a_B, b_B, aux_images[0], aux_images[1]


def derive_alice(
    alpha: int,
    a_B: Fp2,
    b_B: Fp2,
    phiB_PA: Point,
    phiB_QA: Point,
) -> Fp2:
    """Alice derives the shared secret from Bob's public key.

    Computes j(E_B / <phi_B(P_A) + alpha * phi_B(Q_A)>).
    """
    kernel = point_add(
        phiB_PA,
        scalar_mul(alpha % (L_A ** E_A), phiB_QA, a_B, P),
        a_B, P,
    )
    a_AB, b_AB, _ = _walk_isogeny_chain(
        kernel, L_A, E_A, a_B, b_B, [],
    )
    return j_invariant(a_AB, b_AB, P)


def derive_bob(
    beta: int,
    a_A: Fp2,
    b_A: Fp2,
    phiA_PB: Point,
    phiA_QB: Point,
) -> Fp2:
    """Bob derives the shared secret from Alice's public key.

    Computes j(E_A / <phi_A(P_B) + beta * phi_A(Q_B)>).
    """
    kernel = point_add(
        phiA_PB,
        scalar_mul(beta % (L_B ** E_B), phiA_QB, a_A, P),
        a_A, P,
    )
    a_AB, b_AB, _ = _walk_isogeny_chain(
        kernel, L_B, E_B, a_A, b_A, [],
    )
    return j_invariant(a_AB, b_AB, P)


def sidh_exchange(
    alpha: int, beta: int,
) -> tuple[Fp2, Fp2]:
    """Run the full SIDH key exchange and return both shared secrets.

    If the protocol is correct, j_alice == j_bob.
    """
    a_A, b_A, phiA_PB, phiA_QB = keygen_alice(alpha)
    a_B, b_B, phiB_PA, phiB_QA = keygen_bob(beta)

    j_alice = derive_alice(alpha, a_B, b_B, phiB_PA, phiB_QA)
    j_bob = derive_bob(beta, a_A, b_A, phiA_PB, phiA_QB)

    return j_alice, j_bob
