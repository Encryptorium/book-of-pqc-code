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
    return tuple(int(part) for part in value.split("."))


def _format_version(v: tuple[int, ...]) -> str:
    return ".".join(str(part) for part in v)


def classify(
    inventory: list[tuple[str, str, str]],
    library_matrix: dict[str, tuple[int, ...]],
) -> list[FleetRow]:
    """Classify each inventory row into ready / gated / blocked."""
    out: list[FleetRow] = []
    for component, library, version in inventory:
        parsed = _parse_version(version)
        minimum = library_matrix.get(library)
        if minimum is None:
            out.append(FleetRow(
                component=component,
                library=library,
                version=parsed,
                status="blocked",
                reason=f"no X25519MLKEM768 support known for {library}",
            ))
            continue
        if parsed >= minimum:
            out.append(FleetRow(
                component=component,
                library=library,
                version=parsed,
                status="ready",
                reason=f"{library} {version} meets minimum {_format_version(minimum)}",
            ))
        else:
            out.append(FleetRow(
                component=component,
                library=library,
                version=parsed,
                status="gated",
                reason=f"{library} {version} below minimum {_format_version(minimum)}",
            ))
    return out
