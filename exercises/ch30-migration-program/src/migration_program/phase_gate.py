"""Phase-gate exit-criteria checker.

Validates whether a named program phase's exit criteria are met against
a gate record. The four phases follow the NCSC 2025 timeline anchors:

- ``discovery`` (2025-2028): CBOM complete, PQRA scored, owners
  assigned.
- ``first-wave`` (2028-2031): public-facing vulnerable touchpoints
  migrated, rollback drill completed.
- ``broad-rollout`` (2031-2035): remaining vulnerable touchpoints
  migrated, composite-aware client population above a threshold.
- ``end-of-migration`` (2035+): classical algorithms retired from
  every surviving chain, PQ-only mode asserted (the classical
  component of every composite chain is now retired, leaving single-PQ
  signers everywhere), post-migration review signed off.

A gate record is a ``Mapping[str, object]`` where each key is a
criterion name and the value is ``True`` if the criterion has been met.
Any value other than ``True`` (missing key, ``False``, any falsy value)
counts as unmet.

The checker returns a ``PhaseGateResult`` with the phase name, overall
pass/fail, the list of met criteria, and the list of missing criteria.
Missing criteria are reported in the order defined by
``PHASE_EXIT_CRITERIA`` so a runbook can step through them in sequence.

An unknown phase name raises ``ValueError``.
"""

from collections.abc import Mapping
from dataclasses import dataclass

PHASE_EXIT_CRITERIA: Mapping[str, tuple[str, ...]] = {
    "discovery": (
        "cbom_complete",
        "pqra_scored",
        "owners_assigned",
    ),
    "first-wave": (
        "public_vulnerable_migrated",
        "jwt_signing_migrated",
        "rollback_drill_completed",
    ),
    "broad-rollout": (
        "remaining_vulnerable_migrated",
        "composite_client_adoption_above_threshold",
        "work_stream_reports_green",
    ),
    "end-of-migration": (
        "classical_retired",
        "pq_only_mode",
        "post_migration_review_signed",
    ),
}


@dataclass(frozen=True)
class PhaseGateResult:
    """Result of a phase-gate check."""

    phase: str
    passed: bool
    met: tuple[str, ...]
    missing: tuple[str, ...]


def check(phase_name: str, gate_record: Mapping[str, object]) -> PhaseGateResult:
    """Validate ``gate_record`` against ``phase_name``'s exit criteria.

    Returns a ``PhaseGateResult``. Raises ``ValueError`` if
    ``phase_name`` is not one of the four defined phases.
    """
    # EXERCISE: implement this function.
    #
    # PHASE_EXIT_CRITERIA already holds the four phases and each one's
    # ordered criteria. Reject a phase name that is not in it with
    # ValueError rather than returning a vacuous pass over an empty
    # criterion list. Then split the phase's criteria into met and missing
    # by testing whether gate_record.get(c) is True. Only the literal True
    # counts as met: a missing key, False, the string 'yes', and the integer
    # 1 are all unmet, because 'probably done' is not done. Walk the
    # criteria in the order PHASE_EXIT_CRITERIA declares rather than the
    # order the record happens to carry, so a runbook can step through the
    # gaps in sequence. The gate passes exactly when nothing is missing.
    #
    # Reference: Chapter 30, 'First-wave deployment (2028-2031)'
    #
    # Proved by:
    #   tests/ch30/test_phase_gate.py
    raise NotImplementedError("exercise: check")
