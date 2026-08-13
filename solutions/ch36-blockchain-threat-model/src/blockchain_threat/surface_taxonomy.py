"""Quantum-vulnerability classifier for blockchain cryptographic surfaces.

The classifier walks a list of asset records and tags each with one
of three labels:

- ``"shor-vulnerable"``: the primitive's security reduces to integer
  factorization, a discrete-log problem in a Shor-reducible group, or
  a pairing-based assumption on a pairing-friendly elliptic curve.
  ECDSA, Schnorr, EdDSA, BLS over BLS12-381, and RSA all fall here.
- ``"hash-quantum-degraded"``: the primitive is a hash or symmetric
  function. Grover gives a square-root preimage speedup and
  Brassard-Hoyer-Tapp gives a roughly ``2^(n/3)`` collision-search
  cost, but neither yields a polynomial-time break; the mitigation
  is a parameter bump, not a primitive swap.
- ``"post-quantum-standardized"``: the primitive is a standardized
  post-quantum signature scheme (FIPS 204 / FIPS 205, or the
  SP 800-208 stateful schemes XMSS-MT and LMS). It is the migration
  target, not a guarantee of unconditional security.

FN-DSA (Falcon) is deliberately absent from the table. Its standard,
FIPS 206, is under development at chain-tip 2026 with no Initial
Public Draft released, so no final parameter set exists to classify
and the third label would be false of it. An asset record naming
``FN-DSA-512`` therefore crashes on the unknown-primitive assertion,
which is the intended behaviour: the table records what a standard
says today, not what one is expected to say.

Asset records are mappings with at least the keys ``surface``,
``primitive``, ``exposure``, and ``lifecycle``. The classifier reads
the ``primitive`` key only; the other keys carry context for code
that walks the same records in Ch 37 through Ch 41 (the chapters
that perform the actual migrations).

The contract is narrow on purpose. The classifier refuses any
primitive name not in the lookup table. New primitive names land via
extension of ``PRIMITIVE_CLASSIFICATION``, not via a fallback rule;
the chapter relies on every primitive being explicitly classified.
"""

from collections.abc import Iterable, Mapping

PRIMITIVE_CLASSIFICATION: Mapping[str, str] = {
    # Discrete-log-based, factoring-based, or pairing-based; Shor
    # breaks all of these in polynomial time on a fault-tolerant
    # quantum computer.
    "ECDSA-secp256k1": "shor-vulnerable",
    "Schnorr-secp256k1": "shor-vulnerable",
    "EdDSA-Ed25519": "shor-vulnerable",
    "BLS-BLS12-381": "shor-vulnerable",
    "RSA-2048": "shor-vulnerable",
    # Hash- or symmetric-based; Grover yields a square-root preimage
    # speedup and Brassard-Hoyer-Tapp gives roughly 2^(n/3) collision
    # search, but neither yields a polynomial-time break. The
    # mitigation is a parameter bump, not a primitive swap.
    "SHA-256": "hash-quantum-degraded",
    "SHA3-256": "hash-quantum-degraded",
    "Keccak-256": "hash-quantum-degraded",
    "BLAKE2b": "hash-quantum-degraded",
    "AES-256-GCM": "hash-quantum-degraded",
    # Post-quantum signature schemes standardized at NIST (FIPS 204,
    # FIPS 205) or under SP 800-208 (stateful hash-based).
    "ML-DSA-65": "post-quantum-standardized",
    "ML-DSA-87": "post-quantum-standardized",
    "SLH-DSA-128s": "post-quantum-standardized",
    "SLH-DSA-256f": "post-quantum-standardized",
    "XMSS-MT": "post-quantum-standardized",
    "LMS": "post-quantum-standardized",
}


def classify(asset: Mapping[str, object]) -> str:
    """Return the quantum-vulnerability class for one asset record.

    Reads ``asset["primitive"]`` and returns one of
    ``"shor-vulnerable"``, ``"hash-quantum-degraded"``, or
    ``"post-quantum-standardized"``. Asserts that the primitive name
    is in ``PRIMITIVE_CLASSIFICATION``; an unknown primitive crashes
    loudly per CLAUDE.md section 9.
    """
    primitive = asset["primitive"]
    assert primitive in PRIMITIVE_CLASSIFICATION, (
        f"unknown primitive: {primitive!r}"
    )
    return PRIMITIVE_CLASSIFICATION[primitive]


def classify_all(
    assets: Iterable[Mapping[str, object]],
) -> list[tuple[str, str]]:
    """Classify every asset; return ``(surface, class)`` in input order.

    Each tuple pairs the asset's ``surface`` field with its
    classification. Ordering is preserved so the caller can pair the
    output back with the input list by index.
    """
    return [(str(asset["surface"]), classify(asset)) for asset in assets]
