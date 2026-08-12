"""Configuration lint for X25519MLKEM768 advertisement in TLS server configs.

Two entry points:

- ``lint_openssl_groups`` parses a ``Groups=`` line from an OpenSSL
  configuration-file snippet.
- ``lint_nginx_groups`` parses the ``ssl_ecdh_curve`` directive from an
  nginx server-block snippet.

Both apply the same three rules against the resulting group list:

- ``hybrid-missing`` (blocker): X25519MLKEM768 is not present.
- ``hybrid-not-first-preference`` (major): a classical group (X25519,
  secp256r1, secp384r1, secp521r1) appears before X25519MLKEM768, so
  clients that also offer X25519MLKEM768 will still negotiate the
  classical group per TLS 1.3 server-preference semantics.
- ``duplicate-codepoint`` (nit): a group name appears more than once in
  the list.

Malformed input (no directive at all) raises ``ValueError`` directly;
this is pedagogical tooling, not production code.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


HYBRID = "X25519MLKEM768"
CLASSICAL = ("X25519", "secp256r1", "secp384r1", "secp521r1", "P-256", "P-384", "P-521")


@dataclass(frozen=True)
class Finding:
    """One lint result for a configuration line."""

    severity: str
    rule: str
    message: str
    line_number: int


def _find_directive(config_text: str, pattern: str) -> tuple[int, str] | None:
    for i, raw in enumerate(config_text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(pattern, line)
        if match:
            return i, match.group(1).strip()
    return None


def _split_groups(value: str) -> list[str]:
    cleaned = value.rstrip(";").strip()
    return [g.strip() for g in cleaned.split(":") if g.strip()]


def _lint_groups(groups: list[str], line_number: int) -> list[Finding]:
    findings: list[Finding] = []
    if HYBRID not in groups:
        findings.append(Finding(
            severity="blocker",
            rule="hybrid-missing",
            message=f"{HYBRID} not present in group list",
            line_number=line_number,
        ))
        return findings

    hybrid_index = groups.index(HYBRID)
    for i in range(hybrid_index):
        if groups[i] in CLASSICAL:
            findings.append(Finding(
                severity="major",
                rule="hybrid-not-first-preference",
                message=(
                    f"{HYBRID} appears after classical {groups[i]}; "
                    "clients that also offer the hybrid will still negotiate the classical group"
                ),
                line_number=line_number,
            ))
            break

    seen: set[str] = set()
    for name in groups:
        if name in seen:
            findings.append(Finding(
                severity="nit",
                rule="duplicate-codepoint",
                message=f"{name} appears more than once in the group list",
                line_number=line_number,
            ))
        seen.add(name)
    return findings


def lint_openssl_groups(config_text: str) -> list[Finding]:
    """Lint an OpenSSL-style ``Groups=`` directive for X25519MLKEM768 hygiene."""
    found = _find_directive(config_text, r"Groups\s*=\s*(.+)$")
    if found is None:
        raise ValueError("no Groups= directive found in config text")
    line_number, value = found
    return _lint_groups(_split_groups(value), line_number)


def lint_nginx_groups(config_text: str) -> list[Finding]:
    """Lint an nginx ``ssl_ecdh_curve`` directive for X25519MLKEM768 hygiene."""
    found = _find_directive(config_text, r"ssl_ecdh_curve\s+(.+)$")
    if found is None:
        raise ValueError("no ssl_ecdh_curve directive found in config text")
    line_number, value = found
    return _lint_groups(_split_groups(value), line_number)
