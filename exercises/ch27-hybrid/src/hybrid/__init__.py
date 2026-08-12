"""Chapter 27: Hybrid schemes in practice.

Pure-Python implementations of the two canonical transition-period
hybrids.

- ``x25519``: Curve25519 scalar multiplication per RFC 7748.
- ``ed25519``: EdDSA signatures on Curve25519 per RFC 8032.
- ``mldsa_stub``: documented placeholder standing in for
  solutions/ch12-mldsa, which ships the real FIPS 204 implementation;
  the stub has the ML-DSA-65 byte-size API shape but is not a real
  signature scheme.
- ``kem_combiner``: X25519MLKEM768 construction following the wire
  format in RFC 10024. Imports ML-KEM-768 from
  solutions/ch11-mlkem via sys.path, which is why this package needs
  NumPy even though none of its own modules import it.
- ``sig_combiner``: Ed25519+ML-DSA-65 explicit-composite signature
  following draft-ietf-lamps-pq-composite-sigs, AND-mode.

The chapter text walks pedagogical stdlib-only slices; the full
implementation lives here.
"""

from .x25519 import x25519_scalarmult, x25519_base
from .ed25519 import ed25519_sign, ed25519_verify, ed25519_keygen
from .mldsa_stub import (
    MLDSA65_PK_BYTES,
    MLDSA65_SK_BYTES,
    MLDSA65_SIG_BYTES,
    mldsa65_keygen_stub,
    mldsa65_sign_stub,
    mldsa65_verify_stub,
)
from .kem_combiner import (
    X25519MLKEM768_NAMED_GROUP,
    X25519MLKEM768_PK_BYTES,
    X25519MLKEM768_CT_BYTES,
    X25519MLKEM768_SS_BYTES,
    hybrid_kem_keygen,
    hybrid_kem_encaps,
    hybrid_kem_decaps,
)
from .sig_combiner import (
    composite_sig_keygen,
    composite_sig_sign,
    composite_sig_verify,
)

__all__ = [
    "x25519_scalarmult",
    "x25519_base",
    "ed25519_keygen",
    "ed25519_sign",
    "ed25519_verify",
    "MLDSA65_PK_BYTES",
    "MLDSA65_SK_BYTES",
    "MLDSA65_SIG_BYTES",
    "mldsa65_keygen_stub",
    "mldsa65_sign_stub",
    "mldsa65_verify_stub",
    "X25519MLKEM768_NAMED_GROUP",
    "X25519MLKEM768_PK_BYTES",
    "X25519MLKEM768_CT_BYTES",
    "X25519MLKEM768_SS_BYTES",
    "hybrid_kem_keygen",
    "hybrid_kem_encaps",
    "hybrid_kem_decaps",
    "composite_sig_keygen",
    "composite_sig_sign",
    "composite_sig_verify",
]
