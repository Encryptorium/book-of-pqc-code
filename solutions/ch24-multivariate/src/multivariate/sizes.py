"""Key-size and attack-cost arithmetic for the multivariate candidates.

Two things live here. The first is the arithmetic behind the public-key sizes
Chapter 24 quotes: a UOV public key stores one coefficient per degree-2
monomial for each of m quadratic forms, and at GF(16) two coefficients pack
into a byte. The second is the Kipnis-Shamir cost model, whose exponent is what
forces the unbalanced choice n > 2m.

Every figure in ``ROUND2_SIZES`` is read from the round-2 submission package of
the scheme named, and ``tests/ch24/test_sizes.py`` checks the derived
quantities against it. The sizes are round-2 figures and may be revised.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


def upper_triangular_count(n: int) -> int:
    """Number of degree-2 monomials x_i x_j with i <= j in n variables.

    The n diagonal entries plus the n(n-1)/2 strictly upper-triangular ones,
    which is n(n+1)/2. This is the storage a homogeneous quadratic form needs
    when it is kept in upper-triangular rather than symmetric form.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    return n * (n + 1) // 2


def uov_public_key_bytes(n: int, m: int, elements_per_byte: int = 2) -> int:
    """Size in bytes of an expanded UOV public key.

    ``m`` quadratic forms, each ``upper_triangular_count(n)`` field elements,
    packed ``elements_per_byte`` to a byte. GF(16) elements are nibbles, so the
    default of 2 is the uov-Is case; GF(256) elements are whole bytes, so
    uov-Ip passes ``elements_per_byte=1``.

    This models the expanded key. UOV also ships public-key-compressed
    versions, whose key is a 16-byte seed plus only the oil-oil part of each
    form, and those are much smaller; see ``ROUND2_SIZES``.
    """
    if elements_per_byte < 1:
        raise ValueError("elements_per_byte must be at least 1")
    return m * upper_triangular_count(n) // elements_per_byte


def kipnis_shamir_log2_cost(q: int, n: int, m: int) -> float:
    """Base-2 log of the Kipnis-Shamir key-recovery cost, literature form.

    The attack searches for a single vector in the oil subspace, and the
    expected number of candidates it must try is q^(n - 2m). The literature
    cost quoted in the UOV round-2 specification is O(q^(n-2m) * n^4), so this
    returns ``(n - 2m) * log2(q) + 4 * log2(n)``.

    For balanced parameters (n = 2m) the exponent vanishes and the attack runs
    in polynomial time, which is exactly the Kipnis-Shamir 1998 break of the
    original Oil-Vinegar scheme.

    The round-2 specification refines the estimate to q^(n-2m) * n^2.8 *
    (2r^2 + r) and tabulates 154 bits for uov-Is, a few bits below what this
    function returns. Use it for the shape of the exponent, not as a security
    claim.
    """
    if n < 2 * m:
        raise ValueError("UOV requires n >= 2m")
    return (n - 2 * m) * math.log2(q) + 4 * math.log2(n)


def kipnis_shamir_search_exponent(q: int, n: int, m: int) -> float:
    """Base-2 log of q^(n - 2m) alone, the dominant factor above."""
    if n < 2 * m:
        raise ValueError("UOV requires n >= 2m")
    return (n - 2 * m) * math.log2(q)


@dataclass(frozen=True)
class SchemeSizes:
    """Public-key and signature sizes for one parameter set, in bytes."""

    name: str
    nist_level: int
    public_key: int
    signature: int
    source: str


ROUND2_SIZES: dict[str, SchemeSizes] = {
    "uov-Is": SchemeSizes(
        name="uov-Is",
        nist_level=1,
        public_key=412_160,
        signature=96,
        source="UOV round-2 specification v2.0, Table 1 (expanded public key)",
    ),
    "uov-Is-pkc": SchemeSizes(
        name="uov-Is-pkc",
        nist_level=1,
        public_key=66_576,
        signature=96,
        source="UOV round-2 specification v2.0, Table 1 (compact public key)",
    ),
    "uov-Ip": SchemeSizes(
        name="uov-Ip",
        nist_level=1,
        public_key=278_432,
        signature=128,
        source="UOV round-2 specification v2.0, Table 1 (expanded public key)",
    ),
    "MAYO1": SchemeSizes(
        name="MAYO1",
        nist_level=1,
        public_key=1_420,
        signature=454,
        source="MAYO round-2 specification, Table 2.1",
    ),
    "MAYO2": SchemeSizes(
        name="MAYO2",
        nist_level=1,
        public_key=4_912,
        signature=186,
        source="MAYO round-2 specification, Table 2.1",
    ),
    "SNOVA-(24,5,16,4)": SchemeSizes(
        name="SNOVA-(24,5,16,4)",
        nist_level=1,
        public_key=1_016,
        signature=248,
        source="SNOVA round-2 specification, Table 6",
    ),
    "SNOVA-(37,17,16,2)": SchemeSizes(
        name="SNOVA-(37,17,16,2)",
        nist_level=1,
        public_key=9_842,
        signature=124,
        source="SNOVA round-2 specification, Table 6",
    ),
}
