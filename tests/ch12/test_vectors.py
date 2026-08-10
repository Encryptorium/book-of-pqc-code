"""NIST ACVP test-vector byte-for-byte match (CLAUDE.md §2 rigor rule #3).

This is the rigor-bar contract for the Chapter 12 flagship ML-DSA (FIPS 204)
implementation. For each of the three parameter sets it loads one KAT round per
operation from ``tests/ch12/vectors/ml_dsa_{44,65,87}_acvp.json`` and checks:

- ``keyGen``: seed -> (pk, sk) reproduced byte-for-byte.
- ``sigGen``: deterministic Sign_internal (rnd = 0^32) of the given message under
  the given sk reproduces the expected signature byte-for-byte.
- ``sigVer`` valid: Verify_internal accepts the genuine (pk, message, signature).
- ``sigVer`` invalid: Verify_internal *rejects* a tampered case. The invalid case
  is the specific defense against a verify bug that mirrors a sign bug: a
  round-trip test alone would pass even if both directions shared the flaw.

All cases use the ACVP "internal" signature interface with ``externalMu=false``,
so the ``message`` field is exactly the M' passed to the internal functions.

The vectors are vendored from the NIST usnistgov/ACVP-Server repository with the
source commit pinned in each JSON (``sourceCommit``); the network fetch happened
once, at KAT landing time, so pytest runs fully offline. The committed vectors are
a processed subset (four rounds per parameter set) of the public-domain ACVP
suites (US Federal government work, 17 USC §105).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mldsa import ML_DSA_44, ML_DSA_65, ML_DSA_87
from mldsa.ml_dsa import (
    ml_dsa_keygen_internal,
    ml_dsa_sign_internal,
    ml_dsa_verify_internal,
)

VECTORS_DIR = Path(__file__).parent / "vectors"
PARAM_SETS = {
    "ML-DSA-44": ML_DSA_44,
    "ML-DSA-65": ML_DSA_65,
    "ML-DSA-87": ML_DSA_87,
}
PINNED_COMMIT = "2972def23bf9f3680c2c531561ed9bdd0f1086ad"


def _load_kat(name: str) -> dict:
    filename = f"{name.lower().replace('-', '_')}_acvp.json"
    return json.loads((VECTORS_DIR / filename).read_text())


@pytest.mark.parametrize("param_name", list(PARAM_SETS.keys()), ids=lambda p: p)
class TestACVPByteForByte:
    def test_keygen(self, param_name: str) -> None:
        kat = _load_kat(param_name)
        params = PARAM_SETS[param_name]
        kg = kat["keyGen"]
        pk, sk = ml_dsa_keygen_internal(params, bytes.fromhex(kg["seed"]))
        assert pk.hex() == kg["pk"].lower(), f"{param_name} keyGen tc{kg['tcId']}: pk mismatch"
        assert sk.hex() == kg["sk"].lower(), f"{param_name} keyGen tc{kg['tcId']}: sk mismatch"

    def test_siggen_deterministic(self, param_name: str) -> None:
        kat = _load_kat(param_name)
        params = PARAM_SETS[param_name]
        sg = kat["sigGen"]
        sig = ml_dsa_sign_internal(
            params,
            bytes.fromhex(sg["sk"]),
            bytes.fromhex(sg["message"]),
            bytes.fromhex(sg["rnd"]),
        )
        assert sig.hex() == sg["signature"].lower(), (
            f"{param_name} sigGen tc{sg['tcId']}: signature mismatch"
        )

    def test_sigver_valid(self, param_name: str) -> None:
        kat = _load_kat(param_name)
        params = PARAM_SETS[param_name]
        sv = kat["sigVerValid"]
        ok = ml_dsa_verify_internal(
            params, bytes.fromhex(sv["pk"]), bytes.fromhex(sv["message"]),
            bytes.fromhex(sv["signature"]),
        )
        assert ok is True, f"{param_name} sigVer(valid) tc{sv['tcId']}: should accept"

    def test_sigver_invalid(self, param_name: str) -> None:
        kat = _load_kat(param_name)
        params = PARAM_SETS[param_name]
        sv = kat["sigVerInvalid"]
        ok = ml_dsa_verify_internal(
            params, bytes.fromhex(sv["pk"]), bytes.fromhex(sv["message"]),
            bytes.fromhex(sv["signature"]),
        )
        assert ok is False, (
            f"{param_name} sigVer(invalid) tc{sv['tcId']} "
            f"({sv.get('reason')}): should reject"
        )


class TestKATProvenance:
    def test_all_three_files_committed(self) -> None:
        for name in ("ml_dsa_44", "ml_dsa_65", "ml_dsa_87"):
            path = VECTORS_DIR / f"{name}_acvp.json"
            assert path.exists(), f"missing committed KAT at {path}"
            assert path.stat().st_size > 1000, f"{path} suspiciously small (<1 KB)"

    def test_source_commit_pinned(self) -> None:
        for name in PARAM_SETS:
            kat = _load_kat(name)
            assert kat["sourceCommit"] == PINNED_COMMIT
            assert "ACVP-Server" in kat["sourceRepo"]
            assert kat["signatureInterface"] == "internal"
            assert kat["externalMu"] is False
