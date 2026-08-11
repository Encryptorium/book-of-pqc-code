"""End-to-end test: TOUCHPOINTS -> CBOM -> expected quantum posture."""

import json

from cbom.app import TOUCHPOINTS
from cbom.generator import build_cbom, render
from cbom.vulnerability import (
    GROVER_ONLY,
    QUANTUM_SAFE,
    UNKNOWN,
    VULNERABLE,
    touchpoint_status,
)


def _expected_status(families: list[str]) -> str:
    # Mirror cbom.vulnerability.touchpoint_status to keep the oracle
    # honest when new families (e.g. ML-KEM in Exercise 1) are added.
    return touchpoint_status(families)


def test_every_touchpoint_emits_one_component():
    cbom = build_cbom(TOUCHPOINTS)
    assert len(cbom["components"]) == 5


def test_quantum_status_matches_family_rules():
    cbom = build_cbom(TOUCHPOINTS)
    for touchpoint, component in zip(TOUCHPOINTS, cbom["components"]):
        props = {p["name"]: p["value"] for p in component["properties"]}
        expected = _expected_status(touchpoint["families"])
        assert props["encryptorium:quantum-status"] == expected, (
            touchpoint["name"],
            expected,
        )


def test_tls_jwt_and_validator_are_vulnerable_webhook_and_pbkdf_are_grover():
    cbom = build_cbom(TOUCHPOINTS)
    status_by_name = {}
    for comp in cbom["components"]:
        props = {p["name"]: p["value"] for p in comp["properties"]}
        status_by_name[comp["bom-ref"]] = props[
            "encryptorium:quantum-status"
        ]
    assert status_by_name["crypto:tls_endpoint_api"] == VULNERABLE
    assert status_by_name["crypto:jwt_signing"] == VULNERABLE
    assert status_by_name["crypto:password_hashing"] == GROVER_ONLY
    assert status_by_name["crypto:webhook_hmac"] == GROVER_ONLY
    assert status_by_name["crypto:blockchain_validator_sig"] == VULNERABLE


def test_deterministic_serialization_round_trip():
    cbom = build_cbom(TOUCHPOINTS)
    text_a = render(cbom)
    text_b = render(cbom)
    assert text_a == text_b
    assert json.loads(text_a) == cbom


def test_parameter_set_identifier_is_nonempty():
    cbom = build_cbom(TOUCHPOINTS)
    for comp in cbom["components"]:
        algo = comp["cryptoProperties"]["algorithmProperties"]
        assert len(algo["parameterSetIdentifier"]) > 0


def test_primitive_distribution():
    cbom = build_cbom(TOUCHPOINTS)
    primitives = sorted(
        comp["cryptoProperties"]["algorithmProperties"]["primitive"]
        for comp in cbom["components"]
    )
    assert primitives == ["kdf", "key-agree", "mac", "signature", "signature"]
