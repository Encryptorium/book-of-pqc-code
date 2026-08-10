"""ML-DSA (FIPS 204) from scratch.

A byte-for-byte reference implementation of the Module-Lattice-Based Digital
Signature Algorithm at the three standardized parameter sets ML-DSA-44/65/87.
It follows FIPS 204's variable names and call structure literally: the full
256-point NTT at q = 8380417, the rounding/hint algebra (Power2Round, Decompose,
MakeHint, UseHint), rejection sampling (ExpandA, ExpandS, ExpandMask,
SampleInBall), the BitPack/SimpleBitPack serializers, and the Fiat-Shamir-with-
aborts KeyGen/Sign/Verify. It matches the NIST ACVP test vectors byte-for-byte
(see tests/ch12/test_vectors.py).

The exposed operations are the *internal* (explicit-seed / explicit-rnd) variants
that the ACVP vectors drive directly, plus the external context wrappers a
deploying application calls. The OS-randomness-drawing outermost KeyGen/Sign are
omitted because every seed and rnd is supplied by the caller here; the numpy code
slices printed in the chapter text are a pedagogical subset of this full
byte-exact implementation. This is toy code: it crashes loudly on bad input and
does not attempt constant-time execution.
"""

from .params import (
    MLDSAParams,
    ParameterSet,
    ML_DSA_44,
    ML_DSA_65,
    ML_DSA_87,
    params_for,
    ML_DSA_Q,
    ML_DSA_N,
    ML_DSA_D,
    ML_DSA_ZETA,
)
from .ml_dsa import (
    ml_dsa_keygen_internal,
    ml_dsa_sign_internal,
    ml_dsa_verify_internal,
    ml_dsa_sign,
    ml_dsa_verify,
)

__all__ = [
    "MLDSAParams", "ParameterSet",
    "ML_DSA_44", "ML_DSA_65", "ML_DSA_87", "params_for",
    "ML_DSA_Q", "ML_DSA_N", "ML_DSA_D", "ML_DSA_ZETA",
    "ml_dsa_keygen_internal", "ml_dsa_sign_internal", "ml_dsa_verify_internal",
    "ml_dsa_sign", "ml_dsa_verify",
]
