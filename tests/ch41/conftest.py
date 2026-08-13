"""Pytest conftest for the Chapter 41 test suite.

Adds the selected tree's ``ch41-governance/src`` to ``sys.path`` so the
``governance`` package imports without a ``pip install -e``.

Provides shared fixtures:

- ``stakeholders``: the three-element list of stakeholder names
  (protocol-developer, validator-operator,
  infrastructure-service-provider), this chapter's own taxonomy.
- ``actions``: the three-element list of hard-fork actions (propose,
  audit, deploy).
- ``cycles``: the two-element list of named hard-fork coordination
  cycles (bitcoin-bip-cycle, ethereum-acd-cycle).
- ``strand_governance_xy``: the (X=4, Y=3) anchor for the Strand
  governance surface, mirroring the tests/ch36/conftest.py governance
  row.
- ``mosca_z_scenarios``: three Z scenarios (narrow=6, central=9,
  wide=13) spanning the every-N-vote-cycles cadence regime
  (narrow) and the governance-trigger regime (central, wide). The
  vocabulary deliberately avoids collision with any pq-status or
  coordination-role cell value in stakeholder_matrix.
"""

import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
PACKAGE_SRC = REPO_ROOT / IMPL / "ch41-governance" / "src"

entry_str = str(PACKAGE_SRC)
if entry_str not in sys.path:
    sys.path.insert(0, entry_str)


@pytest.fixture
def stakeholders() -> list[str]:
    """The three-element stakeholder list, this chapter's own taxonomy."""
    return [
        "protocol-developer",
        "validator-operator",
        "infrastructure-service-provider",
    ]


@pytest.fixture
def actions() -> list[str]:
    """The three-element hard-fork action list."""
    return ["propose", "audit", "deploy"]


@pytest.fixture
def cycles() -> list[str]:
    """The two-element named-cycle list for fork_choreography."""
    return ["bitcoin-bip-cycle", "ethereum-acd-cycle"]


@pytest.fixture
def strand_governance_xy() -> tuple[int, int]:
    """The (X=4, Y=3) governance-surface anchor from the Ch 36 fixture."""
    return (4, 3)


@pytest.fixture
def mosca_z_scenarios() -> dict[str, int]:
    """Three Z scenarios spanning two cadence regimes.

    - ``narrow`` (Z=6): forces every-N-vote-cycles (breach by one
      year; safe window three years).
    - ``central`` (Z=9): clears; recommendation is governance-trigger.
    - ``wide`` (Z=13): clears; recommendation is governance-trigger.
    """
    return {
        "narrow": 6,
        "central": 9,
        "wide": 13,
    }
