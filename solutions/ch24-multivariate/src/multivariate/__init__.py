"""Chapter 24 of the Encryptorium Book of Post-Quantum Cryptography.

A toy Unbalanced Oil and Vinegar signature scheme over a prime field, plus the
key-size and attack-cost arithmetic behind the chapter's four-family
comparison.

The scheme is pedagogical. At the chapter's (n, m, q) = (5, 2, 7) it is
trivially breakable, and it stays breakable at every parameter set this package
can run in reasonable time. Nothing here should sign anything.
"""

from .gf import inv, matmul, transpose, mat_vec, quadratic_eval
from .linalg import is_invertible, invert_mat, solve_linear
from .uov import (
    UOVParams,
    TOY,
    PublicKey,
    SecretKey,
    sample_secret_transformation,
    sample_central_map,
    oil_oil_block,
    public_map,
    keygen,
    collapse_to_linear_system,
    sign,
    verify,
)
from .sizes import (
    upper_triangular_count,
    uov_public_key_bytes,
    kipnis_shamir_log2_cost,
    kipnis_shamir_search_exponent,
    SchemeSizes,
    ROUND2_SIZES,
)

__all__ = [
    "inv",
    "matmul",
    "transpose",
    "mat_vec",
    "quadratic_eval",
    "is_invertible",
    "invert_mat",
    "solve_linear",
    "UOVParams",
    "TOY",
    "PublicKey",
    "SecretKey",
    "sample_secret_transformation",
    "sample_central_map",
    "oil_oil_block",
    "public_map",
    "keygen",
    "collapse_to_linear_system",
    "sign",
    "verify",
    "upper_triangular_count",
    "uov_public_key_bytes",
    "kipnis_shamir_log2_cost",
    "kipnis_shamir_search_exponent",
    "SchemeSizes",
    "ROUND2_SIZES",
]
