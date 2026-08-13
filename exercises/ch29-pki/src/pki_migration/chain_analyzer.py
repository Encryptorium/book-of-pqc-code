"""X.509 chain-algorithm analyzer.

Pedagogical chain analyzer for deployment runbooks. Does not parse
real DER certificates. Input is a sequence of ``CertRef`` tuples
(leaf first) giving subject, issuer, and the certificate's
signatureAlgorithm OID. Output is a ``ChainReport`` classifying the
chain by overall posture.

Cited OIDs:

- ``id-sha256WithRSAEncryption`` (RFC 8017), classical.
- ``ecdsa-with-SHA256`` (RFC 5758), classical; P-256 default.
- ``ecdsa-with-SHA384`` (RFC 5758), classical; P-384 default.
- ``id-Ed25519`` (RFC 8410), classical.
- ``id-ml-dsa-65`` (RFC 9881, section 5), single-PQ.
- ``id-slh-dsa-sha2-128s`` (RFC 9909, section 4), single-PQ.
- ``id-MLDSA65-Ed25519-SHA512``
  (draft-ietf-lamps-pq-composite-sigs-19, Ch 27-settled), composite;
  OID ``1.3.6.1.5.5.7.6.48``.

The overall posture distinguishes the deployment-bug case (a
classical link sitting above a post-quantum or composite leaf) from
the legitimate transition case (a classical leaf still under
post-quantum higher links during re-issuance), so an operator
running a fleet-wide scan does not flag a rollout in progress as a
bug.

Audit coverage note. This analyzer inspects each certificate's
``signatureAlgorithm`` OID only. A production deployment audit must
also inspect each CA certificate's ``SubjectPublicKeyInfo`` (RFC
5280 section 4.1.2.7): a PQ or composite signature over a CA
certificate does not make the subtree quantum-safe if the CA's own
signing key is classical (RSA, ECDSA, or Ed25519), because a future
quantum attacker who recovers the CA private key from its classical
public key can sign new child certificates under that CA. The
``CertRef`` dataclass tracks only the signature OID; a production
extension would carry the issuer / subject public-key algorithm
alongside and run a parallel classification.
"""

from dataclasses import dataclass
from typing import Iterable

OID_RSA_SHA256 = "1.2.840.113549.1.1.11"
OID_ECDSA_P256_SHA256 = "1.2.840.10045.4.3.2"
OID_ECDSA_P384_SHA384 = "1.2.840.10045.4.3.3"
OID_ED25519 = "1.3.101.112"

OID_ML_DSA_65 = "2.16.840.1.101.3.4.3.18"
OID_SLH_DSA_SHA2_128S = "2.16.840.1.101.3.4.3.20"

OID_MLDSA65_ED25519_SHA512 = "1.3.6.1.5.5.7.6.48"

CLASSICAL_OIDS = frozenset(
    {OID_RSA_SHA256, OID_ECDSA_P256_SHA256, OID_ECDSA_P384_SHA384, OID_ED25519}
)
SINGLE_PQ_OIDS = frozenset({OID_ML_DSA_65, OID_SLH_DSA_SHA2_128S})
COMPOSITE_OIDS = frozenset({OID_MLDSA65_ED25519_SHA512})


def classify_oid(oid: str) -> str:
    """Return ``"classical"``, ``"single-pq"``, ``"composite"``, or
    ``"unknown"``."""
    if oid in CLASSICAL_OIDS:
        return "classical"
    if oid in SINGLE_PQ_OIDS:
        return "single-pq"
    if oid in COMPOSITE_OIDS:
        return "composite"
    return "unknown"


@dataclass(frozen=True)
class CertRef:
    """Pedagogical certificate reference: subject, issuer, sig OID."""

    subject: str
    issuer: str
    sig_oid: str


@dataclass(frozen=True)
class ChainReport:
    """Report for a chain: depth, per-cert classes, overall posture."""

    depth: int
    per_cert: tuple
    overall: str


def analyze_chain(chain: Iterable[CertRef]) -> ChainReport:
    """Analyze a leaf-first chain and report overall posture.

    Overall posture is:

    - ``empty`` for an empty chain.
    - ``unknown-oid-present`` if any cert's OID is not recognized.
    - ``classical-only`` if every cert is classical.
    - ``single-pq-only`` if every cert is a single-PQ signature.
    - ``composite-only`` if every cert is a composite signature.
    - ``mixed-classical-above-pq-leaf`` if the leaf is single-PQ or
      composite and at least one higher link is classical (the
      deployment-bug case: forge the classical link, forge the leaf).
    - ``mixed-transition`` for any other mixed pattern (the
      legitimate rollout case: classical leaf under PQ higher links
      while leaf re-issuance is in flight, for example).
    """
    # EXERCISE: implement this function.
    #
    # The chain arrives leaf first, so chain[0] is the leaf and chain[-1] is
    # the root. Classify every certificate, then reduce the set of classes
    # to one overall posture. An empty chain is 'empty'. Any unknown OID
    # outranks everything else and reports 'unknown-oid-present', because a
    # scanner that cannot name an algorithm cannot rank the chain it sits
    # in. A single-class set reports 'classical-only', 'single-pq-only', or
    # 'composite-only'. For a mixed chain the leaf's own class decides: a
    # single-PQ or composite leaf with a classical link above it is
    # 'mixed-classical-above-pq-leaf', the deployment bug, because forging
    # the classical link forges the leaf transitively. Every other mix is
    # 'mixed-transition', the legitimate re-issuance state where the higher
    # links have moved and the leaf has not. Report the depth and the
    # per-certificate class tuple alongside the verdict.
    #
    # Reference: Chapter 29, 'CA-hierarchy migration'
    #
    # Proved by:
    #   tests/ch29/test_chain_algorithm_scan.py
    raise NotImplementedError("exercise: analyze_chain")
