"""Rotation and agility labelling over Chapter 25's touchpoints.

Two rules the chapter states in prose and does not print.

``needs_rehash`` is the lifecycle-management area's password case.
Raising a PBKDF2 iteration count cannot rewrite every stored hash,
because the derivation needs the password and the service does not hold
it. The agile pattern stores the count that produced each row and
re-derives that row on the user's next successful login.

``agility_status`` is Exercise 3's labelling rule, a two-axis lookup on
whether a touchpoint carries an algorithm identifier and whether it
carries a rotation policy. It tracks operational maturity rather than
cryptographic vulnerability, so it moves independently of the
``encryptorium:quantum-status`` value Chapter 25 assigns.
"""

from __future__ import annotations

from typing import Any


def needs_rehash(stored_iterations: int, target_iterations: int) -> bool:
    """Decide whether a stored password row is below the current target."""

    return stored_iterations < target_iterations


def agility_status(touchpoint: dict[str, Any]) -> str:
    """Label a touchpoint ``agile``, ``partial`` or ``brittle``.

    ``agile`` needs both an algorithm identifier and a rotation policy,
    ``partial`` exactly one of the two, ``brittle`` neither. A touchpoint
    that names its algorithm but has nowhere to record how that algorithm
    gets replaced is halfway there: the migration tool can find it, and
    no plan says when it moves.
    """

    has_identifier = bool(touchpoint.get("algorithm"))
    has_rotation = bool(touchpoint.get("rotation_policy"))
    if has_identifier and has_rotation:
        return "agile"
    if has_identifier or has_rotation:
        return "partial"
    return "brittle"


def agility_property(touchpoint: dict[str, Any]) -> dict[str, str]:
    """Render the label as a CycloneDX ``properties`` entry.

    The ``encryptorium:`` prefix is the same organization-specific
    namespace Chapter 25's generator uses; CycloneDX 1.6 has no native
    field for operational agility.
    """

    return {
        "name": "encryptorium:agility-status",
        "value": agility_status(touchpoint),
    }
