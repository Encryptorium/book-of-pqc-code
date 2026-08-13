"""Pytest conftest for the Chapter 40 test suite.

Adds the selected tree's ``ch40-zk-rollups/src`` to ``sys.path`` so the
``zk_rollups`` package imports without a ``pip install -e``.

Provides shared fixtures:

- ``layers``: the four-element list of verifier-contract layer names
  (L1-arithmetization, L2-commitment, L3-protocol-logic,
  L4-fiat-shamir) per Ch 31.
- ``l2_commitment_candidates``: the four-element candidate set for
  the L2 commitment layer (KZG, FRI, Merkle, lattice-PCS).
- ``l4_fiat_shamir_candidates``: the four-element candidate set for
  the L4 Fiat-Shamir hash layer (SHA-256, SHAKE-128, SHAKE-256,
  Keccak-256).
- ``configurations``: the three-element list of verifier
  configurations the gas-budget module compares (legacy-sha256-
  stark, wider-hash-stark, recursive-stark-wrapper).
- ``strand_verifier_xy``: the (X=3, Y=2) anchor for the Strand
  on-chain-verifier surface, mirroring the tests/ch36/conftest.py
  on-chain-verifier row.
- ``mosca_z_scenarios``: three Z scenarios (narrow=4, central=9,
  wide=13) spanning the every-N-rollup-cycles cadence regime
  (narrow) and the governance-trigger regime (central, wide). The
  vocabulary deliberately avoids collision with any pq-status or
  deployment-status cell value in verifier_layers.
"""

import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
PACKAGE_SRC = REPO_ROOT / IMPL / "ch40-zk-rollups" / "src"

entry_str = str(PACKAGE_SRC)
if entry_str not in sys.path:
    sys.path.insert(0, entry_str)


@pytest.fixture
def layers() -> list[str]:
    """The four-element layer name list per Ch 31."""
    return [
        "L1-arithmetization",
        "L2-commitment",
        "L3-protocol-logic",
        "L4-fiat-shamir",
    ]


@pytest.fixture
def l2_commitment_candidates() -> list[str]:
    """The four-element candidate set for the L2 commitment layer."""
    return ["KZG", "FRI", "Merkle", "lattice-PCS"]


@pytest.fixture
def l4_fiat_shamir_candidates() -> list[str]:
    """The four-element candidate set for the L4 Fiat-Shamir layer."""
    return ["SHA-256", "SHAKE-128", "SHAKE-256", "Keccak-256"]


@pytest.fixture
def configurations() -> list[str]:
    """The three-element verifier-configuration list for gas_budget."""
    return [
        "legacy-sha256-stark",
        "wider-hash-stark",
        "recursive-stark-wrapper",
    ]


@pytest.fixture
def strand_verifier_xy() -> tuple[int, int]:
    """The (X=3, Y=2) on-chain-verifier-surface anchor from the Ch 36 fixture."""
    return (3, 2)


@pytest.fixture
def mosca_z_scenarios() -> dict[str, int]:
    """Three Z scenarios spanning two cadence regimes.

    - ``narrow`` (Z=4): forces every-N-rollup-cycles (breach by one
      year; safe window two years).
    - ``central`` (Z=9): clears; recommendation is governance-trigger.
    - ``wide`` (Z=13): clears; recommendation is governance-trigger.
    """
    return {
        "narrow": 4,
        "central": 9,
        "wide": 13,
    }
