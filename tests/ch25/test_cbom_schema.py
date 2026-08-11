"""Structural-schema checks for the hand-rolled CycloneDX CBOM.

These checks validate the subset of CycloneDX 1.6 fields the toy
generator emits. They are intentionally lighter than the full
CycloneDX JSON schema; the book does not ship a schema validator.
A reader who wants full validation can paste the generated document
into an external CycloneDX validator, which is the check the chapter
itself performs before landing.
"""

import json

from cbom.app import TOUCHPOINTS
from cbom.generator import build_cbom, render


def _render_and_parse():
    cbom = build_cbom(TOUCHPOINTS)
    text = render(cbom)
    return cbom, text, json.loads(text)


def test_root_envelope():
    cbom, _, parsed = _render_and_parse()
    assert parsed["bomFormat"] == "CycloneDX"
    assert parsed["specVersion"] == "1.6"
    assert parsed["version"] == 1
    assert parsed["serialNumber"].startswith("urn:uuid:")


def test_metadata_block():
    _, _, parsed = _render_and_parse()
    md = parsed["metadata"]
    assert "timestamp" in md and md["timestamp"].endswith("Z")
    comp = md["component"]
    assert comp["type"] == "application"
    assert "name" in comp and "version" in comp


def test_component_count_matches_touchpoints():
    _, _, parsed = _render_and_parse()
    assert len(parsed["components"]) == len(TOUCHPOINTS)


def test_every_component_is_cryptographic_asset():
    _, _, parsed = _render_and_parse()
    for comp in parsed["components"]:
        assert comp["type"] == "cryptographic-asset"
        assert comp["bom-ref"].startswith("crypto:")
        assert "name" in comp
        assert "cryptoProperties" in comp
        assert comp["cryptoProperties"]["assetType"] == "algorithm"
        algo = comp["cryptoProperties"]["algorithmProperties"]
        assert algo["primitive"] in {
            "signature",
            "key-agree",
            "kdf",
            "mac",
            "encrypt",
        }
        assert (
            algo["executionEnvironment"] == "software-plain-ram"
        )
        assert "parameterSetIdentifier" in algo


def test_every_component_carries_encryptorium_properties():
    required = {
        "encryptorium:location",
        "encryptorium:exposure",
        "encryptorium:owner",
        "encryptorium:deployed",
        "encryptorium:quantum-status",
        "encryptorium:families",
    }
    _, _, parsed = _render_and_parse()
    for comp in parsed["components"]:
        props = {p["name"]: p["value"] for p in comp["properties"]}
        missing = required - props.keys()
        assert not missing, f"{comp['name']} missing {missing}"
        assert props["encryptorium:exposure"] in {"public", "internal"}


def test_render_is_valid_json():
    _, text, _ = _render_and_parse()
    # json.loads already ran in the fixture; also check the string is
    # non-empty and two-space-indented (readable).
    assert text.startswith("{\n  ")


def test_bom_refs_unique():
    _, _, parsed = _render_and_parse()
    refs = [c["bom-ref"] for c in parsed["components"]]
    assert len(refs) == len(set(refs))
