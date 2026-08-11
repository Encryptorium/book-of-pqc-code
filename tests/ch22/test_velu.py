"""Tests for Velu's isogeny formulas (isogenies.velu)."""

from isogenies.fp2 import fp2_eq, fp2_zero
from isogenies.curve import (
    INF,
    is_on_curve,
    j_invariant,
    point_add,
    point_order,
    scalar_mul,
)
from isogenies.velu import compute_kernel, velu_eval, velu_isogeny

P = 431
A = (1, 0)
B = (0, 0)

# 2-torsion point on E_0
T2 = ((0, 0), (0, 0))
# Generator of E_0(F_p)
GEN = ((13, 0), (290, 0))


class TestKernel:
    def test_kernel_size(self):
        kernel = compute_kernel(T2, 2, A, P)
        assert len(kernel) == 2
        assert kernel[0] is None  # identity
        assert kernel[1] is not None

    def test_kernel_order3(self):
        # Find a 3-torsion point: 144*GEN has order 3 (432/3=144)
        P3 = scalar_mul(144, GEN, A, P)
        assert point_order(P3, A, P, 432) == 3
        kernel = compute_kernel(P3, 3, A, P)
        assert len(kernel) == 3
        assert kernel[0] is None


class TestVeluEval:
    def test_kernel_maps_to_infinity(self):
        kernel = compute_kernel(T2, 2, A, P)
        assert velu_eval(T2, kernel, A, P) is None

    def test_identity_maps_to_identity(self):
        kernel = compute_kernel(T2, 2, A, P)
        assert velu_eval(INF, kernel, A, P) is None

    def test_image_on_codomain_degree2(self):
        a_new, b_new, kernel, imgs = velu_isogeny(
            T2, 2, A, B, P, aux_points=[GEN],
        )
        phi_G = imgs[0]
        assert phi_G is not None
        assert is_on_curve(phi_G, a_new, b_new, P)

    def test_homomorphism_degree2(self):
        """phi(P + Q) == phi(P) + phi(Q) on the codomain."""
        Q1 = scalar_mul(3, GEN, A, P)
        Q2 = scalar_mul(7, GEN, A, P)
        Q_sum = point_add(Q1, Q2, A, P)

        a_new, b_new, kernel, imgs = velu_isogeny(
            T2, 2, A, B, P, aux_points=[Q1, Q2, Q_sum],
        )
        phi_Q1, phi_Q2, phi_sum = imgs

        # phi(Q1) + phi(Q2) on the codomain
        phi_sum_expected = point_add(phi_Q1, phi_Q2, a_new, P)
        assert phi_sum is not None and phi_sum_expected is not None
        assert fp2_eq(phi_sum[0], phi_sum_expected[0], P)
        assert fp2_eq(phi_sum[1], phi_sum_expected[1], P)


class TestVeluIsogeny:
    def test_codomain_is_valid_curve_degree2(self):
        a_new, b_new, _, _ = velu_isogeny(T2, 2, A, B, P)
        # Discriminant nonzero: 4a^3 + 27b^2 != 0
        from isogenies.fp2 import fp2_add, fp2_int_mul, fp2_mul, fp2_sqr
        disc = fp2_add(
            fp2_int_mul(4, fp2_mul(fp2_sqr(a_new, P), a_new, P), P),
            fp2_int_mul(27, fp2_sqr(b_new, P), P),
            P,
        )
        assert not fp2_eq(disc, fp2_zero(), P)

    def test_j_invariant_changes_degree3(self):
        """A degree-3 isogeny from E_0 changes the j-invariant.

        The degree-2 isogeny from E_0's only F_p 2-torsion point
        (0,0) maps j=1728 back to j=1728 due to extra automorphisms.
        Degree-3 avoids this fixed-point behavior.
        """
        P3 = scalar_mul(144, GEN, A, P)
        a_new, b_new, _, _ = velu_isogeny(P3, 3, A, B, P)
        j_source = j_invariant(A, B, P)
        j_target = j_invariant(a_new, b_new, P)
        assert not fp2_eq(j_source, j_target, P)

    def test_degree3_isogeny(self):
        P3 = scalar_mul(144, GEN, A, P)
        a_new, b_new, kernel, imgs = velu_isogeny(
            P3, 3, A, B, P, aux_points=[GEN],
        )
        phi_G = imgs[0]
        assert phi_G is not None
        assert is_on_curve(phi_G, a_new, b_new, P)
        # Kernel maps to O
        assert velu_eval(P3, kernel, A, P) is None
