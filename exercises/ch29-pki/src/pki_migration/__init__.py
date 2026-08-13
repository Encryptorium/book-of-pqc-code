"""Chapter 29: operator tooling for post-quantum PKI migration.

Three utilities:

- ``chain_analyzer``: classify X.509 chain signature algorithms as
  classical, single-post-quantum, or composite; flag mixed chains.
- ``jwks_verifier``: build a JWKS fragment that carries an Ed25519 +
  ML-DSA-65 composite public key, look up a JWT's ``kid``, and verify
  the JWT under that composite key.
- ``xmss_index``: durable on-disk counter wrapper around the Ch 15
  XMSS ``xmss_sign`` that refuses to sign if the counter file is
  absent, corrupt, or exhausted.

The JWKS verifier imports ``composite_sig_verify`` from
``solutions/ch27-hybrid``; the XMSS index wrapper imports ``xmss_sign``
from ``solutions/ch15-xmss``. Both cross-chapter imports use ``sys.path``
insertion at module load time.
"""

from .chain_analyzer import (
    CertRef,
    ChainReport,
    classify_oid,
    analyze_chain,
    CLASSICAL_OIDS,
    SINGLE_PQ_OIDS,
    COMPOSITE_OIDS,
    OID_RSA_SHA256,
    OID_ECDSA_P384_SHA384,
    OID_ECDSA_P256_SHA256,
    OID_ED25519,
    OID_ML_DSA_65,
    OID_SLH_DSA_SHA2_128S,
    OID_MLDSA65_ED25519_SHA512,
)
from .jwks_verifier import (
    COMPOSITE_KTY,
    COMPOSITE_ALG,
    build_composite_jwk,
    find_jwk,
    verify_composite_jwt,
)
from .xmss_index import (
    initialize_counter,
    durable_xmss_sign,
    read_counter,
)

__all__ = [
    "CertRef",
    "ChainReport",
    "classify_oid",
    "analyze_chain",
    "CLASSICAL_OIDS",
    "SINGLE_PQ_OIDS",
    "COMPOSITE_OIDS",
    "OID_RSA_SHA256",
    "OID_ECDSA_P384_SHA384",
    "OID_ECDSA_P256_SHA256",
    "OID_ED25519",
    "OID_ML_DSA_65",
    "OID_SLH_DSA_SHA2_128S",
    "OID_MLDSA65_ED25519_SHA512",
    "COMPOSITE_KTY",
    "COMPOSITE_ALG",
    "build_composite_jwk",
    "find_jwk",
    "verify_composite_jwt",
    "initialize_counter",
    "durable_xmss_sign",
    "read_counter",
]
