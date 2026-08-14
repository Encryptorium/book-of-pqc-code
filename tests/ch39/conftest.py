"""Pytest conftest for the Chapter 39 test suite.

Adds the selected tree's ``ch39-consensus-staking/src`` to ``sys.path`` so the
``consensus_staking`` package imports without a ``pip install -e``.

Provides shared fixtures:

- ``primitives``: the five-element list of candidate primitives for
  the consensus matrix (BLS legacy plus four post-quantum candidates).
- ``threshold_roles``: the three-element list of threshold-protocol
  roles (no-threshold, classical-FROST, threshold-PQ).
- ``strand_consensus_xy``: the (X=2, Y=1) anchor for the Strand
  consensus surface, mirroring the tests/ch36/conftest.py consensus
  row.
- ``mosca_z_values``: four Z scenarios spanning aggressive (Z=0;
  CRQC arrives sooner than the migration window), narrow (Z=2;
  hypothetical breach), NCSC working assumption (Z=9), and
  mid-2040 (Z=14).
- ``validator_count_scenarios``: three illustrative N values for the
  per-block byte-budget arithmetic.
"""

import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
PACKAGE_SRC = REPO_ROOT / IMPL / "ch39-consensus-staking" / "src"

entry_str = str(PACKAGE_SRC)
if entry_str not in sys.path:
    sys.path.insert(0, entry_str)


@pytest.fixture
def primitives() -> list[str]:
    """The fixed five-element candidate set for the consensus matrix."""
    return [
        "BLS-BLS12-381",
        "ML-DSA-65",
        "SLH-DSA-128s",
        "FN-DSA-512",
        "threshold-ML-DSA",
    ]


@pytest.fixture
def threshold_roles() -> list[str]:
    """The fixed three-element threshold-protocol role list."""
    return [
        "no-threshold",
        "classical-FROST",
        "threshold-PQ",
    ]


@pytest.fixture
def strand_consensus_xy() -> tuple[int, int]:
    """The (X=2, Y=1) consensus-surface anchor from the Ch 36 fixture."""
    return (2, 1)


@pytest.fixture
def mosca_z_values() -> dict[str, int]:
    """Four Z scenarios spanning the three rotation-cadence regimes.

    The Strand consensus surface (X=2, Y=1) clears the Mosca window
    under both ``ncsc_2035`` (Z=9) and ``mid_2040`` (Z=14); the
    chapter introduces a hypothetical ``narrow`` (Z=2) to
    illustrate the every-N-epochs cadence regime, since the
    canonical Ch 36 Z values do not breach the consensus surface.

    - ``aggressive`` (Z=0): forces hard-fork-trigger (no positive
      safe window).
    - ``narrow`` (Z=2): forces every-N-epochs at N=1 (breach by
      one year; safe window one year).
    - ``ncsc_2035`` (Z=9): clears; recommendation is per-epoch.
    - ``mid_2040`` (Z=14): clears; recommendation is per-epoch.
    """
    return {
        "aggressive": 0,
        "narrow": 2,
        "ncsc_2035": 9,
        "mid_2040": 14,
    }


@pytest.fixture
def validator_count_scenarios() -> dict[str, int]:
    """Three validator-count scenarios for the per-set byte budget.

    ``small_chain`` is a smaller PoS chain (10K validators).
    ``ethereum_mainnet`` is a one-million-validator normalisation at
    mainnet scale, not a chain-tip count. ``hypothetical_large`` is
    a forward-looking scenario for stress-testing the byte budget.
    """
    return {
        "small_chain": 10_000,
        "ethereum_mainnet": 1_000_000,
        "hypothetical_large": 10_000_000,
    }
