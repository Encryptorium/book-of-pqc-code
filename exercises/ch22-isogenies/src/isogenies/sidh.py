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
    # EXERCISE: implement this function.
    #
    # The kernel generator R_A = P_A + alpha * Q_A has order 2^e_A for every
    # alpha, which is why the secret is one scalar rather than a pair of
    # them. Reduce alpha modulo L_A ** E_A, form R_A on E_0 with A0 as the
    # curve coefficient, walk the 2-isogeny chain with _walk_isogeny_chain,
    # and pass Bob's basis [PB, QB] as the auxiliary points. Return the
    # codomain coefficients and the two torsion images in that order.
    # Publishing those images is what makes the exchange work and is also
    # exactly the data the Castryck-Decru attack consumes.
    #
    # Reference: Chapter 22, 'The SIDH protocol'
    #
    # Proved by:
    #   tests/ch22/test_sidh.py
    raise NotImplementedError("exercise: keygen_alice")


def keygen_bob(
    beta: int,
) -> tuple[Fp2, Fp2, Point, Point]:
    """Bob generates his public key.

    Computes the kernel generator R_B = P_B + beta * Q_B (order 27),
    walks the 3-isogeny chain E_0 -> E_B, and pushes Alice's torsion
    basis {P_A, Q_A} through.

    Returns (a_B, b_B, phi_B(P_A), phi_B(Q_A)).
    """
    # EXERCISE: implement this function.
    #
    # The mirror of keygen_alice with the roles of the two primes swapped:
    # R_B = P_B + beta * Q_B has order 3^e_B, the chain is E_B steps of
    # degree L_B, and the auxiliary points pushed through are Alice's basis
    # [PA, QA]. Reduce beta modulo L_B ** E_B. Nothing else changes, which
    # is the symmetry that makes the Diffie-Hellman analogy hold.
    #
    # Reference: Chapter 22, 'The SIDH protocol'
    #
    # Proved by:
    #   tests/ch22/test_sidh.py
    raise NotImplementedError("exercise: keygen_bob")


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
    # EXERCISE: implement this function.
    #
    # Alice repeats her own secret on Bob's curve. Form the kernel
    # phi_B(P_A) + alpha * phi_B(Q_A) using a_B as the curve coefficient
    # rather than A0, because these points live on E_B and not on E_0. Walk
    # E_A steps of degree L_A from (a_B, b_B) with no auxiliary points, and
    # return the j-invariant of where it lands. The result is j(E_0 / <R_A,
    # R_B>), which is what Bob reaches from the other side; returning j
    # rather than the coefficient pair is what makes the two answers
    # comparable.
    #
    # Reference: Chapter 22, 'The SIDH protocol'
    #
    # Proved by:
    #   tests/ch22/test_sidh.py
    raise NotImplementedError("exercise: derive_alice")


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
    # EXERCISE: implement this function.
    #
    # The mirror of derive_alice: build the kernel phi_A(P_B) + beta *
    # phi_A(Q_B) on Alice's curve using a_A as the coefficient, walk E_B
    # steps of degree L_B, and return the j-invariant. Reduce beta modulo
    # L_B ** E_B first, as keygen_bob did, or a large beta selects a
    # different kernel here than it did there and the two sides disagree.
    #
    # Reference: Chapter 22, 'The SIDH protocol'
    #
    # Proved by:
    #   tests/ch22/test_sidh.py
    raise NotImplementedError("exercise: derive_bob")


def sidh_exchange(
    alpha: int, beta: int,
) -> tuple[Fp2, Fp2]:
    """Run the full SIDH key exchange and return both shared secrets.

    If the protocol is correct, j_alice == j_bob.
    """
    # EXERCISE: implement this function.
    #
    # Run both key generations, then feed each party's published data to the
    # other's derivation, and return the two j-invariants as a pair. They
    # agree because quotienting by <R_A> and <R_B> commutes: both parties
    # land on a curve isomorphic to E_0 / <R_A, R_B>. Returning both values
    # rather than one is what lets the tests check that agreement instead of
    # assuming it.
    #
    # Reference: Chapter 22, 'The SIDH protocol'
    #
    # Proved by:
    #   tests/ch22/test_sidh.py
    raise NotImplementedError("exercise: sidh_exchange")
