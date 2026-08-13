"""Chapter 30: operator tooling for a multi-year PQ migration program.

Three utilities:

- ``risk_rollup``: rank-order the touchpoints in a CBOM by quantum
  migration urgency, combining the Ch 25 quantum-status and exposure
  axes with a PQRA-style weighted readiness score.
- ``phase_gate``: validate whether a named program phase's exit criteria
  are met against a fixture gate record, and return a structured
  pass/fail with a reason list.
- ``milestone_tracker``: read a dated milestone list and a current date,
  and report percentage complete and a slipped-milestone list.

The package is stdlib-only. No cryptographic code lives here; Ch 30 does
not re-derive any primitive. The rollup inputs are the Ch 25 CBOM
records, the PQRA weights are the Encryptorium Post-Quantum Readiness
Assessment domains, and the phase definitions follow the NCSC 2025 and
CNSA 2.0 timeline anchors.
"""

from .risk_rollup import (
    QUANTUM_MULT,
    EXPOSURE_MULT,
    PQRA_DOMAINS,
    DEFAULT_PQRA_WEIGHTS,
    migration_urgency,
)
from .phase_gate import (
    PHASE_EXIT_CRITERIA,
    PhaseGateResult,
    check,
)
from .milestone_tracker import (
    Milestone,
    MilestoneReport,
    report,
)

__all__ = [
    "QUANTUM_MULT",
    "EXPOSURE_MULT",
    "PQRA_DOMAINS",
    "DEFAULT_PQRA_WEIGHTS",
    "migration_urgency",
    "PHASE_EXIT_CRITERIA",
    "PhaseGateResult",
    "check",
    "Milestone",
    "MilestoneReport",
    "report",
]
