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
        # EXERCISE: implement this function.
        #
        # Bits per coefficient for BitPack of s1 and s2, which store signed
        # values in [-eta, eta]. BitPack uses bitlen(a+b) bits with a = b =
        # eta, so this is bitlen(2*eta): 3 bits when eta = 2, 4 bits when
        # eta = 4.
        #
        # Reference: Chapter 12, 'A concrete ML-DSA-65 parameter and seed derivation' (FIPS 204 Section 7.1)
        #
        # Proved by:
        #   tests/ch12/test_mldsa_params.py
        #   tests/ch12/test_mldsa_encode.py
        raise NotImplementedError("exercise: MLDSAParams.eta_bits")

    def t0_bits(self) -> int:
        """Bits per coefficient for BitPack(t0, 2^(d-1)-1, 2^(d-1)) = bitlen(2^d - 1) = d."""
        # EXERCISE: implement this function.
        #
        # Bits per coefficient for BitPack of t0, whose centered range is
        # (-2^(d-1), 2^(d-1)]. BitPack stores b - w with a = 2^(d-1) - 1 and
        # b = 2^(d-1), so the width is bitlen(a+b) = bitlen(2^d - 1) = d =
        # 13.
        #
        # Reference: Chapter 12, 'A concrete ML-DSA-65 parameter and seed derivation' (FIPS 204 Section 7.1)
        #
        # Proved by:
        #   tests/ch12/test_mldsa_params.py
        #   tests/ch12/test_mldsa_encode.py
        raise NotImplementedError("exercise: MLDSAParams.t0_bits")

    def t1_bits(self) -> int:
        """Bits per coefficient for SimpleBitPack(t1, 2^(bitlen(q-1)-d) - 1)."""
        # EXERCISE: implement this function.
        #
        # Bits per coefficient for SimpleBitPack of t1, the high part of the
        # public key after Power2Round drops the low d bits. Each
        # coefficient of t is bitlen(q-1) = 23 bits; dropping d = 13 leaves
        # 23 - 13 = 10 bits.
        #
        # Reference: Chapter 12, 'A concrete ML-DSA-65 parameter and seed derivation' (FIPS 204 Section 7.1)
        #
        # Proved by:
        #   tests/ch12/test_mldsa_params.py
        #   tests/ch12/test_mldsa_encode.py
        raise NotImplementedError("exercise: MLDSAParams.t1_bits")

    def gamma1_bits(self) -> int:
        """Bits per coefficient for BitPack(z, gamma1-1, gamma1) = bitlen(2*gamma1 - 1)."""
        # EXERCISE: implement this function.
        #
        # Bits per coefficient for BitPack of the response z, whose
        # coefficients lie in (-gamma1, gamma1]. BitPack uses bitlen(a+b)
        # with a = gamma1 - 1 and b = gamma1, so this is bitlen(2*gamma1 -
        # 1): 18 bits for gamma1 = 2^17, 20 bits for gamma1 = 2^19.
        #
        # Reference: Chapter 12, 'A concrete ML-DSA-65 parameter and seed derivation' (FIPS 204 Section 7.1)
        #
        # Proved by:
        #   tests/ch12/test_mldsa_params.py
        #   tests/ch12/test_mldsa_encode.py
        raise NotImplementedError("exercise: MLDSAParams.gamma1_bits")

    def w1_bits(self) -> int:
        """Bits per coefficient for w1Encode = bitlen((q-1)/(2*gamma2) - 1).

        6 bits for ML-DSA-44 (44 high-bit values), 4 bits for ML-DSA-65/87 (16).
        Getting this wrong silently corrupts c-tilde and every signature; it is a
        classic ML-DSA implementation bug, so it is a named helper with its own test.
        """
        # EXERCISE: implement this function.
        #
        # Bits per coefficient for SimpleBitPack of w1 inside w1Encode. Each
        # high value is one of (q-1)/(2*gamma2) possibilities, so the width
        # is bitlen((q-1)/(2*gamma2) - 1): 6 bits for ML-DSA-44 (44 values),
        # 4 bits for ML-DSA-65 and ML-DSA-87 (16 values). Getting this wrong
        # silently corrupts c-tilde.
        #
        # Reference: Chapter 12, 'A concrete ML-DSA-65 parameter and seed derivation' (FIPS 204 Section 7.1)
        #
        # Proved by:
        #   tests/ch12/test_mldsa_params.py
        #   tests/ch12/test_mldsa_encode.py
        raise NotImplementedError("exercise: MLDSAParams.w1_bits")

    # --- Byte lengths (FIPS 204 Table 2). ---
    def c_tilde_len(self) -> int:
        """Challenge-hash length in bytes = lambda/4."""
        # EXERCISE: implement this function.
        #
        # The challenge-hash length in bytes is lambda/4, where lambda is
        # the collision strength in bits: 32, 48, and 64 bytes for lambda =
        # 128, 192, 256.
        #
        # Reference: Chapter 12, 'A concrete ML-DSA-65 parameter and seed derivation' (FIPS 204 Table 2)
        #
        # Proved by:
        #   tests/ch12/test_mldsa_params.py
        #   tests/ch12/test_vectors.py
        raise NotImplementedError("exercise: MLDSAParams.c_tilde_len")

    def pk_len(self) -> int:
        """Public key: rho (32) || SimpleBitPack(t1) over k polynomials."""
        # EXERCISE: implement this function.
        #
        # The public key is rho (32 bytes) followed by SimpleBitPack of t1
        # over k polynomials at t1_bits bits each: 32 + 32 * t1_bits() * k.
        # That is 1312, 1952, and 2592 bytes at (k, t1_bits) = (4, 10), (6,
        # 10), (8, 10).
        #
        # Reference: Chapter 12, 'A concrete ML-DSA-65 parameter and seed derivation' (FIPS 204 Table 2)
        #
        # Proved by:
        #   tests/ch12/test_mldsa_params.py
        #   tests/ch12/test_vectors.py
        raise NotImplementedError("exercise: MLDSAParams.pk_len")

    def sk_len(self) -> int:
        """Secret key: rho(32) || K(32) || tr(64) || BitPack(s1) || BitPack(s2) || BitPack(t0)."""
        # EXERCISE: implement this function.
        #
        # The secret key is rho (32) || K (32) || tr (64) || BitPack(s1) ||
        # BitPack(s2) || BitPack(t0). That is 128 + 32 * eta_bits() * (k +
        # l) for the two secret vectors plus 32 * t0_bits() * k for t0. It
        # comes to 2560, 4032, and 4896 bytes.
        #
        # Reference: Chapter 12, 'A concrete ML-DSA-65 parameter and seed derivation' (FIPS 204 Table 2)
        #
        # Proved by:
        #   tests/ch12/test_mldsa_params.py
        #   tests/ch12/test_vectors.py
        raise NotImplementedError("exercise: MLDSAParams.sk_len")

    def sig_len(self) -> int:
        """Signature: c-tilde || BitPack(z) over l polys || HintBitPack (omega + k bytes)."""
        # EXERCISE: implement this function.
        #
        # The signature is c-tilde || BitPack(z) over l polynomials ||
        # HintBitPack (omega + k bytes): c_tilde_len() + 32 * gamma1_bits()
        # * l + omega + k. It comes to 2420, 3309, and 4627 bytes.
        #
        # Reference: Chapter 12, 'A concrete ML-DSA-65 parameter and seed derivation' (FIPS 204 Table 2)
        #
        # Proved by:
        #   tests/ch12/test_mldsa_params.py
        #   tests/ch12/test_vectors.py
        raise NotImplementedError("exercise: MLDSAParams.sig_len")


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
