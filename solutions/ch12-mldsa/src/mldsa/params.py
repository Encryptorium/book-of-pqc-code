"""ML-DSA (FIPS 204) parameter sets.

The three standardized parameter sets ML-DSA-44, ML-DSA-65, and ML-DSA-87 share
the ring R_q = Z_q[X]/(X^256 + 1) with the prime q = 8380417 and the dropped-bit
count d = 13. Because q ≡ 1 (mod 2n), the ring splits completely and a full
256-point number-theoretic transform exists with primitive 512-th root of unity
ζ = 1753 (see ``ntt.py``).

The parameter *sets* differ in the module dimensions (k, l), the secret-key noise
bound η, the challenge weight τ, the mask/low-bit windows γ1 and γ2, the hint
budget ω, and the challenge-hash collision strength λ. Everything a reader needs
to size a buffer is a derived-length method here (``pk_len``, ``sk_len``,
``sig_len``, ``c_tilde_len``, and the packing bit widths), computed from those
primitives rather than hard-coded, so the arithmetic that produces FIPS 204
Table 2 is visible in code.

Following the pedagogical stance of the book, ``__post_init__`` validates with
bare ``assert`` and the dispatcher crashes loudly on an unknown set: this is toy
code that should fail obviously on bad input, not degrade quietly.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# --- Ring constants shared by every parameter set (FIPS 204 §4, Table 1). ---
ML_DSA_Q = 8380417          # prime modulus, 2^23 - 2^13 + 1
ML_DSA_N = 256              # ring degree; R_q = Z_q[X]/(X^256 + 1)
ML_DSA_D = 13              # number of low bits of t dropped by Power2Round
ML_DSA_ZETA = 1753          # primitive 512-th root of unity mod q


def bitlen(m: int) -> int:
    """FIPS 204 ``bitlen``: the number of bits needed to represent m (m >= 0)."""
    assert m >= 0, f"bitlen: m must be non-negative, got {m}"
    return m.bit_length()


class ParameterSet(Enum):
    ML_DSA_44 = "ML-DSA-44"
    ML_DSA_65 = "ML-DSA-65"
    ML_DSA_87 = "ML-DSA-87"


@dataclass(frozen=True)
class MLDSAParams:
    """A single ML-DSA parameter set.

    Fields are the free parameters from FIPS 204 Table 1; the ring constants
    (n, q, d, ζ) are shared and exposed as properties. Byte lengths and packing
    widths are methods so the length arithmetic stays visible.
    """

    name: str
    k: int              # rows of A / dimension of t, w, s2
    l: int              # columns of A / dimension of s1, y, z
    eta: int            # secret coefficient bound: s1, s2 in [-eta, eta]
    tau: int            # number of +-1 coefficients in the challenge c
    gamma_1: int        # mask coefficient range: y in (-gamma1, gamma1]
    gamma_2: int        # low-order rounding window (decompose)
    omega: int          # maximum number of 1s in the hint h
    lam: int            # challenge-hash collision strength in bits (128/192/256)
    nist_category: int  # target NIST security category

    def __post_init__(self) -> None:
        assert self.k in (4, 6, 8), f"MLDSAParams.k must be in (4, 6, 8), got {self.k}"
        assert self.l in (4, 5, 7), f"MLDSAParams.l must be in (4, 5, 7), got {self.l}"
        assert self.eta in (2, 4), f"MLDSAParams.eta must be 2 or 4, got {self.eta}"
        assert self.tau in (39, 49, 60), f"MLDSAParams.tau invalid: {self.tau}"
        assert self.gamma_1 in (1 << 17, 1 << 19), (
            f"MLDSAParams.gamma_1 must be 2^17 or 2^19, got {self.gamma_1}"
        )
        assert self.gamma_2 in ((ML_DSA_Q - 1) // 88, (ML_DSA_Q - 1) // 32), (
            f"MLDSAParams.gamma_2 invalid: {self.gamma_2}"
        )
        assert self.omega in (75, 80, 55), f"MLDSAParams.omega invalid: {self.omega}"
        assert self.lam in (128, 192, 256), f"MLDSAParams.lam invalid: {self.lam}"
        assert self.nist_category in (2, 3, 5), (
            f"MLDSAParams.nist_category invalid: {self.nist_category}"
        )

    # --- Shared ring constants, exposed per-instance for convenience. ---
    @property
    def n(self) -> int:
        return ML_DSA_N

    @property
    def q(self) -> int:
        return ML_DSA_Q

    @property
    def d(self) -> int:
        return ML_DSA_D

    @property
    def beta(self) -> int:
        """FIPS 204: beta = tau * eta, the max infinity-norm of c*s_i."""
        return self.tau * self.eta

    # --- Packing bit widths (FIPS 204 §7.1-7.2 encoders). ---
    def eta_bits(self) -> int:
        """Bits per coefficient for BitPack(s, eta, eta) = bitlen(2*eta)."""
        return bitlen(2 * self.eta)

    def t0_bits(self) -> int:
        """Bits per coefficient for BitPack(t0, 2^(d-1)-1, 2^(d-1)) = bitlen(2^d - 1) = d."""
        return bitlen((1 << self.d) - 1)

    def t1_bits(self) -> int:
        """Bits per coefficient for SimpleBitPack(t1, 2^(bitlen(q-1)-d) - 1)."""
        return bitlen(ML_DSA_Q - 1) - self.d  # 23 - 13 = 10

    def gamma1_bits(self) -> int:
        """Bits per coefficient for BitPack(z, gamma1-1, gamma1) = bitlen(2*gamma1 - 1)."""
        return bitlen(2 * self.gamma_1 - 1)  # 18 for 2^17, 20 for 2^19

    def w1_bits(self) -> int:
        """Bits per coefficient for w1Encode = bitlen((q-1)/(2*gamma2) - 1).

        6 bits for ML-DSA-44 (44 high-bit values), 4 bits for ML-DSA-65/87 (16).
        Getting this wrong silently corrupts c-tilde and every signature; it is a
        classic ML-DSA implementation bug, so it is a named helper with its own test.
        """
        return bitlen((ML_DSA_Q - 1) // (2 * self.gamma_2) - 1)

    # --- Byte lengths (FIPS 204 Table 2). ---
    def c_tilde_len(self) -> int:
        """Challenge-hash length in bytes = lambda/4."""
        return self.lam // 4

    def pk_len(self) -> int:
        """Public key: rho (32) || SimpleBitPack(t1) over k polynomials."""
        return 32 + 32 * self.t1_bits() * self.k

    def sk_len(self) -> int:
        """Secret key: rho(32) || K(32) || tr(64) || BitPack(s1) || BitPack(s2) || BitPack(t0)."""
        return (
            32 + 32 + 64
            + 32 * self.eta_bits() * (self.k + self.l)
            + 32 * self.t0_bits() * self.k
        )

    def sig_len(self) -> int:
        """Signature: c-tilde || BitPack(z) over l polys || HintBitPack (omega + k bytes)."""
        return self.c_tilde_len() + 32 * self.gamma1_bits() * self.l + self.omega + self.k


# --- The three standardized parameter sets (FIPS 204 Table 1). ---
_GAMMA2_44 = (ML_DSA_Q - 1) // 88   # 95232
_GAMMA2_65_87 = (ML_DSA_Q - 1) // 32  # 261888

ML_DSA_44 = MLDSAParams(
    name="ML-DSA-44", k=4, l=4, eta=2, tau=39, gamma_1=1 << 17,
    gamma_2=_GAMMA2_44, omega=80, lam=128, nist_category=2,
)
ML_DSA_65 = MLDSAParams(
    name="ML-DSA-65", k=6, l=5, eta=4, tau=49, gamma_1=1 << 19,
    gamma_2=_GAMMA2_65_87, omega=55, lam=192, nist_category=3,
)
ML_DSA_87 = MLDSAParams(
    name="ML-DSA-87", k=8, l=7, eta=2, tau=60, gamma_1=1 << 19,
    gamma_2=_GAMMA2_65_87, omega=75, lam=256, nist_category=5,
)


def params_for(which: ParameterSet) -> MLDSAParams:
    """Map a ``ParameterSet`` enum to its ``MLDSAParams`` instance."""
    if which is ParameterSet.ML_DSA_44:
        return ML_DSA_44
    if which is ParameterSet.ML_DSA_65:
        return ML_DSA_65
    if which is ParameterSet.ML_DSA_87:
        return ML_DSA_87
    raise AssertionError(f"unknown parameter set: {which!r}")
