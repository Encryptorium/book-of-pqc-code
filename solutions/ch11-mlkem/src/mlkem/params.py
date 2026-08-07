"""ML-KEM parameter sets per FIPS 203 §8.

FIPS 203 standardizes three parameter sets that share the polynomial
ring $R_q = \\mathbb{Z}_{3329}[x]/(x^{256}+1)$ and differ only in the
module rank $k$, the noise parameters $\\eta_1$ and $\\eta_2$, and the
ciphertext compression widths $d_u$ and $d_v$:

========  ==  =======  =======  ====  ====  =============
Variant    k    eta_1    eta_2   d_u   d_v   NIST category
========  ==  =======  =======  ====  ====  =============
ML-KEM-512  2       3        2    10     4              1
ML-KEM-768  3       2        2    10     4              3
ML-KEM-1024 4       2        2    11     5              5
========  ==  =======  =======  ====  ====  =============

The ring parameters ``n = 256`` and ``q = 3329`` are shared by all
three instances. This file only stores the per-parameter-set numbers;
the derived byte-length constants (``ek`` length, ``dk`` length,
ciphertext length, shared-secret length) are computed as dataclass
methods rather than hard-coded so the derivation is visible.

No error handling on degenerate input beyond structural asserts: the
dataclass crashes loudly on bad values, which is the correct
behaviour for a pedagogical package.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# The ring is fixed across all three parameter sets (FIPS 203 §8).
ML_KEM_N: int = 256
ML_KEM_Q: int = 3329


class ParameterSet(Enum):
    """The three ML-KEM parameter sets standardized in FIPS 203 §8."""

    ML_KEM_512 = "ML-KEM-512"
    ML_KEM_768 = "ML-KEM-768"
    ML_KEM_1024 = "ML-KEM-1024"


@dataclass(frozen=True)
class MLKEMParams:
    """Parameters for one ML-KEM parameter set (FIPS 203 §8).

    Fields:
        name: the human-readable name from the standard.
        k: module rank (number of ring elements in the secret).
        eta_1: noise parameter for secret key and decryption randomness.
        eta_2: noise parameter for encryption randomness.
        d_u: compression width for the ciphertext u component.
        d_v: compression width for the ciphertext v component.
        nist_category: claimed NIST security category.
    """

    name: str
    k: int
    eta_1: int
    eta_2: int
    d_u: int
    d_v: int
    nist_category: int

    def __post_init__(self) -> None:
        assert self.k in (2, 3, 4), (
            f"MLKEMParams.k must be in (2, 3, 4), got {self.k}"
        )
        assert self.eta_1 in (2, 3), (
            f"MLKEMParams.eta_1 must be in (2, 3), got {self.eta_1}"
        )
        assert self.eta_2 == 2, (
            f"MLKEMParams.eta_2 must equal 2 in FIPS 203, got {self.eta_2}"
        )
        # FIPS 203 Table 2 approves only d_u = 10 and d_u = 11. The range
        # here is wider so Chapter 11's Exercise 2 can build a toy set with
        # a deliberately smaller noise budget; nothing below d_u = 10 is a
        # standardized parameter set.
        assert 1 <= self.d_u <= 11, (
            f"MLKEMParams.d_u must be in [1, 11], got {self.d_u}"
        )
        assert self.d_v in (4, 5), (
            f"MLKEMParams.d_v must be in (4, 5), got {self.d_v}"
        )
        assert self.nist_category in (1, 3, 5), (
            f"MLKEMParams.nist_category must be 1, 3, or 5, "
            f"got {self.nist_category}"
        )

    @property
    def n(self) -> int:
        """The shared ring degree n = 256."""
        return ML_KEM_N

    @property
    def q(self) -> int:
        """The shared modulus q = 3329."""
        return ML_KEM_Q

    def byte_encode_poly_12_len(self) -> int:
        """Byte length of ByteEncode_12 on a single polynomial in R_q.

        FIPS 203 §4.2.1: twelve bits per coefficient, 256 coefficients,
        packed into 384 bytes per polynomial.
        """
        return 384

    def ek_len(self) -> int:
        """Byte length of the K-PKE and ML-KEM encryption key ek.

        FIPS 203 §5.1 and §6.1: ek is ByteEncode_12(t_hat) for t in R_q^k
        followed by the 32-byte seed rho, so 384 * k + 32 bytes.
        """
        return 384 * self.k + 32

    def dk_pke_len(self) -> int:
        """Byte length of the K-PKE decryption key.

        FIPS 203 §5.1: dk_PKE is ByteEncode_12(s_hat) for s in R_q^k,
        so 384 * k bytes.
        """
        return 384 * self.k

    def dk_len(self) -> int:
        """Byte length of the ML-KEM decryption key dk.

        FIPS 203 §6.1: dk is dk_PKE || ek || H(ek) || z, where H(ek) is
        32 bytes and z is the 32-byte implicit-rejection seed.
        """
        return self.dk_pke_len() + self.ek_len() + 32 + 32

    def ct_len(self) -> int:
        """Byte length of an ML-KEM ciphertext c.

        FIPS 203 §5.2: c = ByteEncode_{d_u}(Compress_{d_u}(u)) ||
        ByteEncode_{d_v}(Compress_{d_v}(v)), where u in R_q^k and
        v in R_q. Each compressed polynomial in R_q contributes
        32 * d bytes because 256 * d bits = 32 * d bytes.
        """
        return 32 * (self.d_u * self.k + self.d_v)

    def shared_secret_len(self) -> int:
        """Byte length of an ML-KEM shared secret K, always 32 bytes."""
        return 32


ML_KEM_512 = MLKEMParams(
    name="ML-KEM-512",
    k=2,
    eta_1=3,
    eta_2=2,
    d_u=10,
    d_v=4,
    nist_category=1,
)

ML_KEM_768 = MLKEMParams(
    name="ML-KEM-768",
    k=3,
    eta_1=2,
    eta_2=2,
    d_u=10,
    d_v=4,
    nist_category=3,
)

ML_KEM_1024 = MLKEMParams(
    name="ML-KEM-1024",
    k=4,
    eta_1=2,
    eta_2=2,
    d_u=11,
    d_v=5,
    nist_category=5,
)


def params_for(which: ParameterSet) -> MLKEMParams:
    """Return the MLKEMParams for a given ParameterSet enum value."""
    if which is ParameterSet.ML_KEM_512:
        return ML_KEM_512
    if which is ParameterSet.ML_KEM_768:
        return ML_KEM_768
    if which is ParameterSet.ML_KEM_1024:
        return ML_KEM_1024
    raise AssertionError(f"params_for: unknown parameter set {which}")
