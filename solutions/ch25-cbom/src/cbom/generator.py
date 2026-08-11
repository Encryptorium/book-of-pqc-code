"""Hand-rolled CycloneDX 1.6 CBOM generator.

Produces a CycloneDX 1.6 document in which every cryptographic
touchpoint is a ``cryptographic-asset`` component. The document is
built using ``dict`` and ``list`` primitives and serialized with
``json.dumps`` from the standard library. No third-party CycloneDX
library is required.

CycloneDX 1.7 was released on 2025-10-21 and is the current version.
This package targets 1.6 deliberately: ``specVersion`` is a per-document
field, 1.6 remains a valid value, and every field used below is defined
identically in both. 1.7 adds ``algorithmFamily`` and ``ellipticCurve``
to ``algorithmProperties`` and ``key-wrap`` to the ``primitive`` enum,
none of which this generator emits.

The fields emitted are the subset of CycloneDX 1.6 needed for a
pedagogical CBOM:

* Document level: ``bomFormat``, ``specVersion``, ``serialNumber``,
  ``version``, ``metadata.timestamp``, ``metadata.component``.
* Each component: ``type="cryptographic-asset"``, ``bom-ref``,
  ``name``, ``cryptoProperties.assetType="algorithm"``,
  ``cryptoProperties.algorithmProperties`` (primitive plus a
  parameter-set identifier), and a ``properties`` list carrying the
  custom encryptorium-prefixed fields (location, exposure, owner,
  deployed date, quantum status).

The six ``encryptorium:``-prefixed entries in the ``properties``
list are ``location``, ``exposure``, ``owner``, ``deployed``,
``quantum-status``, and ``families`` (the comma-joined family list
that the vulnerability lookup consumed). The ``properties`` convention is
the standard CycloneDX escape hatch for organization-specific
metadata; production CBOM tooling uses the same pattern.
"""

from __future__ import annotations

import json
from typing import Any

from .vulnerability import touchpoint_status


SPEC_VERSION = "1.6"


def _parameter_set_identifier(touchpoint: dict[str, Any]) -> str:
    """Summarize a touchpoint's parameters in one human-readable line.

    Keys are sorted so the identifier is stable across versions of
    the document and a CBOM-to-CBOM diff stays meaningful.
    """

    params = touchpoint["parameters"]
    parts: list[str] = [f"{key}={params[key]}" for key in sorted(params)]
    return "; ".join(parts)


def _build_component(touchpoint: dict[str, Any]) -> dict[str, Any]:
    """Build a single cryptographic-asset component."""

    quantum_status = touchpoint_status(touchpoint["families"])
    return {
        "type": "cryptographic-asset",
        "bom-ref": f"crypto:{touchpoint['name']}",
        "name": touchpoint["algorithm"],
        "cryptoProperties": {
            "assetType": "algorithm",
            "algorithmProperties": {
                "primitive": touchpoint["primitive"],
                "parameterSetIdentifier": _parameter_set_identifier(
                    touchpoint
                ),
                "executionEnvironment": "software-plain-ram",
            },
        },
        "properties": [
            {
                "name": "encryptorium:location",
                "value": touchpoint["location"],
            },
            {
                "name": "encryptorium:exposure",
                "value": touchpoint["exposure"],
            },
            {"name": "encryptorium:owner", "value": touchpoint["owner"]},
            {
                "name": "encryptorium:deployed",
                "value": touchpoint["deployed"],
            },
            {
                "name": "encryptorium:quantum-status",
                "value": quantum_status,
            },
            {
                "name": "encryptorium:families",
                "value": ",".join(touchpoint["families"]),
            },
        ],
    }


def build_cbom(
    touchpoints: list[dict[str, Any]],
    *,
    app_name: str = "example-api",
    app_version: str = "1.0.0",
    timestamp: str = "2026-04-16T12:00:00Z",
    serial_number: str = (
        "urn:uuid:00000000-0000-4000-8000-000000000000"
    ),
) -> dict[str, Any]:
    """Build a CycloneDX 1.6 CBOM for a list of touchpoints.

    The timestamp and serial number default to deterministic values so
    tests can compare output byte-for-byte. Real CBOM tooling fills
    both with current time and a fresh UUID.
    """

    return {
        "bomFormat": "CycloneDX",
        "specVersion": SPEC_VERSION,
        "serialNumber": serial_number,
        "version": 1,
        "metadata": {
            "timestamp": timestamp,
            "component": {
                "type": "application",
                "name": app_name,
                "version": app_version,
            },
        },
        "components": [_build_component(t) for t in touchpoints],
    }


def render(cbom: dict[str, Any]) -> str:
    """Render a CBOM dict as CycloneDX-style JSON (2-space indent)."""

    return json.dumps(cbom, indent=2, sort_keys=False)
