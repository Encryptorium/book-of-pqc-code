"""Pytest conftest for the Chapter 1 test suite.

Adds the selected tree's ``ch01-quantum-threat/src`` to ``sys.path`` so the
``quantum_threat`` package imports without a ``pip install -e``.

Provides one shared fixture:

- ``semiprimes``: (n, p, q) triples with p <= q, both prime. The chapter's
  own modulus 3233 = 53 x 61 is in the list, alongside a smaller pair, a
  square of a prime, and a pair large enough that the count is not the
  smaller factor by coincidence.
"""

import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
PACKAGE_SRC = REPO_ROOT / IMPL / "ch01-quantum-threat" / "src"

entry_str = str(PACKAGE_SRC)
if entry_str not in sys.path:
    sys.path.insert(0, entry_str)


@pytest.fixture
def semiprimes() -> list[tuple[int, int, int]]:
    """(n, p, q) with n = p * q, p <= q, both prime.

    3233 = 53 x 61 is the chapter's modulus and the one exercise 2 asks the
    reader to confirm a division count for. 9409 = 97 x 97 covers the case
    where the two factors are equal, which is where the loop's stopping
    condition is tightest.
    """
    return [
        (15, 3, 5),
        (21, 3, 7),
        (1147, 31, 37),
        (3233, 53, 61),
        (9409, 97, 97),
    ]
