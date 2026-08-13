"""Bit-margin arithmetic for the Chapter 35 case studies.

The chapter prints four of these routines as listings. Two more are here
because the chapter states them in prose but never prints them: the three
decoding radii as one function, and the composed FRI budget with its three
terms exposed rather than summed away.
"""

import math
from dataclasses import dataclass

__all__ = [
    "REGIMES",
    "MarginTerms",
    "bit_margin_pairing",
    "composed_margin",
    "decoding_radius",
    "dfms20_exact_cbits",
    "dfms20_required_cbits",
    "query_miss_bits",
    "shor_pairing_margin",
    "stark_classical_margin",
]

# The three proximity radii Ch 34 Section 5.1 names, in increasing order.
# Only "johnson" carries a proven proximity gap (BCIKS Theorem 1.2); the
# capacity radius rests on conjectures Crites and Stewart disproved in 2025.
REGIMES = ("unique", "johnson", "capacity")


@dataclass(frozen=True)
class MarginTerms:
    """The composed FRI soundness budget with its terms kept apart.

    ``bad_beta``, ``per_round`` and ``consistency`` are base-2 logarithms of
    probabilities, so all three are negative and the least negative one is
    the term that dominates the sum.
    """

    bad_beta: float
    per_round: float
    consistency: float
    grinding: int
    total: float

    @property
    def dominant(self) -> str:
        """Name the term contributing most of the composed probability."""
        pairs = (
            ("bad_beta", self.bad_beta),
            ("per_round", self.per_round),
            ("consistency", self.consistency),
        )
        return max(pairs, key=lambda pair: pair[1])[0]


def bit_margin_pairing(field_bit: int) -> int:
    """Post-quantum bit margin of a pairing-based L2, which is zero."""
    if field_bit <= 0:
        raise ValueError("field_bit must be positive")
    return 0


def shor_pairing_margin(curve_bits: int) -> int:
    """The same result named for a concrete deployed curve."""
    if curve_bits <= 0:
        raise ValueError("curve_bits must be positive")
    return 0


def decoding_radius(rho: float, regime: str) -> float:
    """Return the relative decoding radius ``delta_0`` for a code rate.

    ``unique`` is the unique-decoding radius ``(1 - rho) / 2``, ``johnson``
    the Johnson / Guruswami-Sudan list-decoding radius ``1 - sqrt(rho)``,
    and ``capacity`` the capacity bound ``1 - rho``.
    """
    if not 0.0 < rho < 1.0:
        raise ValueError("rho must lie strictly between 0 and 1")
    if regime not in REGIMES:
        raise ValueError(f"unknown regime: {regime!r}")
    if regime == "unique":
        return (1.0 - rho) / 2.0
    if regime == "johnson":
        return 1.0 - math.sqrt(rho)
    return 1.0 - rho


def composed_margin(field_bits: int, L: int, N: int, mu: int, r_FRI: int,
                    grinding: int, regime: str = "johnson") -> MarginTerms:
    """Compose the FRI soundness budget, keeping the three terms apart.

    ``stark_classical_margin`` is this routine's ``total`` at the Johnson
    radius; the chapter prints that form, and the terms behind it are what
    the prose discusses when it asks which one dominates.
    """
    if min(field_bits, L, N, mu, r_FRI) <= 0:
        raise ValueError("field_bits, L, N, mu, r_FRI must be positive")
    if grinding < 0:
        raise ValueError("grinding must be non-negative")
    if L >= N:
        raise ValueError("L must be less than N")
    delta_0 = decoding_radius(L / N, regime)
    bad_beta = math.log2(r_FRI * (N + 1)) - field_bits
    per_round = mu * math.log2(1.0 - delta_0)
    consistency = mu * math.log2((L - 1) / N)
    composed_prob = (2.0 ** bad_beta + 2.0 ** per_round + 2.0 ** consistency)
    total = round(-math.log2(composed_prob) + grinding, 1)
    return MarginTerms(bad_beta=bad_beta, per_round=per_round,
                       consistency=consistency, grinding=grinding, total=total)


def stark_classical_margin(field_bits: int, L: int, N: int, mu: int,
                           r_FRI: int, grinding: int) -> float:
    """The listing form: the composed margin at the Johnson radius."""
    return composed_margin(field_bits, L, N, mu, r_FRI, grinding,
                           regime="johnson").total


def dfms20_required_cbits(k_target: int, q_bits: int, r_FS: int) -> int:
    """Approximate DFMS20 per-round challenge width, ``2 q + ceil(k / r)``."""
    if k_target <= 0 or r_FS <= 0 or q_bits < 0:
        raise ValueError("k_target, r_FS must be positive; q_bits non-negative")
    return 2 * q_bits + math.ceil(k_target / r_FS)


def dfms20_exact_cbits(k_target: int, q_bits: int, r_FS: int) -> int:
    """Exact DFMS20 per-round width, ``2 log2(2q + 1) + k / r``.

    The approximation drops the ``log2(2q + 1)`` correction, which is a
    shade over ``q_bits + 1``. The strict inequality is what forces the
    round up, so an exact bound landing on an integer still needs the next
    width above it.
    """
    if k_target <= 0 or r_FS <= 0 or q_bits < 0:
        raise ValueError("k_target, r_FS must be positive; q_bits non-negative")
    exact = 2.0 * math.log2(2 * (2 ** q_bits) + 1) + k_target / r_FS
    width = math.ceil(exact)
    return width + 1 if width == exact else width


def query_miss_bits(n_queries: int, pow_bits: int, log_blowup: int,
                    regime: str) -> float:
    """Query-miss margin alone, for a published (queries, grinding, rate) set."""
    if min(n_queries, log_blowup) <= 0 or pow_bits < 0:
        raise ValueError("n_queries, log_blowup positive; pow_bits non-negative")
    delta_0 = decoding_radius(2.0 ** (-log_blowup), regime)
    return round(-n_queries * math.log2(1.0 - delta_0) + pow_bits, 1)
