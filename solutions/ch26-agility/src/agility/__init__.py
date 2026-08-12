"""Crypto-agility patterns for Chapter 26 of the Encryptorium Book of PQC.

Four modules, each mapping to material in the chapter:

* ``tokens``   -- the brittle and agile JWT-like signers of Block 1.
* ``algid``    -- the namespaced algorithm-identifier parser of Block 2.
* ``registry`` -- the four-state approval registry of Block 3, plus the
                  approval-state and effective-date rules the chapter
                  states in prose but does not print.
* ``posture``  -- the rotation and agility-labelling rules from the
                  lifecycle-management area and Exercise 3.

Standard library only.
"""

from .algid import parse_algid
from .posture import agility_property, agility_status, needs_rehash
from .registry import POLICY, STATES, approved_at, permits, sign
from .tokens import (
    b64url,
    sign_agile,
    sign_brittle,
    verify_agile,
    verify_brittle,
)

__all__ = [
    "POLICY",
    "STATES",
    "agility_property",
    "agility_status",
    "approved_at",
    "b64url",
    "needs_rehash",
    "parse_algid",
    "permits",
    "sign",
    "sign_agile",
    "sign_brittle",
    "verify_agile",
    "verify_brittle",
]
