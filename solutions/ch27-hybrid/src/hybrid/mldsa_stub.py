"""Documented placeholder for ML-DSA-65 (FIPS 204).

The real thing is in the repository: the Chapter 12 ML-DSA from-scratch
package (``solutions/ch12-mldsa``) matches the NIST ACVP vectors for
ML-DSA-65 byte-for-byte. This module is a deliberate placeholder used
anyway, because Chapter 27's subject is the composite combiner rather
than ML-DSA, and a component with the correct ML-DSA-65 byte-size API
exercises the combiner logic and the AND-mode verification semantics
end to end without pulling a second lattice implementation into this
package.

What this stub IS:

- A byte-size-correct harness for the ML-DSA-65 keygen/sign/verify
  interface: 1952-byte public keys, 4032-byte secret keys, 3309-byte
  signatures (FIPS 204 Table 2).
- Deterministic: the same (sk, message) pair always produces the same
  signature bytes.
- Binding: a signature is valid only if it was produced over the
  exact (pk, message) pair it is verified against. This is sufficient
  to exercise the AND-mode composite-signature logic in
  ``sig_combiner``.

What this stub is NOT:

- A signature scheme. It offers NO cryptographic security. It is a
  hash-based binding function dressed in the ML-DSA-65 shape.
- FIPS 204 ML-DSA-65. Swap this module out for
  ``solutions/ch12-mldsa`` to get the real one; the combiner in
  ``sig_combiner`` depends only on the byte-size API, so the swap is
  a one-line change.

FIPS 204 Table 2 references the sizes used here.
"""

import hashlib


MLDSA65_PK_BYTES = 1952
MLDSA65_SK_BYTES = 4032
MLDSA65_SIG_BYTES = 3309


def _expand(seed: bytes, length: int) -> bytes:
    out = b""
    counter = 0
    while len(out) < length:
        out += hashlib.sha512(seed + counter.to_bytes(4, "little")).digest()
        counter += 1
    return out[:length]


def mldsa65_keygen_stub(seed: bytes) -> tuple[bytes, bytes]:
    """Derive a stub (pk, sk) pair from a 32-byte seed.

    Returns byte strings of the FIPS 204 ML-DSA-65 public-key and
    secret-key lengths. Not a real signature-scheme keygen; see the
    module docstring.
    """
    if len(seed) != 32:
        raise ValueError("seed must be 32 bytes")
    material = _expand(seed, MLDSA65_PK_BYTES + MLDSA65_SK_BYTES)
    pk = material[:MLDSA65_PK_BYTES]
    sk_body = material[MLDSA65_PK_BYTES:]
    sk = pk + sk_body[MLDSA65_PK_BYTES:]
    sk = sk[:MLDSA65_SK_BYTES]
    if len(sk) < MLDSA65_SK_BYTES:
        sk = sk + _expand(seed + b"sk", MLDSA65_SK_BYTES - len(sk))
    return pk, sk


def mldsa65_sign_stub(sk: bytes, message: bytes) -> bytes:
    """Produce a stub signature of ``MLDSA65_SIG_BYTES``.

    The signature is a deterministic expansion of ``sk || message`` to
    3309 bytes. Binding to ``sk`` and ``message`` is sufficient for
    testing the AND-mode composite combiner; it is not cryptographic.
    """
    if len(sk) != MLDSA65_SK_BYTES:
        raise ValueError(f"sk must be {MLDSA65_SK_BYTES} bytes")
    pk_part = sk[:MLDSA65_PK_BYTES]
    return _expand(pk_part + message, MLDSA65_SIG_BYTES)


def mldsa65_verify_stub(pk: bytes, message: bytes, signature: bytes) -> bool:
    """Return True iff ``signature`` equals the stub-expansion over ``(pk, message)``."""
    if len(pk) != MLDSA65_PK_BYTES or len(signature) != MLDSA65_SIG_BYTES:
        return False
    expected = _expand(pk + message, MLDSA65_SIG_BYTES)
    return expected == signature
