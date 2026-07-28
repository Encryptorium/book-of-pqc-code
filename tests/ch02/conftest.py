"""Pytest conftest for the Chapter 2 test suite.

Adds the selected tree's ``ch02-algebra/src`` to ``sys.path`` so the
``prelim_algebra`` package imports without a ``pip install -e``.

Provides one shared fixture:

- ``small_primes``: the primes Chapter 2 and its Appendix D page actually
  compute with, so a test that wants "some prime" uses one the book prints
  rather than inventing a new one.
"""

import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
PACKAGE_SRC = REPO_ROOT / IMPL / "ch02-algebra" / "src"

entry_str = str(PACKAGE_SRC)
if entry_str not in sys.path:
    sys.path.insert(0, entry_str)


@pytest.fixture
def small_primes() -> list[int]:
    """The primes the chapter computes with, plus 2 for the degenerate edge.

    13 is the opening Fermat example, 17 is exercise 2's generator search, 7 is
    exercise 3's root search and the exercise 4 matrix modulus, 5 is the
    polynomial-multiplication example, and 43 is the modulus of the inverse
    example.
    """
    return [2, 3, 5, 7, 13, 17, 43]
