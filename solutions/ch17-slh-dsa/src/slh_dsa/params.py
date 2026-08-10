"""FIPS 205 parameter sets for SLH-DSA.

Each parameter set is a frozen dataclass encoding the values from
FIPS 205 Table 1 (SHA2 instantiation) and Table 2 (SHAKE instantiation).
Derived quantities (ell_1, ell_2, ell, signature size) are computed in
``__post_init__`` and cached as frozen fields.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class SLHDSAParams:
    """SLH-DSA parameter set."""

    name: str
    n: int          # hash output length in bytes
    h: int          # total tree height
    d: int          # hypertree layers
    hp: int         # subtree height (h // d)
    a: int          # FORS tree height (t = 2^a)
    k: int          # number of FORS trees
    w: int          # Winternitz parameter
    hash_family: str  # "sha2" or "shake"

    # Derived WOTS+ parameters (set in __post_init__)
    lg_w: int = 0
    ell_1: int = 0
    ell_2: int = 0
    ell: int = 0

    def __post_init__(self) -> None:
        assert self.h == self.d * self.hp, (
            f"h ({self.h}) != d * hp ({self.d} * {self.hp})"
        )
        assert self.w in (4, 16, 256), f"unsupported w={self.w}"
        assert self.hash_family in ("sha2", "shake"), (
            f"unknown hash_family={self.hash_family!r}"
        )

        lg_w = int(math.log2(self.w))
        ell_1 = math.ceil(8 * self.n / lg_w)
        max_csum = ell_1 * (self.w - 1)
        ell_2 = math.ceil((math.floor(math.log2(max_csum)) + 1) / lg_w)
        ell = ell_1 + ell_2

        # Bypass frozen to set derived fields
        object.__setattr__(self, "lg_w", lg_w)
        object.__setattr__(self, "ell_1", ell_1)
        object.__setattr__(self, "ell_2", ell_2)
        object.__setattr__(self, "ell", ell)

    @property
    def t(self) -> int:
        """Number of leaves per FORS tree."""
        return 1 << self.a

    @property
    def md_len(self) -> int:
        """Message digest length in bytes for H_msg output (m in Table 2).

        Algorithm 19 lines 6 to 8 cut the digest into three fields, and
        each one is rounded up to a whole number of bytes on its own:
        ceil(k*a / 8) for md, ceil((h - h/d) / 8) for idx_tree, and
        ceil(h / 8d) for idx_leaf.  Summing the bit counts first and
        rounding once at the end is a different number wherever two of
        the three roundings would have contributed, which is 4 of the 6
        parameter sets.  A digest one byte short leaves idx_leaf reading
        past the end of the slice, so it silently becomes 0 and only the
        signatures whose true idx_leaf was already 0 still verify.
        """
        return ((self.k * self.a + 7) // 8
                + (self.h - self.hp + 7) // 8
                + (self.hp + 7) // 8)

    def sig_bytes(self) -> int:
        """Total SLH-DSA signature size in bytes."""
        fors = self.k * (1 + self.a) * self.n
        ht = self.d * (self.ell * self.n + self.hp * self.n)
        return self.n + fors + ht

    def pk_bytes(self) -> int:
        """Public key size: PK.seed || PK.root."""
        return 2 * self.n

    def sk_bytes(self) -> int:
        """Secret key size: SK.seed || SK.prf || PK.seed || PK.root."""
        return 4 * self.n


# -- FIPS 205 Table 1: SHA2 parameter sets --------------------------------

SLH_DSA_SHA2_128s = SLHDSAParams(
    name="SLH-DSA-SHA2-128s", n=16, h=63, d=7, hp=9,
    a=12, k=14, w=16, hash_family="sha2",
)
SLH_DSA_SHA2_128f = SLHDSAParams(
    name="SLH-DSA-SHA2-128f", n=16, h=66, d=22, hp=3,
    a=6, k=33, w=16, hash_family="sha2",
)
SLH_DSA_SHA2_192s = SLHDSAParams(
    name="SLH-DSA-SHA2-192s", n=24, h=63, d=7, hp=9,
    a=14, k=17, w=16, hash_family="sha2",
)
SLH_DSA_SHA2_192f = SLHDSAParams(
    name="SLH-DSA-SHA2-192f", n=24, h=66, d=22, hp=3,
    a=8, k=33, w=16, hash_family="sha2",
)
SLH_DSA_SHA2_256s = SLHDSAParams(
    name="SLH-DSA-SHA2-256s", n=32, h=64, d=8, hp=8,
    a=14, k=22, w=16, hash_family="sha2",
)
SLH_DSA_SHA2_256f = SLHDSAParams(
    name="SLH-DSA-SHA2-256f", n=32, h=68, d=17, hp=4,
    a=9, k=35, w=16, hash_family="sha2",
)


# -- FIPS 205 Table 2: SHAKE parameter sets --------------------------------

SLH_DSA_SHAKE_128s = SLHDSAParams(
    name="SLH-DSA-SHAKE-128s", n=16, h=63, d=7, hp=9,
    a=12, k=14, w=16, hash_family="shake",
)
SLH_DSA_SHAKE_128f = SLHDSAParams(
    name="SLH-DSA-SHAKE-128f", n=16, h=66, d=22, hp=3,
    a=6, k=33, w=16, hash_family="shake",
)
SLH_DSA_SHAKE_192s = SLHDSAParams(
    name="SLH-DSA-SHAKE-192s", n=24, h=63, d=7, hp=9,
    a=14, k=17, w=16, hash_family="shake",
)
SLH_DSA_SHAKE_192f = SLHDSAParams(
    name="SLH-DSA-SHAKE-192f", n=24, h=66, d=22, hp=3,
    a=8, k=33, w=16, hash_family="shake",
)
SLH_DSA_SHAKE_256s = SLHDSAParams(
    name="SLH-DSA-SHAKE-256s", n=32, h=64, d=8, hp=8,
    a=14, k=22, w=16, hash_family="shake",
)
SLH_DSA_SHAKE_256f = SLHDSAParams(
    name="SLH-DSA-SHAKE-256f", n=32, h=68, d=17, hp=4,
    a=9, k=35, w=16, hash_family="shake",
)


# -- Teaching parameter set (not FIPS 205) ---------------------------------

TOY = SLHDSAParams(
    name="TOY", n=16, h=9, d=3, hp=3,
    a=3, k=3, w=16, hash_family="sha2",
)
