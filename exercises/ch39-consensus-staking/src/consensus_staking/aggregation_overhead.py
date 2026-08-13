"""Per-validator-set byte budget across a fixed five-candidate set.

The chapter's running example pins five candidate primitives for the
Strand consensus surface:

- ``BLS-BLS12-381`` is the legacy baseline used by Ethereum's beacon
  chain. The 96-byte signature is the canonical G2 form per the IETF
  BLS signature draft and the Ethereum consensus-specs. The 48-byte
  public key is the canonical G1 form. Aggregation collapses N partial
  signatures from N validators to one 96-byte aggregate signature plus
  a participation bitmap of ceiling(N / 8) bytes.
- ``ML-DSA-65`` is the lattice candidate per FIPS 204 (Table 1):
  3309-byte signature, 1952-byte public key. Does not aggregate
  trivially; N validators produce N independent signatures.
- ``SLH-DSA-128s`` is the hash-based candidate per FIPS 205 (Table 1):
  7856-byte signature, 32-byte public key. Does not aggregate; the
  conservative-assumption choice for a long-lived validator-set key.
- ``FN-DSA-512`` is the lattice signature NIST selected for FIPS 206.
  The 666-byte signature and 897-byte public key are Falcon-512's,
  from the Falcon specification v1.2 (round-3 submission), section
  "Parameter sets": public key bytelength 897, signature bytelength
  sbytelen 666. FIPS 206 itself has published nothing at chain-tip
  2026, so these figures are the submission's rather than a
  standard's and can move at finalization. Smallest post-quantum
  signature among the four NIST candidates. Does not aggregate
  trivially.
- ``threshold-ML-DSA`` is the threshold-signature variant of ML-DSA
  per active research at chain-tip 2026; combines T partial signatures
  to one ML-DSA-65 signature plus a per-validator participation
  bitmap analogous to the BLS bitmap. Research-grade at chain-tip
  2026; no NIST standard.

Validator-count anchor: Ethereum mainnet at chain-tip 2026 carries on
the order of one million active validators. The chapter uses
N = 1_000_000 as the round-figure illustrative anchor for per-epoch
attestation-set calculations. Each validator attests once per epoch
(SLOTS_PER_EPOCH = 32 on Ethereum mainnet); the per-validator-set
byte total below is the upper-bound thought experiment in which all N
validators sign the same message in one aggregation operation. The
literal beacon-chain structure splits this across 32 slots and the
sub-committees inside each slot, but the architectural property
(aggregation collapses N to 1 vs PQ produces N) holds at any subset.
The figure records as a named constant so a future revision can
update one number rather than recompute every figure.

Aggregate signature size for BLS:
    aggregate_bytes(N) = 96 + ceil(N / 8)

Per-validator-set byte total under a non-aggregating PQ candidate:
    pq_total_bytes(N, sig_bytes) = N * sig_bytes

Per-validator-set byte total under a threshold-PQ candidate:
    threshold_total(N) = sig_bytes + ceil(N / 8)
where the second term is the analogous participation bitmap that
records which T-of-N validators contributed to the combine round.
A deployable threshold-PQ protocol must ship a per-validator
signer set on-chain to attribute attestation rewards and slashing.

Aggregation ratio: per-validator-set partial-sig total divided by
per-validator-set aggregate output size. BLS at large N saturates
near 96 * 8 = 768 because the bitmap dominates the denominator;
threshold-ML-DSA at large N saturates near 8 * 3309 = 26472 for
the same reason (the bitmap dominates the denominator at the
per-signature byte size scaled by 8); plain PQ candidates produce
ratio 1.
"""

from typing import Dict, TypedDict


class CandidateSizes(TypedDict):
    sig_bytes: int
    pk_bytes: int
    aggregates: bool
    deployment_status: str
    notes: str


CANDIDATES: Dict[str, CandidateSizes] = {
    "BLS-BLS12-381": {
        "sig_bytes": 96,
        "pk_bytes": 48,
        "aggregates": True,
        "deployment_status": "deployed-legacy",
        "notes": (
            "Ethereum beacon-chain baseline; Shor-vulnerable on the "
            "BLS12-381 discrete-log assumption"
        ),
    },
    "ML-DSA-65": {
        "sig_bytes": 3309,
        "pk_bytes": 1952,
        "aggregates": False,
        "deployment_status": "fips-final",
        "notes": "FIPS 204 final; per-validator linear blowup",
    },
    "SLH-DSA-128s": {
        "sig_bytes": 7856,
        "pk_bytes": 32,
        "aggregates": False,
        "deployment_status": "fips-final",
        "notes": "FIPS 205 final; conservative-assumption preference",
    },
    "FN-DSA-512": {
        "sig_bytes": 666,
        "pk_bytes": 897,
        "aggregates": False,
        "deployment_status": "pre-draft",
        "notes": (
            "FIPS 206 under development, no initial public draft "
            "released; sizes are Falcon-512's from the round-3 "
            "submission; smallest PQ signature in the candidate set"
        ),
    },
    "threshold-ML-DSA": {
        "sig_bytes": 3309,
        "pk_bytes": 1952,
        "aggregates": True,
        "deployment_status": "research-grade",
        "notes": (
            "threshold variant of ML-DSA; collapses T partials to one "
            "ML-DSA-65 signature via the combine round; research-grade"
        ),
    },
}

# Ethereum mainnet at chain-tip 2026. Round-figure illustrative anchor.
# The exact validator count varies day to day; the chapter's
# calculations are linear in N and the chapter rounds figures
# accordingly.
ETH_VALIDATORS_2026 = 1_000_000

# BLS canonical sizes per the IETF BLS signature draft and the
# Ethereum consensus-specs. Recorded as constants for the chapter.
BLS_AGGREGATE_SIG_BYTES = 96


def participation_bitmap_bytes(N: int) -> int:
    """Bytes required for the BLS participation bitmap on N validators.

    One bit per validator, rounded up to the nearest byte. Matches the
    Ethereum consensus-specs ``Bitlist[VALIDATOR_REGISTRY_LIMIT]``
    serialization at the byte-count level (the SSZ wrapping adds a
    fixed overhead the chapter ignores for the comparison).
    """
    # EXERCISE: implement this function.
    #
    # One bit per validator rounded up to a whole byte, which is (N + 7) //
    # 8. Assert N is non-negative and let zero validators return zero bytes
    # rather than special-casing them. This is the term that does not
    # aggregate away: the 96-byte BLS signature is flat in N while this
    # grows linearly, so at a million validators the bitmap is 125000 bytes
    # against 96 and dominates the whole payload.
    #
    # Reference: Chapter 39, 'BLS signatures, aggregation, and the discrete-log reduction'
    #
    # Proved by:
    #   tests/ch39/test_aggregation_overhead.py
    raise NotImplementedError("exercise: participation_bitmap_bytes")


def bls_aggregate_total_bytes(N: int) -> int:
    """Total bytes for the BLS aggregate signature plus the bitmap.

    Aggregate signature is 96 bytes regardless of N. The participation
    bitmap is ceil(N / 8). The two together carry the entire
    attestation-aggregate payload on the wire.
    """
    # EXERCISE: implement this function.
    #
    # BLS_AGGREGATE_SIG_BYTES plus participation_bitmap_bytes(N). The first
    # term is constant because the pairing lets N same-message signatures
    # collapse to one G2 group product; the second is what the chain still
    # has to carry to say which validators contributed, and it is why the
    # aggregate payload is not actually constant in N.
    #
    # Reference: Chapter 39, 'BLS signatures, aggregation, and the discrete-log reduction'
    #
    # Proved by:
    #   tests/ch39/test_aggregation_overhead.py
    raise NotImplementedError("exercise: bls_aggregate_total_bytes")


def pq_total_bytes(primitive: str, N: int) -> int:
    """Total per-validator-set bytes shipping on-chain.

    For non-aggregating candidates, each validator's signature ships
    independently; the per-validator-set total is N times sig_bytes.
    For BLS the function returns bls_aggregate_total_bytes(N) (one
    96-byte aggregate plus the ceil(N/8) participation bitmap). For
    threshold-ML-DSA the function returns the threshold-aggregate
    size (one ML-DSA-65 signature) plus a per-validator participation
    bitmap of ceil(N/8) bytes, analogous to the BLS bitmap; a
    deployable threshold-PQ protocol must ship a signer set on-chain
    to attribute attestation rewards and slashing.
    """
    # EXERCISE: implement this function.
    #
    # Three branches after asserting the primitive is known and N is
    # non-negative. BLS-BLS12-381 delegates to bls_aggregate_total_bytes.
    # threshold-ML-DSA returns one combined ML-DSA-65 signature plus the
    # same ceil(N/8) participation bitmap, because a deployable threshold
    # protocol still has to name its signer set on-chain to attribute
    # rewards and slashing. Everything else is a plain non-aggregating
    # candidate and returns N times its signature size. That last branch is
    # the chapter's headline: 3.3 GB per attestation set for ML-DSA-65 at a
    # million validators against 125 KB for BLS.
    #
    # Reference: Chapter 39, 'Pick the candidate per validator-set byte budget'
    #
    # Proved by:
    #   tests/ch39/test_aggregation_overhead.py
    raise NotImplementedError("exercise: pq_total_bytes")


def aggregation_ratio(primitive: str, N: int) -> float:
    """Per-validator-set partial-sig total over aggregate output size.

    BLS partial total is N * 96 and aggregate output is 96 +
    ceil(N/8); at large N the bitmap dominates the denominator and
    the ratio saturates near 96 * 8 = 768. Threshold-ML-DSA partial
    total is N * 3309 and aggregate output is 3309 + ceil(N/8); at
    large N the ratio approaches 8 * 3309 = 26472 (the per-signature
    byte size scaled by 8 because the bitmap dominates). ML-DSA-65,
    SLH-DSA-128s, and FN-DSA-512 produce N independent signatures
    so partial total equals output and the ratio is 1.
    """
    # EXERCISE: implement this function.
    #
    # How far the candidate compresses N partial signatures: N times
    # sig_bytes on top, pq_total_bytes(primitive, N) underneath. Assert N is
    # at least one before dividing, since a zero validator set has no
    # partials to compress. A plain post-quantum candidate returns exactly
    # 1.0 because the two expressions are the same number. BLS climbs with N
    # and saturates near 96 * 8 = 768 once the bitmap dominates the
    # denominator, and threshold-ML-DSA saturates near 3309 * 8 for the same
    # reason. The factor of 8 in both limits is the bitmap's one bit per
    # validator.
    #
    # Reference: Chapter 39, 'BLS signatures, aggregation, and the discrete-log reduction'
    #
    # Proved by:
    #   tests/ch39/test_aggregation_overhead.py
    raise NotImplementedError("exercise: aggregation_ratio")


def evaluate(primitive: str, N: int = ETH_VALIDATORS_2026) -> dict:
    """Combined per-validator-set envelope for the candidate.

    Returns a dict with the four pedagogical numbers the chapter's
    inline Block 1 prints: signature bytes, public key bytes,
    per-validator-set total bytes (aggregated for BLS / threshold;
    linear N times sig_bytes for plain PQ), and aggregation ratio.
    """
    # EXERCISE: implement this function.
    #
    # Assemble the per-candidate envelope the chapter's Block 1 prints:
    # primitive, sig_bytes, pk_bytes, aggregates, deployment_status,
    # validator_count, per_set_bytes, aggregation_ratio, notes. Read the
    # fixed fields off the CANDIDATES row once and delegate the two computed
    # fields to pq_total_bytes and aggregation_ratio. Assert N is at least
    # one rather than non-negative, because the ratio is undefined at zero.
    #
    # Reference: Chapter 39, 'Pick the candidate per validator-set byte budget'
    #
    # Proved by:
    #   tests/ch39/test_aggregation_overhead.py
    raise NotImplementedError("exercise: evaluate")


def per_set_bytes_against_baseline(N: int = ETH_VALIDATORS_2026) -> Dict[str, dict]:
    """Per-candidate envelope against the BLS baseline at validator count N.

    Useful for the chapter's tradeoffs table. Each row carries the
    candidate's per-set bytes and the multiplicative factor against
    the BLS aggregate baseline.
    """
    # EXERCISE: implement this function.
    #
    # Compute the BLS aggregate total once as the baseline, then walk
    # CANDIDATES building a row per primitive with per_set_bytes and
    # factor_vs_bls, the latter being the candidate's total divided by that
    # baseline. Keep the division floating point: the interesting numbers
    # are 26451.69 for ML-DSA-65 and 1.03 for threshold-ML-DSA at a million
    # validators, and the second one only reads as near-parity if the
    # fractional part survives. This is the table Exercise 1 asks for.
    #
    # Reference: Chapter 39, 'Pick the candidate per validator-set byte budget'
    #
    # Proved by:
    #   tests/ch39/test_aggregation_overhead.py
    raise NotImplementedError("exercise: per_set_bytes_against_baseline")
