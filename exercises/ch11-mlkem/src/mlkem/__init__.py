"""Chapter 11: ML-KEM (FIPS 203) from scratch.

A pedagogical Python package for ML-KEM as standardized in NIST
FIPS 203. The package exposes the three parameter-set instances
``ML_KEM_512``, ``ML_KEM_768``, ``ML_KEM_1024``, the three internal
routines ``ml_kem_keygen_internal``, ``ml_kem_encaps_internal`` and
``ml_kem_decaps_internal``, and the K-PKE layer beneath them. The
external ML-KEM.KeyGen and ML-KEM.Encaps of FIPS 203 section 7 are
not implemented: they only add the sampling of ``d``, ``z`` and
``m`` from an approved RBG, and the ACVP vectors take those seeds
as inputs.

The implementation matches FIPS 203 section 5 (K-PKE) and section 6
(the internal algorithms, which apply the Fujisaki-Okamoto transform
in its implicit-rejection form) variable names and call structure
literally. The chapter text walks pedagogical
numpy slices of these functions; the full implementation here is
the byte-for-byte NIST ACVP-vector-matching version.
"""

from .params import (
    MLKEMParams,
    ParameterSet,
    ML_KEM_512,
    ML_KEM_768,
    ML_KEM_1024,
)
from .hashes import H, G, J, PRF, XOF
from .k_pke import k_pke_keygen, k_pke_encrypt, k_pke_decrypt
from .ml_kem import (
    ml_kem_keygen_internal,
    ml_kem_encaps_internal,
    ml_kem_decaps_internal,
)

__all__ = [
    "MLKEMParams",
    "ParameterSet",
    "ML_KEM_512",
    "ML_KEM_768",
    "ML_KEM_1024",
    "H",
    "G",
    "J",
    "PRF",
    "XOF",
    "k_pke_keygen",
    "k_pke_encrypt",
    "k_pke_decrypt",
    "ml_kem_keygen_internal",
    "ml_kem_encaps_internal",
    "ml_kem_decaps_internal",
]
