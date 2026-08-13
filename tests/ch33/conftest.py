"""Pytest conftest for the Chapter 33 test suite.

Adds the selected tree's ``ch33-fiat-shamir-qrom/src`` to ``sys.path`` so the
``fiat_shamir_qrom`` package imports without a ``pip install -e``.
"""

import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
FSQROM_SRC = REPO_ROOT / IMPL / "ch33-fiat-shamir-qrom" / "src"

entry_str = str(FSQROM_SRC)
if entry_str not in sys.path:
    sys.path.insert(0, entry_str)
