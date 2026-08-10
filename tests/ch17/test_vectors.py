"""NIST ACVP test-vector byte-for-byte match (CLAUDE.md §2 rigor rule #3).

This module is the rigor-bar contract for the Chapter 17 flagship
implementation.  It loads two committed ACVP fixtures, both pinned to a
commit of the NIST ACVP-Server repository rather than to ``master``:

- ``vectors/slh_dsa_keygen_acvp.json`` -- one keyGen round per parameter
  set: ``(skSeed, skPrf, pkSeed)`` in, expected ``(sk, pk)`` out.
- ``vectors/slh_dsa_sigver_acvp.json`` -- the ``internal`` interface
  groups of SLH-DSA-sigVer-FIPS205, which drive ``slh_verify`` directly.

Four independent checks run:

1. ``TestParameterSetsAgainstTable2`` pins ``n, h, d, h', a, k, m`` and the
   public-key and signature sizes of all twelve sets against FIPS 205
   Table 2, transcribed as a frozen literal.
2. ``TestACVPKeyGenByteForByte`` reproduces ``sk`` and ``pk`` from seeds.
3. ``TestACVPSigVer`` accepts every valid signature and rejects every
   invalid one, at all twelve parameter sets.
4. ``TestACVPSigGenByteForByte`` regenerates the signature of each valid
   case from its ``sk`` and ``additionalRandomness`` and compares bytes.

Why all four, and not just keygen plus a round-trip.  Key generation
never calls ``H_msg`` or ``PRF_msg`` and never splits a digest, so it
leaves the entire message-hashing path unpinned.  A deterministic
sign-then-verify round-trip does exercise that path, but it passes
whenever signing and verification make the *same* mistake, which is
exactly the failure an independent vector is for.  Both defects found on
2026-08-10 were invisible to keygen and to the round-trip together, and
both are pinned here:

- ``md_len`` summed the three digest field widths in bits and rounded
  once, where FIPS 205 Algorithm 19 rounds each field to a byte boundary
  separately.  The result was one byte short at 4 of the 6 parameter
  sets, which left ``idx_leaf`` reading an empty slice.  Check 1 is the
  cheap guard against that class; check 3 is what found it.
- The SHA2 ``H_msg`` seeded MGF1 with ``digest || R || PK.seed`` where
  FIPS 205 Sections 11.2.1 and 11.2.2 specify ``R || PK.seed || digest``.

Runtime.  Verification is a few milliseconds at every parameter set, so
check 3 runs everywhere.  Signing is not: it is under a second at the
six 'f' sets and 8 to 10 seconds at SLH-DSA-SHA2-128s, growing with the
subtree depth of the other 's' sets.  Check 4 therefore covers the six
'f' sets only, and skips the six 's' sets rather than silently omitting
them.

Coverage dropped on purpose.  Upstream carries 14 sigVer cases at each of
the 12 parameter sets, 168 in all, and the implementation passes all 168.
Committing them costs about 10 MB, so the fixture keeps 24: every set's
shortest-message valid case, plus one case per rejection reason at the
two smallest sets.  The fixture's own ``selection`` field records this.

License note: the committed vectors are a processed subset of the NIST
ACVP-Server test vectors, which are US Federal government work and in
the public domain under 17 USC §105.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from slh_dsa import (
    SLH_DSA_SHA2_128s, SLH_DSA_SHA2_128f,
    SLH_DSA_SHA2_192s, SLH_DSA_SHA2_192f,
    SLH_DSA_SHA2_256s, SLH_DSA_SHA2_256f,
    SLH_DSA_SHAKE_128s, SLH_DSA_SHAKE_128f,
    SLH_DSA_SHAKE_192s, SLH_DSA_SHAKE_192f,
    SLH_DSA_SHAKE_256s, SLH_DSA_SHAKE_256f,
)
from slh_dsa.slh import slh_keygen_internal, slh_sign_internal, slh_verify


VECTORS_DIR = Path(__file__).parent / "vectors"

PARAM_SETS = {
    "SLH-DSA-SHA2-128s": SLH_DSA_SHA2_128s,
    "SLH-DSA-SHA2-128f": SLH_DSA_SHA2_128f,
    "SLH-DSA-SHA2-192s": SLH_DSA_SHA2_192s,
    "SLH-DSA-SHA2-192f": SLH_DSA_SHA2_192f,
    "SLH-DSA-SHA2-256s": SLH_DSA_SHA2_256s,
    "SLH-DSA-SHA2-256f": SLH_DSA_SHA2_256f,
    "SLH-DSA-SHAKE-128s": SLH_DSA_SHAKE_128s,
    "SLH-DSA-SHAKE-128f": SLH_DSA_SHAKE_128f,
    "SLH-DSA-SHAKE-192s": SLH_DSA_SHAKE_192s,
    "SLH-DSA-SHAKE-192f": SLH_DSA_SHAKE_192f,
    "SLH-DSA-SHAKE-256s": SLH_DSA_SHAKE_256s,
    "SLH-DSA-SHAKE-256f": SLH_DSA_SHAKE_256f,
}

# FIPS 205 Table 2, transcribed by hand from the standard.  The six rows
# each cover a SHA2 and a SHAKE set, which share every parameter in this
# table and differ only in how Section 11 instantiates the six hash
# functions.  Keyed by the shared suffix.
#
#                    n,   h,  d,  hp,  a,  k,   m, category, pk, sig
FIPS205_TABLE_2 = {
    "128s": (16, 63,  7,  9, 12, 14, 30, 1, 32,  7_856),
    "128f": (16, 66, 22,  3,  6, 33, 34, 1, 32, 17_088),
    "192s": (24, 63,  7,  9, 14, 17, 39, 3, 48, 16_224),
    "192f": (24, 66, 22,  3,  8, 33, 42, 3, 48, 35_664),
    "256s": (32, 64,  8,  8, 14, 22, 47, 5, 64, 29_792),
    "256f": (32, 68, 17,  4,  9, 35, 49, 5, 64, 49_856),
}


def _load(name: str) -> dict:
    return json.loads((VECTORS_DIR / name).read_text())


_KEYGEN = None
_SIGVER = None


def _keygen_vectors() -> list[dict]:
    global _KEYGEN
    if _KEYGEN is None:
        _KEYGEN = _load("slh_dsa_keygen_acvp.json")["testCases"]
    return _KEYGEN


def _sigver_groups() -> list[dict]:
    global _SIGVER
    if _SIGVER is None:
        _SIGVER = _load("slh_dsa_sigver_acvp.json")["testGroups"]
    return _SIGVER


def _sigver_cases(valid_only: bool = False) -> list[tuple[str, dict]]:
    return [
        (g["parameterSet"], t)
        for g in _sigver_groups()
        for t in g["tests"]
        if t["testPassed"] or not valid_only
    ]


def _case_id(value: object) -> str:
    """Build a pytest node id with no ``" - "`` and no comma in it.

    ``tools/verify_exercises.py`` reads pytest's short summary and splits
    each line on the first ``" - "`` to separate the node id from the
    exception.  ACVP reason strings are of the form ``modified signature
    - R``, so passing one through verbatim moves the split point into the
    id and the tool reports a parse artifact as a non-stub failure.
    """
    if isinstance(value, str):
        return value
    slug = "".join(
        c if c.isalnum() else "_" for c in str(value.get("reason", ""))
    ).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    return f"tc{value['tcId']}_{slug}"


# -- Parameters against FIPS 205 Table 2 -----------------------------------

@pytest.mark.parametrize("param_name", list(PARAM_SETS), ids=lambda p: p)
class TestParameterSetsAgainstTable2:
    """Pin every Table 2 column, so a derived formula cannot drift.

    ``md_len`` is a computed property rather than a stored field, and it
    was wrong at four of these six rows until 2026-08-10 while every
    round-trip test still passed.  A frozen table is what makes that a
    one-line failure instead of a cryptographic investigation.
    """

    def test_matches_table_2(self, param_name: str) -> None:
        params = PARAM_SETS[param_name]
        n, h, d, hp, a, k, m, category, pk_len, sig_len = (
            FIPS205_TABLE_2[param_name.rsplit("-", 1)[1]]
        )
        assert (params.n, params.h, params.d, params.hp, params.a, params.k) == (
            n, h, d, hp, a, k
        ), f"{param_name}: tree parameters disagree with FIPS 205 Table 2"
        assert params.md_len == m, (
            f"{param_name}: md_len is {params.md_len}, Table 2 says m = {m}"
        )
        assert params.pk_bytes() == pk_len
        assert params.sk_bytes() == 2 * pk_len
        assert params.sig_bytes() == sig_len, (
            f"{param_name}: sig_bytes() is {params.sig_bytes():,d}, "
            f"Table 2 says {sig_len:,d}"
        )
        # Algorithm 19 lines 6 to 8: the three digest fields must fit in m.
        assert (
            (k * a + 7) // 8 + (h - hp + 7) // 8 + (hp + 7) // 8
        ) == m, f"{param_name}: the three Algorithm 19 field widths do not sum to m"
        assert category in (1, 3, 5)


# -- Keygen byte-for-byte match -------------------------------------------

@pytest.mark.parametrize("param_name", list(PARAM_SETS), ids=lambda p: p)
class TestACVPKeyGenByteForByte:
    def test_keygen(self, param_name: str) -> None:
        vec = next(
            (v for v in _keygen_vectors() if v["parameterSet"] == param_name), None
        )
        if vec is None:
            pytest.skip(f"no vector for {param_name}")

        params = PARAM_SETS[param_name]
        sk, pk = slh_keygen_internal(
            params,
            bytes.fromhex(vec["skSeed"]),
            bytes.fromhex(vec["skPrf"]),
            bytes.fromhex(vec["pkSeed"]),
        )

        assert sk.hex() == vec["sk"].lower(), (
            f"{param_name} KeyGen tcId={vec['tcId']}: sk mismatch"
        )
        assert pk.hex() == vec["pk"].lower(), (
            f"{param_name} KeyGen tcId={vec['tcId']}: pk mismatch"
        )


# -- sigVer: accept the valid, reject the invalid --------------------------

@pytest.mark.parametrize(
    "param_name,vec",
    _sigver_cases(),
    ids=_case_id,
)
class TestACVPSigVer:
    """Every committed ACVP sigVer case, at all twelve parameter sets.

    The valid cases are the ones that matter most: they are signatures
    this package did not produce, so they cannot pass by sharing a
    mistake with the signer.
    """

    def test_verdict(self, param_name: str, vec: dict) -> None:
        params = PARAM_SETS[param_name]
        got = slh_verify(
            params,
            bytes.fromhex(vec["pk"]),
            bytes.fromhex(vec["message"]),
            bytes.fromhex(vec["signature"]),
        )
        assert got is vec["testPassed"], (
            f"{param_name} sigVer tcId={vec['tcId']} ({vec['reason']}): "
            f"expected {vec['testPassed']}, got {got}"
        )


# -- sigGen byte-for-byte, at the parameter sets that are fast enough ------

@pytest.mark.parametrize(
    "param_name,vec",
    _sigver_cases(valid_only=True),
    ids=_case_id,
)
class TestACVPSigGenByteForByte:
    """Regenerate each valid ACVP signature from its own sk and addrnd.

    Stronger than sigVer, which only checks a boolean.  Restricted to the
    six 'f' parameter sets on runtime grounds: signing is under a second
    there and 8 to 10 seconds at SLH-DSA-SHA2-128s, rising with subtree
    depth across the rest of the 's' sets.  The 's' sets are skipped
    rather than dropped, so the gap is visible in the pytest report.
    """

    def test_siggen(self, param_name: str, vec: dict) -> None:
        if param_name.endswith("s"):
            pytest.skip(
                f"{param_name}: signing is too slow for CI "
                "(sigVer still covers this parameter set)"
            )
        params = PARAM_SETS[param_name]
        sig = slh_sign_internal(
            params,
            bytes.fromhex(vec["sk"]),
            bytes.fromhex(vec["message"]),
            bytes.fromhex(vec["additionalRandomness"]),
        )
        assert sig.hex() == vec["signature"].lower(), (
            f"{param_name} sigGen tcId={vec['tcId']}: signature mismatch"
        )


# -- Sanity check: fixtures exist and cover every parameter set ------------

class TestKATFilesPresent:
    def test_keygen_file_committed(self) -> None:
        path = VECTORS_DIR / "slh_dsa_keygen_acvp.json"
        assert path.exists(), f"missing committed KAT at {path}"
        assert path.stat().st_size > 1000, f"{path} suspiciously small (<1 KB)"

    def test_sigver_file_committed(self) -> None:
        path = VECTORS_DIR / "slh_dsa_sigver_acvp.json"
        assert path.exists(), f"missing committed KAT at {path}"
        assert path.stat().st_size > 1000, f"{path} suspiciously small (<1 KB)"

    def test_all_param_sets_have_vectors(self) -> None:
        keygen = {v["parameterSet"] for v in _keygen_vectors()}
        sigver = {g["parameterSet"] for g in _sigver_groups()}
        for name in PARAM_SETS:
            assert name in keygen, f"no keygen vector for {name}"
            assert name in sigver, f"no sigVer vector for {name}"

    def test_every_set_has_a_valid_sigver_case(self) -> None:
        for group in _sigver_groups():
            assert any(t["testPassed"] for t in group["tests"]), (
                f"{group['parameterSet']} has no valid sigVer case, so nothing "
                "pins its signing path against an independent signer"
            )

    def test_fixtures_are_commit_pinned(self) -> None:
        """A ``master`` URL does not identify the bytes that were tested."""
        for name in ("slh_dsa_keygen_acvp.json", "slh_dsa_sigver_acvp.json"):
            source = _load(name)["source"]
            assert "/master/" not in source, f"{name}: source pins master"
            assert "ACVP-Server/" in source and "pinned to the commit" in source
