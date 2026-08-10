"""FIPS 205's six SHA-2 parameter sets, and the WOTS+ chain count they imply.

Every number in Chapter 18 is a function of six integers per parameter set:
the security parameter `n` in bytes, the total hypertree height `h`, the layer
count `d`, the FORS tree height `a`, the FORS tree count `k`, and the Winternitz
parameter `w`. Those six are read from FIPS 205 Table 2 and are frozen here as
data rather than recomputed, because they are the output of NIST's parameter
search and not derivable from anything the book states.

Everything else *is* derivable, and is exposed as a property rather than stored:
`t = 2**a` leaves per FORS tree, `h_prime = h // d` as the per-layer XMSS height,
and `ell` as the WOTS+ chain count. `tests/ch18/test_params.py` checks each
derived value against the corresponding Table 2 column, which is what stops a
transcription error in the six frozen integers from propagating silently into
every other module.

The SHAKE parameter sets carry the same six integers as their SHA-2 namesakes
and differ only in the hash instantiation (FIPS 205 Section 11), which this
package never evaluates. They are omitted rather than duplicated: adding them
would double the table without changing a single computed result.

Standard library only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


def wots_ell_parts(n_bytes: int, w: int) -> tuple[int, int]:
    """The WOTS+ chain count split into `(ell_1, ell_2)`.

    `ell_1` chains carry the message digits: `8 * n_bytes` bits read `lg_w` at a
    time. `ell_2` chains carry the checksum, which is at most `ell_1 * (w - 1)`
    and so needs `floor(log2(max_checksum)) + 1` bits, again read `lg_w` at a
    time. The checksum is what makes WOTS+ a signature rather than a set of
    independent chains: lowering any message digit raises the checksum, so a
    forger who walks one chain forward is forced to walk another backward
    (Chapter 15).

    The split matters here because only `ell_1` scales with `n`. Chapter 18's
    exercise on custom parameters asks for both parts separately, and the
    package keeps them separate for the same reason.
    """
    lg_w = int(math.log2(w))
    ell_1 = math.ceil(8 * n_bytes / lg_w)
    max_checksum = ell_1 * (w - 1)
    ell_2 = math.ceil((math.floor(math.log2(max_checksum)) + 1) / lg_w)
    return ell_1, ell_2


def wots_ell(n_bytes: int, w: int) -> int:
    """Total WOTS+ chains, `ell = ell_1 + ell_2`. The chapter prints this one."""
    ell_1, ell_2 = wots_ell_parts(n_bytes, w)
    return ell_1 + ell_2


@dataclass(frozen=True)
class ParameterSet:
    """One row of FIPS 205 Table 2, restricted to the columns Chapter 18 uses."""

    name: str
    n_bytes: int
    h: int
    d: int
    a: int
    k: int
    w: int = 16

    @property
    def n_bits(self) -> int:
        """Hash output length in bits.

        FIPS 205 writes `n` in bytes; the security exponents in this chapter are
        in bits. Conflating the two is the easiest way to be off by a factor of
        eight, so the two names never share a variable.
        """
        return 8 * self.n_bytes

    @property
    def t(self) -> int:
        """Leaves per FORS tree, `2**a`."""
        return 2**self.a

    @property
    def h_prime(self) -> int:
        """Height of one XMSS layer, `h // d`.

        FIPS 205 tabulates `h'` separately and requires `h = d * h'` exactly.
        `test_params.py` checks the division is exact rather than trusting it.
        """
        return self.h // self.d

    @property
    def ell(self) -> int:
        """WOTS+ chains per signature."""
        return wots_ell(self.n_bytes, self.w)

    @property
    def category(self) -> int:
        """NIST security category: 1, 3, or 5 at `n_bits` 128, 192, or 256."""
        return {128: 1, 192: 3, 256: 5}[self.n_bits]


#: FIPS 205 Table 2, SHA-2 rows. Order is the standard's own.
SHA2_PARAMETER_SETS: tuple[ParameterSet, ...] = (
    ParameterSet("SLH-DSA-SHA2-128s", n_bytes=16, h=63, d=7, a=12, k=14),
    ParameterSet("SLH-DSA-SHA2-128f", n_bytes=16, h=66, d=22, a=6, k=33),
    ParameterSet("SLH-DSA-SHA2-192s", n_bytes=24, h=63, d=7, a=14, k=17),
    ParameterSet("SLH-DSA-SHA2-192f", n_bytes=24, h=66, d=22, a=8, k=33),
    ParameterSet("SLH-DSA-SHA2-256s", n_bytes=32, h=64, d=8, a=14, k=22),
    ParameterSet("SLH-DSA-SHA2-256f", n_bytes=32, h=68, d=17, a=9, k=35),
)


def by_name(name: str) -> ParameterSet:
    """Look up a parameter set by its FIPS 205 name.

    Accepts the short form the chapter's tables use (`128s`) as well as the full
    standard name (`SLH-DSA-SHA2-128s`), because the chapter prints both.
    """
    for ps in SHA2_PARAMETER_SETS:
        if name in (ps.name, ps.name.rsplit("-", 1)[-1]):
            return ps
    raise KeyError(f"no SHA-2 parameter set named {name!r}")
