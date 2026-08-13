"""Chapter 33: classical pedagogical scaffolding for Fiat-Shamir in the QROM.

Three modules, one per component analyzed at L4 of the four-layer
decomposition (Chapter 31):

- ``rom_simulator``: lazy-sampling classical random oracle with an
  explicit reprogramming invariant (cannot reprogram an already-queried
  input). Models the classical side of the measure-and-reprogram
  reduction.
- ``fiat_shamir``: Schnorr three-move sigma protocol over the
  ``(p=2027, n=1013)`` toy group from Chapter 32, with a Fiat-Shamir
  compilation that replaces the verifier's challenge with a random
  oracle query.
- ``measure_and_reprogram``: scaffolding of the DFMS19 measure-and-
  reprogram mechanic in the classical ROM. Runs an adversary twice:
  once to record queries, then again against a fresh oracle reprogrammed
  at a selected query point, demonstrating the reprogramming
  consistency.

Every module is pedagogical. The package does NOT simulate a quantum
adversary; the QROM content lives in Chapter 33's prose, and this
package models only the classical reduction the measure-and-reprogram
technique produces. See ``README.md`` for the scope boundary.
"""

from . import rom_simulator
from . import fiat_shamir
from . import measure_and_reprogram

__all__ = ["rom_simulator", "fiat_shamir", "measure_and_reprogram"]
