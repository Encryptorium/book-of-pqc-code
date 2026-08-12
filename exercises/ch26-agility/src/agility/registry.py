"""A four-state approval registry and the rules that read it.

``REGISTRY``, ``POLICY`` and ``sign`` are Chapter 26's Block 3: a MAC
registry carrying an approval state per identifier, a policy table
mapping each Chapter 25 touchpoint to the identifier it uses, and a
signer that refuses anything not currently approved for applying
protection.

``permits`` and ``approved_at`` are the two rules the chapter states in
prose and does not print. ``permits`` encodes the asymmetry between the
four states; ``approved_at`` encodes the dated approved-algorithm list
from the governance area.

The four state names come from NIST SP 800-131A Rev. 2, which applies
them to (algorithm, key-length) pairs on dated transitions rather than
to hash functions. For HMAC in particular that document routes entirely
through key length: generation keys of at least 112 bits are acceptable
and shorter ones disallowed, while verification accepts shorter keys for
legacy use. The entries below therefore borrow the vocabulary to record
one organization's local policy, and are not a transcription of NIST
per-algorithm status.
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Any, Callable, Optional


# The four SP 800-131A Rev. 2 approval states, strongest first.
STATES = ("acceptable", "deprecated", "legacy-use", "disallowed")

REGISTRY: dict[str, dict[str, Any]] = {
    "HMAC-MD5": {"hash": hashlib.md5, "state": "disallowed"},
    "HMAC-SHA1": {"hash": hashlib.sha1, "state": "deprecated"},
    "HMAC-SHA256": {"hash": hashlib.sha256, "state": "acceptable"},
    "HMAC-SHA512": {"hash": hashlib.sha512, "state": "acceptable"},
}

POLICY = {
    "webhook_hmac": "HMAC-SHA256",
    "internal_bus": "HMAC-SHA512",
    "legacy_connector": "HMAC-SHA1",
}


def sign(
    touchpoint: str, key: bytes, body: bytes
) -> tuple[str, bytes]:
    """Sign ``body`` under the algorithm this touchpoint's policy names.

    Raises ``ValueError`` when the registry marks that algorithm
    ``disallowed`` or ``deprecated``, so the refusal happens at call
    time rather than at review time.
    """

    alg = POLICY[touchpoint]
    entry = REGISTRY[alg]
    if entry["state"] in ("disallowed", "deprecated"):
        raise ValueError(f"{alg} is {entry['state']}")
    return alg, hmac.new(key, body, entry["hash"]).digest()


def permits(state: str, operation: str) -> bool:
    """Decide whether an approval ``state`` allows an ``operation``.

    ``operation`` is ``"protect"`` (applying cryptographic protection:
    signing, encrypting, generating a MAC) or ``"process"`` (acting on
    data that is already protected: verifying, decrypting).

    The asymmetry is the whole point of having four states rather than a
    boolean. ``legacy-use`` permits processing already-protected data and
    nothing else, which is what lets an organization stop issuing under
    an algorithm without stranding everything already issued under it.
    ``deprecated`` still permits both, and carries risk rather than a
    prohibition.
    """

    # EXERCISE: implement this function.
    #
    # Map an approval state and an operation to a boolean. 'protect' is
    # applying cryptographic protection (signing, encrypting, generating a
    # MAC); 'process' is acting on data that is already protected
    # (verifying, decrypting). Reject any state outside STATES and any
    # operation outside the two, with ValueError. 'disallowed' permits
    # nothing; 'legacy-use' permits processing only, which is what lets an
    # organization stop issuing under an algorithm without stranding what it
    # already issued; 'acceptable' and 'deprecated' both permit everything,
    # because deprecation signals risk rather than prohibition.
    #
    # Reference: Chapter 26, 'Math preliminaries: identifiers, MTI, deprecation signaling'
    #
    # Proved by:
    #   tests/ch26/test_registry.py
    raise NotImplementedError("exercise: permits")


def approved_at(entry: dict[str, Any], on_date: str) -> bool:
    """Decide whether a dated approved-algorithm entry is live on a date.

    ``entry`` carries ISO-8601 ``effective`` and ``expires`` values; an
    absent or ``None`` ``expires`` means the entry has no scheduled end.
    Dates compare as strings because ISO-8601 orders lexicographically.

    This is the check a CI gate runs against the deployed fleet. A list
    with no dates on it cannot be gated: there is no moment at which an
    entry becomes wrong, so nothing can fail a build.
    """

    # EXERCISE: implement this function.
    #
    # Decide whether a dated approved-algorithm entry is live on a given
    # date. The entry carries optional 'effective' and 'expires' ISO-8601
    # values; an absent or None value means that end of the window is open.
    # Both boundaries are inclusive. ISO-8601 dates order lexicographically,
    # so string comparison is the whole implementation. An entry with
    # neither date is always approved, which is the brittle pattern: with no
    # dates on the list there is no moment at which an entry becomes wrong,
    # so no CI gate can ever fail on it.
    #
    # Reference: Chapter 26, 'Governance and policy'
    #
    # Proved by:
    #   tests/ch26/test_registry.py
    raise NotImplementedError("exercise: approved_at")
