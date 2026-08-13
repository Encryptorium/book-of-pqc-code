"""PQRA-weighted CBOM migration-urgency rollup.

The rollup ranks a list of Ch 25 CBOM touchpoints by their **quantum
migration urgency** (not general operational risk; a quantum-safe
touchpoint can still carry weak ownership, telemetry, or rollback
discipline that this rollup does not measure).

Each touchpoint carries:

- ``name``: the touchpoint identifier from the Ch 25 CBOM.
- ``quantum_status``: one of ``"vulnerable"``, ``"grover-only"``, or
  ``"quantum-safe"`` (Ch 25 classification).
- ``exposure``: one of ``"public"`` or ``"internal"`` (Ch 25 Exercise 3).
- ``readiness``: a dict mapping each PQRA domain name to a 1-5 maturity
  score (higher = more ready, lower = larger gap).

The urgency score is

    urgency = quantum_mult * exposure_mult * sum((5 - score) * weight)

where the sum runs over PQRA domains. A ``quantum-safe`` touchpoint
always scores 0 (already migrated, no quantum-migration work). A
``public vulnerable`` touchpoint with every domain at readiness 1 scores
the maximum (3 * 2 * sum((5 - 1) * w) = 6 * 4 = 24 when weights sum to
1.0). Ties break on name for determinism.

The seven PQRA domains and their default weights come from the
Encryptorium Post-Quantum Readiness Assessment v1.0 rubric. The caller
can supply a custom weights dict; the rollup only checks that the
weights sum to 1.0 and that every touchpoint carries a score for every
weighted domain.
"""

from collections.abc import Iterable, Mapping, Sequence

QUANTUM_MULT: Mapping[str, int] = {
    "vulnerable": 3,
    "grover-only": 1,
    "quantum-safe": 0,
}

EXPOSURE_MULT: Mapping[str, int] = {
    "public": 2,
    "internal": 1,
}

PQRA_DOMAINS: Sequence[str] = (
    "inventory",
    "data_sensitivity",
    "standards_compliance",
    "migration_readiness",
    "vendor_supply_chain",
    "timeline_urgency",
    "governance_policy",
)

DEFAULT_PQRA_WEIGHTS: Mapping[str, float] = {
    "inventory": 0.20,
    "data_sensitivity": 0.15,
    "standards_compliance": 0.10,
    "migration_readiness": 0.20,
    "vendor_supply_chain": 0.15,
    "timeline_urgency": 0.10,
    "governance_policy": 0.10,
}


def migration_urgency(
    touchpoints: Iterable[Mapping[str, object]],
    weights: Mapping[str, float] = DEFAULT_PQRA_WEIGHTS,
) -> list[tuple[str, float]]:
    """Rank touchpoints by quantum migration urgency, highest first.

    Returns a list of ``(name, urgency_score)`` tuples. Raises
    ``ValueError`` if the weights do not sum to 1.0, if a touchpoint
    uses an unknown ``quantum_status`` or ``exposure`` value, if a
    readiness score is missing for a weighted domain, or if a readiness
    score is outside the 1-5 range. The valid readiness range is 1
    through 5; 0 is not a valid score ("not yet assessed" is out of
    scope for the rubric and must be resolved before a rollup).
    """
    # EXERCISE: implement this function.
    #
    # urgency = quantum_mult * exposure_mult * sum over the weighted domains
    # of (5 - score) * weight. Check the weights sum to 1.0 within 1e-9
    # before scoring anything, then per touchpoint reject an unrecognised
    # quantum_status or exposure, a domain the weights name that the
    # readiness dict lacks, and any score outside 1 through 5. Zero is not a
    # valid readiness score: 'not yet assessed' has to be resolved before a
    # rollup, not averaged into one. A readiness of 5 contributes nothing to
    # the gap and quantum-safe multiplies by 0, so an already-migrated
    # touchpoint scores zero however weak the rest of its record is; this
    # ranks quantum migration urgency, not general operational risk. Sort
    # descending by score with the name as the tie-break so the ordering is
    # deterministic.
    #
    # Reference: Chapter 30, 'Discovery and assessment (2025-2028)'
    #
    # Proved by:
    #   tests/ch30/test_risk_rollup.py
    raise NotImplementedError("exercise: migration_urgency")
