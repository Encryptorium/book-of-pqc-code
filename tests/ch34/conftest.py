"""Pytest conftest for the Chapter 34 test suite.

Adds the selected tree's ``ch34-starks/src`` to ``sys.path`` so the ``starks`` package
imports without a ``pip install -e``.
"""

import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
STARKS_SRC = REPO_ROOT / IMPL / "ch34-starks" / "src"

entry_str = str(STARKS_SRC)
if entry_str not in sys.path:
    sys.path.insert(0, entry_str)
