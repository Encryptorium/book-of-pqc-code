"""Pytest conftest for the Chapter 10 test suite.

Adds the selected tree's ``ch10-regev-pke/src`` to ``sys.path`` so the ``regev_pke``
package can be imported without a ``pip install -e``.

The chapter's parameter sets are fixtures rather than module-level constants.
``RegevParams.__post_init__`` is one of the functions the exercise manifest
stubs, so constructing a parameter set at import time raises
``NotImplementedError`` during collection, and pytest abandons the whole run
instead of reporting the red list Appendix C promises. A fixture defers
construction to the test body, where the stub hit is one reported failure like
any other.
"""

import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL = os.environ.get("PQC_IMPL", "solutions")
if IMPL not in ("solutions", "exercises"):
    raise SystemExit(f"PQC_IMPL must be 'solutions' or 'exercises', got {IMPL!r}")
PACKAGE_SRC = REPO_ROOT / IMPL / "ch10-regev-pke" / "src"

if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from regev_pke import RegevParams  # noqa: E402  (needs PACKAGE_SRC on sys.path first)


@pytest.fixture
def toy() -> RegevParams:
    """The chapter's worked parameter set: n = 4, q = 97, m = 8, B = 1."""
    return RegevParams(n=4, q=97, m=8, noise_bound=1)


@pytest.fixture
def feasible() -> RegevParams:
    """The worked set again, named for what the noise-budget tests assert: 2*m*B < q//2."""
    return RegevParams(n=4, q=97, m=8, noise_bound=1)


@pytest.fixture
def infeasible() -> RegevParams:
    """q = 13 puts the decoding threshold at 3.0 against a worst-case noise of 8."""
    return RegevParams(n=4, q=13, m=8, noise_bound=1)
