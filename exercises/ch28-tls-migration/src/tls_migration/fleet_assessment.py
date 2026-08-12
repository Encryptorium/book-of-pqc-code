"""Fleet-readiness classification for X25519MLKEM768 migration.

Takes an inventory of ``(component, library, version)`` rows and a
library matrix mapping each known library to the minimum version that
supports X25519MLKEM768. Classifies each row into one of three states:

- ``ready``: library is in the matrix and the version meets or exceeds
  the minimum.
- ``gated``: library is in the matrix but the version is below the
  minimum; the library supports the hybrid, the deployed runtime does
  not.
- ``blocked``: library is not in the matrix; no supported version is
  known to the classifier.

Versions are parsed as dotted integer tuples (``"3.5.0"`` → ``(3, 5, 0)``),
and comparison is tuple-lexicographic. Malformed versions propagate
``ValueError`` from ``int()``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FleetRow:
    component: str
    library: str
    version: tuple[int, ...]
    status: str
    reason: str


def _parse_version(value: str) -> tuple[int, ...]:
    # EXERCISE: implement this function.
    #
    # Split the version string on dots and turn each part into an int,
    # returning the tuple. Tuples compare lexicographically, so (1, 23, 99)
    # sorts below (1, 24, 0) where the strings would not. Let int() raise
    # ValueError on a build suffix such as '3.5.0-fips': the classifier is
    # deliberately narrow, and a version it cannot parse is a row the
    # operator has to look at rather than one to guess about.
    #
    # Reference: Chapter 28, 'Fleet assessment'
    #
    # Proved by:
    #   tests/ch28/test_fleet_assessment.py
    raise NotImplementedError("exercise: _parse_version")


def _format_version(v: tuple[int, ...]) -> str:
    return ".".join(str(part) for part in v)


def classify(
    inventory: list[tuple[str, str, str]],
    library_matrix: dict[str, tuple[int, ...]],
) -> list[FleetRow]:
    """Classify each inventory row into ready / gated / blocked."""
    # EXERCISE: implement this function.
    #
    # One FleetRow per inventory row, in input order. Parse the version,
    # then look the library up in the matrix. No entry means blocked, with a
    # reason naming the library, because the classifier knows of no
    # X25519MLKEM768 support path at any version. An entry the parsed
    # version meets or exceeds means ready; below it means gated, which is a
    # runtime-upgrade task rather than a dead end. Both of those reasons
    # should name the minimum, formatted back to dotted form. The comparison
    # is at least the minimum, not strictly greater, so a component sitting
    # exactly on OpenSSL 3.5.0 is ready.
    #
    # Reference: Chapter 28, 'Fleet assessment'
    #
    # Proved by:
    #   tests/ch28/test_fleet_assessment.py
    raise NotImplementedError("exercise: classify")
