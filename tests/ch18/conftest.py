"""Pytest conftest for the Chapter 18 test suite.

Adds the selected tree's ``ch18-hash-cryptanalysis/src`` to ``sys.path`` so the
``hash_cryptanalysis`` package imports without a ``pip install -e``.

``PQC_IMPL=exercises`` switches the suite from ``solutions/`` to the generated
stub tree, exactly as in every other chapter.

Provides two shared fixtures:

- ``sha2_sets``: the six FIPS 205 SHA-2 parameter sets, in the standard's order.
- ``fips205_table_2``: the Table 2 columns Chapter 18 depends on, frozen as
  literals so a transcription error in ``params.py`` fails here rather than
  propagating into every computed result. The full twelve-row table, including
  the digest length ``m`` and the public-key sizes, is pinned in
  ``tests/ch17/test_vectors.py``; this is the subset Chapter 18 uses.
"""

import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
PACKAGE_SRC = REPO_ROOT / IMPL / "ch18-hash-cryptanalysis" / "src"

entry_str = str(PACKAGE_SRC)
if entry_str not in sys.path:
    sys.path.insert(0, entry_str)


#: FIPS 205 Table 2, the columns Chapter 18 uses: h_prime, category, sig_bytes.
TABLE_2 = {
    "128s": (9, 1, 7_856),
    "128f": (3, 1, 17_088),
    "192s": (9, 3, 16_224),
    "192f": (3, 3, 35_664),
    "256s": (8, 5, 29_792),
    "256f": (4, 5, 49_856),
}


@pytest.fixture
def sha2_sets():
    """The six SHA-2 parameter sets, in FIPS 205 Table 2 order."""
    from hash_cryptanalysis.params import SHA2_PARAMETER_SETS

    return SHA2_PARAMETER_SETS


@pytest.fixture
def fips205_table_2():
    """Frozen Table 2 columns keyed by short name: (h_prime, category, sig_bytes)."""
    return TABLE_2
