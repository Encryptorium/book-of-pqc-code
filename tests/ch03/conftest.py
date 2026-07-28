"""Pytest conftest for the Chapter 3 test suite.

Adds the selected tree's ``ch03-hard-problems/src`` to ``sys.path`` so the
``hard_problems`` package imports without a ``pip install -e``.

Provides one shared fixture:

- ``chapter_basis``: the basis Chapter 3 draws, ``((2, 7), (5, 3))``, as rows,
  matching the matrix ``B`` in the chapter's first exercise.
"""

import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
PACKAGE_SRC = REPO_ROOT / IMPL / "ch03-hard-problems" / "src"

entry_str = str(PACKAGE_SRC)
if entry_str not in sys.path:
    sys.path.insert(0, entry_str)


@pytest.fixture
def chapter_basis() -> tuple[tuple[int, int], tuple[int, int]]:
    """The chapter's basis as rows: b1 = (2, 7), b2 = (5, 3), det -29."""
    return ((2, 7), (5, 3))
