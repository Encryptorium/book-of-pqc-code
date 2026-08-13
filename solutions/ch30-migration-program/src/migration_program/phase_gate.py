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
    if phase_name not in PHASE_EXIT_CRITERIA:
        raise ValueError(
            f"unknown phase: {phase_name!r}. "
            f"expected one of {tuple(PHASE_EXIT_CRITERIA)}"
        )
    criteria = PHASE_EXIT_CRITERIA[phase_name]
    met = tuple(c for c in criteria if gate_record.get(c) is True)
    missing = tuple(c for c in criteria if gate_record.get(c) is not True)
    return PhaseGateResult(
        phase=phase_name,
        passed=(len(missing) == 0),
        met=met,
        missing=missing,
    )
