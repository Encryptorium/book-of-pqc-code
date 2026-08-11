"""HQC NIST KAT structural-integrity tests.

The Chapter 21 implementation is a pedagogical IND-CPA toy; it does not
match the reference HQC KAT byte-for-byte. See
``tests/ch21/vectors/README.md`` for the list of divergences (no Reed-
Muller inner code, no FO wrapping, small parameters).

The sizes below come from the 22 August 2025 HQC specification, which
supersedes the Round-4 submission and is the revision the chapter's
parameter-set table reproduces: Table 5 for the parameters and Table 6
for the byte sizes. They were confirmed against the official KAT files
in the HQC reference repository on 2026-08-11, whose ``.rsp`` filenames
carry the decapsulation-key length.

When those ``.rsp`` files are dropped under ``tests/ch21/vectors/``
under the names in ``PARAMS``, this suite parses each file and checks:

- the file contains exactly 100 NIST-KAT vectors,
- every vector has the ``count``, ``seed``, ``pk``, ``sk``, ``ct``, ``ss``
  fields,
- the byte lengths of ``pk``, ``sk``, ``ct`` match the specification for
  that parameter set.

When the ``.rsp`` files are absent, every test is skipped with a clear
reason. Running ``pytest`` on a clean clone therefore stays green, and
the suite activates as soon as someone supplies the vendored KAT.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


VECTORS_DIR = Path(__file__).resolve().parent / "vectors"


PARAMS = {
    "hqc-1": {"pk": 2241, "sk": 2321, "ct": 4433, "count": 100,
              "kat": "PQCkemKAT_2321.rsp"},
    "hqc-3": {"pk": 4514, "sk": 4602, "ct": 8978, "count": 100,
              "kat": "PQCkemKAT_4602.rsp"},
    "hqc-5": {"pk": 7237, "sk": 7333, "ct": 14421, "count": 100,
              "kat": "PQCkemKAT_7333.rsp"},
}


_BLOCK_FIELDS = ("count", "seed", "pk", "sk", "ct", "ss")
_FIELD_RE = re.compile(r"^(\w+)\s*=\s*(.*)$")


def _kat_path(param_set: str) -> Path:
    return VECTORS_DIR / PARAMS[param_set]["kat"]


def _parse_kat(path: Path) -> list[dict]:
    """Parse a NIST KAT .rsp file into a list of per-vector dicts."""
    vectors: list[dict] = []
    current: dict = {}
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line:
            if current:
                vectors.append(current)
                current = {}
            continue
        if line.startswith("#"):
            continue
        match = _FIELD_RE.match(line)
        if not match:
            continue
        key, value = match.group(1).lower(), match.group(2).strip()
        current[key] = value
    if current:
        vectors.append(current)
    return vectors


@pytest.mark.parametrize("param_set", sorted(PARAMS))
def test_kat_file_parses(param_set: str) -> None:
    path = _kat_path(param_set)
    if not path.exists():
        pytest.skip(
            f"{path.name} not vendored; see tests/ch21/vectors/README.md "
            "for fetch instructions"
        )
    vectors = _parse_kat(path)
    expected_count = PARAMS[param_set]["count"]
    assert len(vectors) == expected_count, (
        f"{path.name}: expected {expected_count} KAT vectors, got {len(vectors)}"
    )


@pytest.mark.parametrize("param_set", sorted(PARAMS))
def test_kat_vectors_have_required_fields(param_set: str) -> None:
    path = _kat_path(param_set)
    if not path.exists():
        pytest.skip(
            f"{path.name} not vendored; see tests/ch21/vectors/README.md"
        )
    vectors = _parse_kat(path)
    for idx, vec in enumerate(vectors):
        missing = [f for f in _BLOCK_FIELDS if f not in vec]
        assert not missing, (
            f"{path.name} vector {idx}: missing fields {missing}"
        )


@pytest.mark.parametrize("param_set", sorted(PARAMS))
def test_kat_byte_lengths_match_specification(param_set: str) -> None:
    path = _kat_path(param_set)
    if not path.exists():
        pytest.skip(
            f"{path.name} not vendored; see tests/ch21/vectors/README.md"
        )
    spec = PARAMS[param_set]
    vectors = _parse_kat(path)
    first = vectors[0]
    for field in ("pk", "sk", "ct"):
        raw_hex = first[field]
        # KAT hex strings are uppercase, whitespace-free.
        byte_len = len(raw_hex) // 2
        assert byte_len == spec[field], (
            f"{path.name} {field}: expected {spec[field]} bytes, "
            f"got {byte_len}"
        )


def test_toy_divergence_is_documented() -> None:
    """The README must name the gap between the toy and the reference.

    Phase 1.7 of the launch fix pass requires this divergence to be
    stated where a reader will actually find it. This test fails if the
    README is absent or the key divergence points are not mentioned.
    """
    readme = VECTORS_DIR / "README.md"
    assert readme.exists(), (
        "tests/ch21/vectors/README.md is missing; the toy-vs-reference "
        "divergence must be documented where a reader will actually find it."
    )
    text = readme.read_text(encoding="utf-8")
    for required in ("Reed-Muller", "FO", "IND-CPA", "17669"):
        assert required in text, (
            f"README missing required divergence marker: {required!r}"
        )
