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
    assert composite in COMPOSITES, f"unknown composite: {composite!r}"
    a, b = COMPOSITES[composite]
    sig_a = PRIMITIVE_SIZES[a]["sig_bytes"]
    sig_b = PRIMITIVE_SIZES[b]["sig_bytes"]
    pk_a = PRIMITIVE_SIZES[a]["pk_bytes"]
    pk_b = PRIMITIVE_SIZES[b]["pk_bytes"]
    return {
        "composite": composite,
        "component_a": a,
        "component_b": b,
        "component_a_sig_bytes": sig_a,
        "component_b_sig_bytes": sig_b,
        "component_a_pk_bytes": pk_a,
        "component_b_pk_bytes": pk_b,
        "composite_sig_bytes": sig_a + sig_b,
        "composite_pk_bytes": pk_a + pk_b,
        "sig_overhead_vs_strongest": (sig_a + sig_b) - max(sig_a, sig_b),
        "pk_overhead_vs_strongest": (pk_a + pk_b) - max(pk_a, pk_b),
    }


def overhead_ratio(composite: str) -> float:
    """Composite signature size as a multiple of the larger component.

    A value of 1.02 means the composite costs 2% more bytes than the
    larger component alone. A value of 2.0 means the composite costs
    twice the larger component.
    """
    assert composite in COMPOSITES, f"unknown composite: {composite!r}"
    info = overhead(composite)
    larger = max(info["component_a_sig_bytes"], info["component_b_sig_bytes"])
    assert larger > 0, "component signature size must be positive"
    return info["composite_sig_bytes"] / larger
