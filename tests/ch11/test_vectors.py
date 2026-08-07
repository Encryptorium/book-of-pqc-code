"""NIST ACVP test-vector byte-for-byte match (CLAUDE.md §2 rigor rule #3).

This test is the rigor-bar contract for the Chapter 11 flagship
implementation. It loads one KAT round per ML-KEM parameter set from
``tests/ch11/vectors/ml_kem_{512,768,1024}_acvp.json``, each containing:

- ``keyGen``: ``(d, z)`` seeds and expected ``(ek, dk)`` from the
  NIST ACVP ML-KEM-keyGen-FIPS203 fixture.
- ``encaps``: ``(ek, m)`` inputs and expected ``(c, k)`` from the
  NIST ACVP ML-KEM-encapDecap-FIPS203 fixture (encapsulation group).
- ``decaps``: ``(dk, c)`` inputs and expected ``k`` from the NIST
  ACVP ML-KEM-encapDecap-FIPS203 fixture (decapsulation group).

For each parameter set, three independent checks run:

1. ``ml_kem_keygen_internal(d, z)`` produces bytes equal to the
   expected ``ek`` and ``dk``.
2. ``ml_kem_encaps_internal(ek, m)`` produces bytes equal to the
   expected ``k`` and ``c``.
3. ``ml_kem_decaps_internal(dk, c)`` produces bytes equal to the
   expected ``k``.

All three are ``==`` comparisons on raw bytes. Any mismatch fails
the chapter merge. The KAT JSON files are committed under
``tests/ch11/vectors/`` so CI runs offline; the network fetch happens
once, at KAT landing time, not on every pytest run.

License note: the committed vectors are a processed subset of the
NIST ACVP-Server test vectors, which are US Federal government work
and in the public domain under 17 USC §105. The full ACVP suites
have thousands of cases; this file extracts exactly three rounds.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mlkem import ML_KEM_512, ML_KEM_768, ML_KEM_1024
from mlkem.ml_kem import (
    ml_kem_keygen_internal,
    ml_kem_encaps_internal,
    ml_kem_decaps_internal,
)


VECTORS_DIR = Path(__file__).parent / "vectors"
PARAM_SETS = {
    "ML-KEM-512": ML_KEM_512,
    "ML-KEM-768": ML_KEM_768,
    "ML-KEM-1024": ML_KEM_1024,
}


def _load_kat(name: str) -> dict:
    filename = f"{name.lower().replace('-', '_')}_acvp.json"
    return json.loads((VECTORS_DIR / filename).read_text())


@pytest.mark.parametrize(
    "param_name",
    list(PARAM_SETS.keys()),
    ids=lambda p: p,
)
class TestACVPByteForByte:
    def test_keygen(self, param_name: str) -> None:
        kat = _load_kat(param_name)
        kg = kat["keyGen"]
        params = PARAM_SETS[param_name]
        d = bytes.fromhex(kg["d"])
        z = bytes.fromhex(kg["z"])
        ek, dk = ml_kem_keygen_internal(params, d, z)
        assert ek.hex() == kg["ek"].lower(), (
            f"{param_name} KeyGen tcId={kg['tcId']}: ek mismatch"
        )
        assert dk.hex() == kg["dk"].lower(), (
            f"{param_name} KeyGen tcId={kg['tcId']}: dk mismatch"
        )

    def test_encaps(self, param_name: str) -> None:
        kat = _load_kat(param_name)
        enc = kat["encaps"]
        params = PARAM_SETS[param_name]
        ek = bytes.fromhex(enc["ek"])
        m = bytes.fromhex(enc["m"])
        K, c = ml_kem_encaps_internal(params, ek, m)
        assert c.hex() == enc["c"].lower(), (
            f"{param_name} Encaps tcId={enc['tcId']}: c mismatch"
        )
        assert K.hex() == enc["k"].lower(), (
            f"{param_name} Encaps tcId={enc['tcId']}: K mismatch"
        )

    def test_decaps(self, param_name: str) -> None:
        kat = _load_kat(param_name)
        dec = kat["decaps"]
        params = PARAM_SETS[param_name]
        dk = bytes.fromhex(dec["dk"])
        c = bytes.fromhex(dec["c"])
        K = ml_kem_decaps_internal(params, dk, c)
        assert K.hex() == dec["k"].lower(), (
            f"{param_name} Decaps tcId={dec['tcId']}: K mismatch"
        )


class TestKATFilesPresent:
    def test_all_three_files_committed(self) -> None:
        for name in ("ml_kem_512", "ml_kem_768", "ml_kem_1024"):
            path = VECTORS_DIR / f"{name}_acvp.json"
            assert path.exists(), f"missing committed KAT at {path}"
            assert path.stat().st_size > 1000, (
                f"{path} suspiciously small (<1 KB)"
            )
