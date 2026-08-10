"""Pytest conftest for the Chapter 15 test suite.

Adds the selected tree's ``ch15-xmss/src`` to ``sys.path`` so the ``wots_xmss``
package can be imported without a ``pip install -e``.  Matches the pattern
set by ``tests/ch14/conftest.py``.
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
PACKAGE_SRC = REPO_ROOT / IMPL / "ch15-xmss" / "src"

if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))
