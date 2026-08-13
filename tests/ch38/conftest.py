"""Pytest conftest for the Chapter 38 test suite.

Adds the selected tree's ``ch38-wallets-addresses-key-rotation/src`` to ``sys.path``
so the ``wallet_rotation`` package imports without a ``pip install -e``.

Provides shared fixtures:

- ``custody_shapes``: the four-element list of custody-shape names
  locked in the chapter's planning notes.
- ``primitives``: the six-element list of candidate primitives for
  the wallet matrix (the four from Ch 37 plus XMSS-MT and LMS).
- ``strand_wallet_xy``: the (X=10, Y=4) anchor for the Strand wallet
  surface, mirroring the tests/ch36/conftest.py wallet row.
- ``mosca_z_values``: three Z scenarios spanning aggressive (Z=4),
  NCSC working assumption (Z=9), and mid-2040 (Z=14).
"""

import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
PACKAGE_SRC = REPO_ROOT / IMPL / "ch38-wallets-addresses-key-rotation" / "src"

entry_str = str(PACKAGE_SRC)
if entry_str not in sys.path:
    sys.path.insert(0, entry_str)


@pytest.fixture
def custody_shapes() -> list[str]:
    """The fixed four-element custody-shape taxonomy from the planning notes."""
    return [
        "single-device-hot",
        "multi-device-hot",
        "hardware-only-cold",
        "multisig-cold",
    ]


@pytest.fixture
def primitives() -> list[str]:
    """The fixed six-element candidate set for the wallet matrix."""
    return [
        "ECDSA-secp256k1",
        "ML-DSA-65",
        "SLH-DSA-128s",
        "Ed25519+ML-DSA-65",
        "XMSS-MT",
        "LMS",
    ]


@pytest.fixture
def strand_wallet_xy() -> tuple[int, int]:
    """The (X=10, Y=4) wallet-surface anchor from the Ch 36 fixture."""
    return (10, 4)


@pytest.fixture
def mosca_z_values() -> dict[str, int]:
    """Three Z scenarios spanning aggressive, working assumption, and mid-2040.

    ``aggressive`` puts a CRQC closer than the wallet's full migration
    window. ``ncsc_2035`` mirrors the tests/ch36/conftest.py NCSC
    working assumption (Z = 9 years from chain-tip 2026 to 2035).
    ``mid_2040`` puts the arrival horizon past the wallet's seed
    lifetime plus migration time (Z = 14, the boundary case).
    """
    return {
        "aggressive": 4,
        "ncsc_2035": 9,
        "mid_2040": 14,
    }
