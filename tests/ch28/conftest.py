"""Pytest conftest for the Chapter 28 test suite.

Adds the selected tree's ``ch28-tls-migration/src`` to ``sys.path`` so the
``tls_migration`` package can be imported without a ``pip install -e``.
"""

import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
TLS_MIGRATION_SRC = REPO_ROOT / IMPL / "ch28-tls-migration" / "src"

entry_str = str(TLS_MIGRATION_SRC)
if entry_str not in sys.path:
    sys.path.insert(0, entry_str)
