"""Pytest conftest for the Chapter 31 test suite.

Adds the selected tree's ``ch31-zk-layers/src`` to ``sys.path`` so the
``zk_layers`` package imports without a ``pip install -e``.
"""

import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
ZK_LAYERS_SRC = REPO_ROOT / IMPL / "ch31-zk-layers" / "src"

entry_str = str(ZK_LAYERS_SRC)
if entry_str not in sys.path:
    sys.path.insert(0, entry_str)
