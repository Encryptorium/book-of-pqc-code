"""Chapter 36: a small toolkit for the blockchain threat model.

Two utilities:

- ``surface_taxonomy``: classify a blockchain signature primitive by
  quantum vulnerability (``"shor-vulnerable"``,
  ``"hash-quantum-degraded"``, or ``"post-quantum-standardized"``).
- ``mosca_window``: given Mosca's three parameters ``X`` (data
  lifetime, in years), ``Y`` (migration time), and ``Z`` (years until
  a cryptographically relevant quantum computer), report the exposure
  window in years.

The package is stdlib-only. No cryptographic code lives here; Ch 36
does not re-derive any primitive. The classifier carries the
classification table the chapter walks, and the Mosca calculator
carries the inequality the chapter restates from Ch 01.
"""

from .surface_taxonomy import (
    PRIMITIVE_CLASSIFICATION,
    classify,
    classify_all,
)
from .mosca_window import evaluate

__all__ = [
    "PRIMITIVE_CLASSIFICATION",
    "classify",
    "classify_all",
    "evaluate",
]
