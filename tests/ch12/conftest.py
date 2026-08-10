"""Pytest conftest for the Chapter 12 test suite.

Adds the selected tree's ``ch12-mldsa/src`` to ``sys.path`` so the ``mldsa``
package can be imported without a ``pip install -e``. Matches the pattern set
by ``tests/ch11/conftest.py`` (and the ch08-ch11 template it follows): the
``PQC_IMPL`` env var switches between the ``solutions`` reference tree and the
``exercises`` stub tree; it defaults to ``solutions``.
"""

import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
PACKAGE_SRC = REPO_ROOT / IMPL / "ch12-mldsa" / "src"

if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))
