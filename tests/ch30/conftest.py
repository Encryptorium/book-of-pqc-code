"""Pytest conftest for the Chapter 30 test suite.

Adds the selected tree's ``ch30-migration-program/src`` to ``sys.path`` so the
``migration_program`` package imports without a ``pip install -e``.

Provides a few shared fixtures used across the three test modules:

- ``four_touchpoint_cbom``: the Ch 25 running example with the per
  touchpoint PQRA readiness scores Ch 30 uses for the priority rollup.
- ``discovery_gate_record`` / ``first_wave_gate_record``: fixture gate
  records for the phase-gate checker.
- ``program_milestones``: a dated milestone list with a mix of
  completed, future, and slipped entries.
"""

import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
MIGRATION_SRC = REPO_ROOT / IMPL / "ch30-migration-program" / "src"

entry_str = str(MIGRATION_SRC)
if entry_str not in sys.path:
    sys.path.insert(0, entry_str)


@pytest.fixture
def four_touchpoint_cbom() -> list[dict]:
    """Four of the five Ch 25 touchpoints, with PQRA readiness scores.

    Omits ``blockchain_validator_sig``, the fifth and only still-vulnerable
    entry, so that this fixture exercises the already-migrated and
    grover-only paths on their own.

    tls_endpoint_api was migrated in Ch 28 so it is quantum-safe.
    jwt_signing was migrated in Ch 29 so it is quantum-safe.
    password_hashing and webhook_hmac remain grover-only.

    In the rollup the two migrated touchpoints score zero; the two
    remaining entries score small but nonzero values because they are
    grover-only. A realistic scenario where the rollup produces the
    full ordering adds one still-vulnerable touchpoint (see
    ``second_wave_cbom`` below).
    """
    return [
        {
            "name": "tls_endpoint_api",
            "quantum_status": "quantum-safe",
            "exposure": "public",
            "readiness": {
                "inventory": 5,
                "data_sensitivity": 5,
                "standards_compliance": 5,
                "migration_readiness": 5,
                "vendor_supply_chain": 5,
                "timeline_urgency": 5,
                "governance_policy": 5,
            },
        },
        {
            "name": "jwt_signing",
            "quantum_status": "quantum-safe",
            "exposure": "internal",
            "readiness": {
                "inventory": 5,
                "data_sensitivity": 5,
                "standards_compliance": 5,
                "migration_readiness": 5,
                "vendor_supply_chain": 5,
                "timeline_urgency": 5,
                "governance_policy": 5,
            },
        },
        {
            "name": "password_hashing",
            "quantum_status": "grover-only",
            "exposure": "internal",
            "readiness": {
                "inventory": 4,
                "data_sensitivity": 2,
                "standards_compliance": 4,
                "migration_readiness": 3,
                "vendor_supply_chain": 4,
                "timeline_urgency": 3,
                "governance_policy": 4,
            },
        },
        {
            "name": "webhook_hmac",
            "quantum_status": "grover-only",
            "exposure": "internal",
            "readiness": {
                "inventory": 4,
                "data_sensitivity": 3,
                "standards_compliance": 4,
                "migration_readiness": 4,
                "vendor_supply_chain": 4,
                "timeline_urgency": 4,
                "governance_policy": 4,
            },
        },
    ]


@pytest.fixture
def second_wave_cbom() -> list[dict]:
    """A CBOM with one still-vulnerable entry to exercise the full rollup.

    The two migrated touchpoints (TLS, JWT) sit alongside a third,
    still-vulnerable public-facing touchpoint to produce a non-trivial
    priority ordering.
    """
    return [
        {
            "name": "tls_endpoint_api",
            "quantum_status": "quantum-safe",
            "exposure": "public",
            "readiness": {d: 5 for d in (
                "inventory", "data_sensitivity", "standards_compliance",
                "migration_readiness", "vendor_supply_chain",
                "timeline_urgency", "governance_policy",
            )},
        },
        {
            "name": "legacy_api_gateway",
            "quantum_status": "vulnerable",
            "exposure": "public",
            "readiness": {
                "inventory": 3,
                "data_sensitivity": 2,
                "standards_compliance": 2,
                "migration_readiness": 1,
                "vendor_supply_chain": 2,
                "timeline_urgency": 1,
                "governance_policy": 3,
            },
        },
        {
            "name": "webhook_hmac",
            "quantum_status": "grover-only",
            "exposure": "internal",
            "readiness": {
                "inventory": 4,
                "data_sensitivity": 3,
                "standards_compliance": 4,
                "migration_readiness": 4,
                "vendor_supply_chain": 4,
                "timeline_urgency": 4,
                "governance_policy": 4,
            },
        },
    ]


@pytest.fixture
def discovery_gate_record() -> dict:
    return {
        "cbom_complete": True,
        "pqra_scored": True,
        "owners_assigned": True,
    }


@pytest.fixture
def first_wave_gate_record() -> dict:
    return {
        "public_vulnerable_migrated": True,
        "jwt_signing_migrated": True,
        "rollback_drill_completed": False,
    }


@pytest.fixture
def program_milestones() -> list:
    """A four-milestone mix: two completed (cbom_complete, pqra_scored),
    one future incomplete (public_vulnerable_migrated), one slipped
    (owners_assigned, past target, not complete at the 2026-04-17
    reporting date)."""
    from migration_program import Milestone

    return [
        Milestone(name="cbom_complete", target_date="2026-12-31", completed=True),
        Milestone(name="pqra_scored", target_date="2027-06-30", completed=True),
        Milestone(name="public_vulnerable_migrated", target_date="2028-12-31", completed=False),
        Milestone(name="owners_assigned", target_date="2025-12-31", completed=False),
    ]
