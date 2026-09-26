"""Tests for the X25519MLKEM768 configuration lint (OpenSSL and nginx)."""

import pytest

from tls_migration.config_lint import (
    HYBRID,
    lint_nginx_groups,
    lint_openssl_groups,
)


def test_openssl_good_snippet_has_no_findings():
    config = """
# OpenSSL 3.5+ TLS 1.3 config snippet
[system_default_sect]
MinProtocol = TLSv1.3
Groups = X25519MLKEM768/X25519:secp256r1
"""
    assert lint_openssl_groups(config) == []


def test_nginx_good_snippet_has_no_findings():
    config = """
server {
    listen 443 ssl;
    ssl_protocols TLSv1.3;
    ssl_ecdh_curve X25519MLKEM768/X25519:secp256r1;
}
"""
    assert lint_nginx_groups(config) == []


def test_openssl_default_list_shape_has_no_findings():
    # OpenSSL 3.5's own default list: prefixes, spaces around "/", four tuples.
    config = (
        "Groups = ?*X25519MLKEM768 / ?*X25519:?secp256r1 / "
        "?X448:?secp384r1:?secp521r1 / ?ffdhe2048:?ffdhe3072"
    )
    assert lint_openssl_groups(config) == []


def test_openssl_missing_hybrid_is_blocker():
    findings = lint_openssl_groups("Groups = X25519:secp256r1")
    assert len(findings) == 1
    assert findings[0].severity == "blocker"
    assert findings[0].rule == "hybrid-missing"
    assert HYBRID in findings[0].message


def test_nginx_missing_hybrid_is_blocker():
    findings = lint_nginx_groups("    ssl_ecdh_curve X25519:secp256r1;")
    assert len(findings) == 1
    assert findings[0].severity == "blocker"
    assert findings[0].rule == "hybrid-missing"


def test_classical_before_hybrid_is_major():
    findings = lint_openssl_groups("Groups = X25519:X25519MLKEM768:secp256r1")
    majors = [f for f in findings if f.rule == "hybrid-not-first-preference"]
    assert len(majors) == 1
    assert majors[0].severity == "major"


def test_classical_sharing_hybrid_tuple_is_major():
    # One tuple: a client that sent only an X25519 key share gets X25519.
    findings = lint_openssl_groups("Groups = X25519MLKEM768:X25519:secp256r1")
    majors = [f for f in findings if f.rule == "hybrid-not-first-preference"]
    assert len(majors) == 1
    assert majors[0].message.endswith("negotiate X25519")


def test_classical_tuple_before_hybrid_is_major():
    findings = lint_nginx_groups("    ssl_ecdh_curve secp256r1/X25519MLKEM768;")
    majors = [f for f in findings if f.rule == "hybrid-not-first-preference"]
    assert len(majors) == 1
    assert majors[0].message.endswith("negotiate secp256r1")


def test_names_compare_without_case_and_aliases_count_as_classical():
    # OpenSSL 3.5 group names are case-insensitive; prime256v1 is P-256.
    findings = lint_openssl_groups("Groups = x25519mlkem768:prime256v1")
    majors = [f for f in findings if f.rule == "hybrid-not-first-preference"]
    assert len(majors) == 1
    assert majors[0].message.endswith("negotiate prime256v1")


def test_classical_names_compare_without_case():
    findings = lint_openssl_groups("Groups = X25519MLKEM768:SECP256R1")
    majors = [f for f in findings if f.rule == "hybrid-not-first-preference"]
    assert len(majors) == 1
    assert majors[0].message.endswith("negotiate SECP256R1")


def test_brainpool_counts_as_classical():
    findings = lint_openssl_groups("Groups = brainpoolP256r1tls13:X25519MLKEM768")
    assert [f.rule for f in findings] == ["hybrid-not-first-preference"]


def test_one_ordering_finding_is_enough():
    # X25519 sits in an earlier tuple and secp256r1 shares the hybrid's.
    findings = lint_openssl_groups("Groups = X25519/secp256r1:X25519MLKEM768")
    assert [f.rule for f in findings] == ["hybrid-not-first-preference"]


def test_removed_hybrid_is_blocker():
    # "-name" removes the group from the list built so far, here the hybrid.
    findings = lint_openssl_groups("Groups = X25519MLKEM768/X25519:-X25519MLKEM768")
    assert [(f.severity, f.rule) for f in findings] == [("blocker", "hybrid-missing")]


def test_removed_classical_group_is_not_counted():
    assert lint_openssl_groups("Groups = X25519:X25519MLKEM768:-X25519") == []


def test_removal_before_a_group_is_listed_does_nothing():
    # OpenSSL removes only from the list so far, so the later X25519 is added
    # to the hybrid's tuple.
    findings = lint_openssl_groups("Groups = X25519MLKEM768:-X25519:X25519")
    assert [f.rule for f in findings] == ["hybrid-not-first-preference"]


def test_removal_applies_to_every_name_for_the_group():
    # prime256v1 and P-256 name one group, so this removes P-256.
    assert lint_openssl_groups("Groups = X25519MLKEM768:P-256:-prime256v1") == []


def test_removal_takes_every_listed_copy():
    # OpenSSL ignores the repeated x25519, so removing X25519 leaves the hybrid.
    assert lint_openssl_groups("Groups = X25519MLKEM768:X25519:x25519:-X25519") == []


def test_removal_by_another_name_for_p384():
    assert lint_openssl_groups("Groups = X25519MLKEM768:P-384:-secp384r1") == []


# Every alias set in OpenSSL 3.5.0's group table (providers/common/capabilities.c).
OPENSSL_ALIAS_SETS = [
    ("secp256r1", "prime256v1", "P-256"), ("secp384r1", "P-384"),
    ("secp521r1", "P-521"), ("secp192r1", "prime192v1", "P-192"),
    ("secp224r1", "P-224"), ("sect163k1", "K-163"), ("sect163r2", "B-163"),
    ("sect233k1", "K-233"), ("sect233r1", "B-233"), ("sect283k1", "K-283"),
    ("sect283r1", "B-283"), ("sect409k1", "K-409"), ("sect409r1", "B-409"),
    ("sect571k1", "K-571"), ("sect571r1", "B-571"),
]


@pytest.mark.parametrize(
    "first,second",
    [(a, b) for names in OPENSSL_ALIAS_SETS for a in names for b in names if a != b],
)
def test_duplicates_follow_the_whole_alias_table(first, second):
    findings = lint_openssl_groups(f"Groups = X25519MLKEM768/{first}:{second}")
    assert [f.rule for f in findings] == ["duplicate-codepoint"]


def test_brainpool_tls12_and_tls13_groups_are_not_aliases():
    # Different codepoints in OpenSSL's table, although one names the other.
    config = "Groups = X25519MLKEM768/brainpoolP256r1:brainpoolP256r1tls13"
    assert lint_openssl_groups(config) == []


def test_removed_group_can_be_listed_again():
    # secp256r1 is removed under its P-256 name and listed again as prime256v1:
    # one group, back in the hybrid's tuple, and no duplicate.
    findings = lint_openssl_groups("Groups = X25519MLKEM768:secp256r1:-P-256:prime256v1")
    assert [f.rule for f in findings] == ["hybrid-not-first-preference"]
    assert findings[0].message.endswith("negotiate prime256v1")


def test_duplicates_compare_without_case_and_across_aliases():
    findings = lint_nginx_groups("    ssl_ecdh_curve X25519MLKEM768/x25519:X25519;")
    assert [f.rule for f in findings] == ["duplicate-codepoint"]
    findings = lint_openssl_groups("Groups = X25519MLKEM768/X25519:secp256r1:prime256v1")
    assert [f.rule for f in findings] == ["duplicate-codepoint"]


def test_duplicate_codepoint_is_nit():
    findings = lint_nginx_groups("    ssl_ecdh_curve X25519MLKEM768/X25519:X25519;")
    nits = [f for f in findings if f.rule == "duplicate-codepoint"]
    assert len(nits) == 1
    assert nits[0].severity == "nit"


def test_openssl_no_directive_raises_valueerror():
    with pytest.raises(ValueError):
        lint_openssl_groups("# no Groups directive here")


def test_nginx_no_directive_raises_valueerror():
    with pytest.raises(ValueError):
        lint_nginx_groups("server { listen 443 ssl; }")


def test_findings_carry_directive_line_number():
    config = "\n# comment\n\nGroups = X25519:secp256r1\n"
    findings = lint_openssl_groups(config)
    assert findings[0].line_number == 4
