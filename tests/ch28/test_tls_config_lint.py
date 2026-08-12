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
Groups = X25519MLKEM768:X25519:secp256r1
"""
    assert lint_openssl_groups(config) == []


def test_nginx_good_snippet_has_no_findings():
    config = """
server {
    listen 443 ssl;
    ssl_protocols TLSv1.3;
    ssl_ecdh_curve X25519MLKEM768:X25519:secp256r1;
}
"""
    assert lint_nginx_groups(config) == []


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


def test_duplicate_codepoint_is_nit():
    findings = lint_nginx_groups("    ssl_ecdh_curve X25519MLKEM768:X25519:X25519;")
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
