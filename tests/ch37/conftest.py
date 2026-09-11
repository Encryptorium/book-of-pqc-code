"""Pytest conftest for the Chapter 37 test suite.

Adds the selected tree's ``ch37-l1-signature-migration/src`` to ``sys.path`` so the
``l1_migration`` package imports without a ``pip install -e``.

Provides shared fixtures:

- ``candidate_set``: the four-element list of candidate primitive
  names locked in the chapter's planning notes.
- ``budget_anchors``: a dict carrying the Bitcoin weight limit and
  the Ethereum Fusaka-era client-default gas-limit scenario so a test can assert against
  the exact constants the chapter pins.
"""

import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
PACKAGE_SRC = REPO_ROOT / IMPL / "ch37-l1-signature-migration" / "src"

entry_str = str(PACKAGE_SRC)
if entry_str not in sys.path:
    sys.path.insert(0, entry_str)


@pytest.fixture
def candidate_set() -> list[str]:
    """The fixed four-element candidate set for the Strand transaction surface."""
    return [
        "classical-secp256k1",
        "ML-DSA-65",
        "SLH-DSA-128s",
        "Ed25519+ML-DSA-65",
    ]


@pytest.fixture
def budget_anchors() -> dict[str, int]:
    """The two block-budget anchors locked in the chapter's planning notes.

    Bitcoin uses the 4,000,000 weight-unit limit, which is weight units
    and not four million raw serialized bytes. Ethereum uses the
    chain-tip 2026 60-million gas scenario, which is the execution-client
    default EIP-7935 recommends in the Fusaka cycle rather than a
    consensus constant. Tests assert against these
    directly so a revision must edit one place rather than every
    figure.
    """
    return {
        "btc_weight_limit": 4_000_000,
        "eth_gas_limit_fusaka": 60_000_000,
    }
