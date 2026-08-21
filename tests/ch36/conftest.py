"""Pytest conftest for the Chapter 36 test suite.

Adds the selected tree's ``ch36-blockchain-threat-model/src`` to ``sys.path`` so the
``blockchain_threat`` package imports without a ``pip install -e``.

Provides shared fixtures:

- ``strand_assets``: the five-surface fixture for the chapter's running
  example (transaction, consensus, wallet, on-chain verifier,
  governance). Each surface deploys the dominant blockchain primitive
  in 2026 (ECDSA-secp256k1, BLS-BLS12-381, BIP-32 HD wallet over
  ECDSA-secp256k1, SHA-256 inside a STARK verifier, Schnorr-secp256k1
  threshold).
- ``mosca_z_values``: three Z values matching the chapter's three
  planning scenarios (NCSC 2035 migration horizon, NSM-10 2035 NSS
  quantum-resistant goal, hypothetical mid-2040 scenario). These
  are policy planning deadlines and a hypothetical, not predicted
  CRQC arrival dates.
- ``strand_xy``: per-surface (X, Y) tuples for the five Strand
  surfaces, used to drive Mosca calculations across the fixture
  distributions.
"""

import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
PACKAGE_SRC = REPO_ROOT / IMPL / "ch36-blockchain-threat-model" / "src"

entry_str = str(PACKAGE_SRC)
if entry_str not in sys.path:
    sys.path.insert(0, entry_str)


@pytest.fixture
def strand_assets() -> list[dict[str, object]]:
    """The fictional Strand chain at chain-tip in 2026: five surfaces.

    Each record carries the four fields the chapter's surface taxonomy
    threads through Ch 37 to Ch 41. ``primitive`` is the deployed
    primitive in 2026; ``exposure`` flags whether the public key
    sits on a public ledger; ``lifecycle`` names the cadence at
    which the surface rotates or migrates.
    """
    return [
        {
            "surface": "transaction",
            "primitive": "ECDSA-secp256k1",
            "exposure": "public",
            "lifecycle": "per-spend",
        },
        {
            "surface": "consensus",
            "primitive": "BLS-BLS12-381",
            "exposure": "public",
            "lifecycle": "per-slot",
        },
        {
            "surface": "wallet",
            "primitive": "ECDSA-secp256k1",
            "exposure": "internal",
            "lifecycle": "per-address",
        },
        {
            "surface": "on-chain-verifier",
            "primitive": "SHA-256",
            "exposure": "public",
            "lifecycle": "per-proof",
        },
        {
            "surface": "governance",
            "primitive": "Schnorr-secp256k1",
            "exposure": "public",
            "lifecycle": "per-vote",
        },
    ]


@pytest.fixture
def mosca_z_values() -> dict[str, int]:
    """Three Z planning scenarios used in the chapter's running example.

    Z is the number of years from 2026 used as a planning stress-test
    value, not as a predicted CRQC arrival date. ``ncsc_2035`` is the
    NCSC 2035 migration horizon (deadline for completing PQC
    migration, not a CRQC forecast); ``nsm10_2035`` is the NSM-10 /
    CNSA 2.0 2035 NSS quantum-resistant goal (policy goal for
    National Security Systems, not a CRQC forecast); ``mid_2040`` is
    a hypothetical mid-arrival scenario the chapter uses for the
    deferred surfaces.
    """
    return {
        "ncsc_2035": 9,
        "nsm10_2035": 9,
        "mid_2040": 14,
    }


@pytest.fixture
def strand_xy() -> dict[str, tuple[int, int]]:
    """Per-surface (X, Y) pairs for Mosca's inequality.

    X is the data-lifetime horizon in years; Y is the migration time.
    The transaction surface sits at the public-ledger archival
    horizon (effectively unbounded; the fixture uses 50 years as a
    practical cap). The consensus surface sits at the validator-set
    rotation cadence. The on-chain verifier sits at the proof-system
    upgrade cadence. The governance surface sits at the multisig
    rotation cadence.
    """
    return {
        "transaction": (50, 5),
        "consensus": (2, 1),
        "wallet": (10, 4),
        "on-chain-verifier": (3, 2),
        "governance": (4, 3),
    }
