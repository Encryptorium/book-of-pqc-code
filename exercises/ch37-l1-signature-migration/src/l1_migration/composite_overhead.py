"""Composite-signature byte arithmetic.

A composite signature carries one classical signature alongside one
post-quantum signature in a single transaction (Ch 27). The composite
is EUF-CMA secure if either component is, which buys defense in depth
during the cutover window at the cost of additional signature bytes
and verification work.

This module reports per-composite signature and public-key sizes and
the overhead vs each component primitive in isolation. The chapter
uses ``Ed25519+ML-DSA-65`` as the canonical cutover-window composite;
``Ed25519+SLH-DSA-128s`` is included as a hash-based alternative for
exercise purposes.
"""

from typing import Dict, Tuple, TypedDict


class PrimitiveSizes(TypedDict):
    sig_bytes: int
    pk_bytes: int


PRIMITIVE_SIZES: Dict[str, PrimitiveSizes] = {
    "Ed25519": {"sig_bytes": 64, "pk_bytes": 32},
    "ML-DSA-65": {"sig_bytes": 3309, "pk_bytes": 1952},
    "SLH-DSA-128s": {"sig_bytes": 7856, "pk_bytes": 32},
}

COMPOSITES: Dict[str, Tuple[str, str]] = {
    "Ed25519+ML-DSA-65": ("Ed25519", "ML-DSA-65"),
    "Ed25519+SLH-DSA-128s": ("Ed25519", "SLH-DSA-128s"),
}


def overhead(composite: str) -> dict:
    """Composite vs component overhead in bytes.

    Returns a dict reporting:

    - ``composite_sig_bytes`` and ``composite_pk_bytes``: the totals.
    - ``component_a`` / ``component_b``: the primitive names.
    - ``component_a_sig_bytes`` / ``component_b_sig_bytes``: each
      component in isolation.
    - ``sig_overhead_vs_strongest``: composite total minus the larger
      component signature. This is the marginal byte cost of carrying
      the second signature.
    - ``pk_overhead_vs_strongest``: composite public-key total minus
      the larger component public key.
    """
    # EXERCISE: implement this function.
    #
    # Read the composite's two component names out of COMPOSITES and each
    # component's sizes out of PRIMITIVE_SIZES. The composite totals are the
    # component sums. Both overhead fields subtract the larger component
    # from the composite total, which is the marginal cost of carrying the
    # second signature; because the classical component is the smaller one
    # in both composites here, those answers come out as Ed25519's 64
    # signature bytes and 32 public-key bytes.
    #
    # Reference: Chapter 37, 'Cutover with a composite signature'
    #
    # Proved by:
    #   tests/ch37/test_composite_overhead.py
    raise NotImplementedError("exercise: overhead")


def overhead_ratio(composite: str) -> float:
    """Composite signature size as a multiple of the larger component.

    A value of 1.02 means the composite costs 2% more bytes than the
    larger component alone. A value of 2.0 means the composite costs
    twice the larger component.
    """
    # EXERCISE: implement this function.
    #
    # Composite signature bytes divided by the larger of the two component
    # signature sizes, both read out of the dict overhead already built
    # rather than recomputed. Assert the larger component is positive before
    # dividing. The ratio sits near 1 exactly when the classical component
    # is small against the post-quantum one: 3373 over 3309 is about 1.019,
    # 7920 over 7856 about 1.008.
    #
    # Reference: Chapter 37, 'Cutover with a composite signature'
    #
    # Proved by:
    #   tests/ch37/test_composite_overhead.py
    raise NotImplementedError("exercise: overhead_ratio")
