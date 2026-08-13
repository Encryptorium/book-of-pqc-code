"""Chapter 35: the case-study apparatus for deployed zero-knowledge systems."""

from .grid import L2_COLORS, L4_COLORS, classify, dominant_color
from .margins import (
    MarginTerms,
    bit_margin_pairing,
    composed_margin,
    decoding_radius,
    dfms20_exact_cbits,
    dfms20_required_cbits,
    query_miss_bits,
    shor_pairing_margin,
    stark_classical_margin,
)
from .systems import SYSTEMS, STWO_DEFAULTS, names, posture

__all__ = [
    "L2_COLORS", "L4_COLORS", "MarginTerms", "SYSTEMS", "STWO_DEFAULTS",
    "bit_margin_pairing", "classify", "composed_margin", "decoding_radius",
    "dfms20_exact_cbits", "dfms20_required_cbits", "dominant_color", "names",
    "posture", "query_miss_bits", "shor_pairing_margin",
    "stark_classical_margin",
]
