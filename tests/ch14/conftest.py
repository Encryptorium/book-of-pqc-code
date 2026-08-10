"""Pytest conftest for the Chapter 14 test suite.

Adds the selected tree's ``ch14-lamport/src`` to ``sys.path`` so the ``lamport_merkle``
package can be imported without a ``pip install -e``.  Matches the pattern
set by ``tests/ch11/conftest.py`` and ``tests/ch13/conftest.py``.
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
PACKAGE_SRC = REPO_ROOT / IMPL / "ch14-lamport" / "src"

if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))
