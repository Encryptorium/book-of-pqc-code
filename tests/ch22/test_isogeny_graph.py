"""Tests for supersingular isogeny graph structure."""

from isogenies.fp2 import fp2_eq, fp2_zero
from isogenies.curve import (
    is_on_curve,
    j_invariant,
    point_add,
    scalar_mul,
)
from isogenies.velu import velu_isogeny

P = 431
A = (1, 0)
B = (0, 0)
GEN = ((13, 0), (290, 0))  # order 432 on E_0(F_p)


def _j_key(j):
    """Normalize a j-invariant to a hashable key."""
    return (j[0] % P, j[1] % P)


def _neighbours_via_one_generator(a, b, p, l, gen, gen_order):
    """Walk the order-l points inside ONE cyclic group and take their images.

    This is a restricted search, not an enumeration of kernels. It scales
    a single generator ``gen``, so every point it can reach lies in the
    order-l subgroup of ``<gen>``, which is one of the l+1 order-l
    subgroups of the full l-torsion. Reaching all of them needs a torsion
    BASIS and the combinations P + [k]Q, which this helper does not build.

    Returns ``(kernel_point, a_codomain, b_codomain, j_key)`` four-tuples,
    deduplicated by codomain j-invariant. Note that deduplicating on j is
    not in general a one-to-one test of distinct kernels: two different
    kernels can land on isomorphic codomains, so this collapses rather
    than counts them.
    """
    cofactor = gen_order // l
    pts = []
    for k in range(1, l):
        pt = scalar_mul(cofactor * k, gen, a, p)
        if pt is not None:
            pts.append(pt)
    # Deduplicate: keep one generator per subgroup
    subgroups = []
    seen_j = set()
    for pt in pts:
        a_new, b_new, _, _ = velu_isogeny(pt, l, a, b, p)
        j_new = _j_key(j_invariant(a_new, b_new, p))
        if j_new not in seen_j:
            seen_j.add(j_new)
            subgroups.append((pt, a_new, b_new, j_new))
    return subgroups


class TestIsogenyGraph:
    def test_3isogeny_from_e0(self):
        """E_0 has at least one distinct 3-isogeny neighbor."""
        # 3-torsion: 144*GEN has order 3
        P3 = scalar_mul(144, GEN, A, P)
        a_new, b_new, _, _ = velu_isogeny(P3, 3, A, B, P)
        j_start = _j_key(j_invariant(A, B, P))
        j_new = _j_key(j_invariant(a_new, b_new, P))
        assert j_new != j_start

    def test_3isogeny_graph_bfs(self):
        """BFS via 3-isogenies reaches multiple j-invariants."""
        j_start = _j_key(j_invariant(A, B, P))
        # We need to track curve coefficients and a generator for each
        visited = {j_start}
        queue = [(A, B, GEN, 432)]

        for _ in range(3):  # limited depth for speed
            next_queue = []
            for a_cur, b_cur, gen_cur, order_cur in queue:
                for pt, a_new, b_new, j_new in _neighbours_via_one_generator(
                    a_cur, b_cur, P, 3, gen_cur, order_cur,
                ):
                    if j_new not in visited:
                        visited.add(j_new)
                        # Push gen through to get a generator on the new curve
                        _, _, _, imgs = velu_isogeny(
                            pt, 3, a_cur, b_cur, P,
                            aux_points=[gen_cur],
                        )
                        new_gen = imgs[0]
                        if new_gen is not None:
                            from isogenies.curve import point_order
                            # The image has order dividing order_cur
                            # (it might be smaller if gen was in the kernel)
                            try:
                                new_order = point_order(
                                    new_gen, a_new, P, order_cur + 1,
                                )
                            except ValueError:
                                continue
                            next_queue.append(
                                (a_new, b_new, new_gen, new_order)
                            )
            queue = next_queue

        assert len(visited) >= 3, (
            f"BFS reached {len(visited)} j-invariants (expected >= 3)"
        )

    def test_2isogeny_preserves_j1728(self):
        """The 2-isogeny from E_0 using (0,0) maps j=1728 to j=1728.

        This is correct: j=1728 has extra automorphisms (the curve
        y^2 = x^3 + x admits the automorphism (x,y) -> (-x, iy)),
        and the degree-2 isogeny with kernel <(0,0)> produces an
        isomorphic curve.
        """
        T2 = ((0, 0), (0, 0))
        a_new, b_new, _, _ = velu_isogeny(T2, 2, A, B, P)
        j_source = _j_key(j_invariant(A, B, P))
        j_target = _j_key(j_invariant(a_new, b_new, P))
        assert j_source == j_target  # j=1728 is a fixed point
