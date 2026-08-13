"""Pytest conftest for the Chapter 35 test suite.

Adds the selected tree's ``ch35-case-studies/src`` to ``sys.path`` so the
``zk_case_studies`` package imports without a ``pip install -e``.
"""

import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
CASE_STUDIES_SRC = REPO_ROOT / IMPL / "ch35-case-studies" / "src"

entry_str = str(CASE_STUDIES_SRC)
if entry_str not in sys.path:
    sys.path.insert(0, entry_str)
