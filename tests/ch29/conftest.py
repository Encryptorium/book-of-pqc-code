"""Pytest conftest for the Chapter 29 test suite.

Adds the selected tree's ``ch29-pki/src``, ``ch27-hybrid/src``, and
``ch15-xmss/src`` to ``sys.path`` so the ``pki_migration``,
``hybrid``, and ``wots_xmss`` packages can be imported without a
``pip install -e``.
"""

import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
PKI_SRC = REPO_ROOT / IMPL / "ch29-pki" / "src"
HYBRID_SRC = REPO_ROOT / IMPL / "ch27-hybrid" / "src"
XMSS_SRC = REPO_ROOT / IMPL / "ch15-xmss" / "src"

for entry in (PKI_SRC, HYBRID_SRC, XMSS_SRC):
    entry_str = str(entry)
    if entry_str not in sys.path:
        sys.path.insert(0, entry_str)
