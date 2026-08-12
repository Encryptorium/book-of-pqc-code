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
    # EXERCISE: implement this function.
    #
    # Three rules over the parsed group list, all reported against the
    # directive's line number. If the hybrid name is absent, emit a single
    # blocker with rule 'hybrid-missing' and return immediately; the
    # ordering and duplicate rules say nothing useful about a list that does
    # not contain it. Otherwise find the hybrid's index and scan the entries
    # before it: the first one that is a classical group is a major with
    # rule 'hybrid-not-first-preference', and one finding is enough, so stop
    # after it. Finally walk the whole list tracking names already seen and
    # emit a nit with rule 'duplicate-codepoint' for each repeat.
    #
    # Reference: Chapter 28, 'Server configuration'
    #
    # Proved by:
    #   tests/ch28/test_tls_config_lint.py
    raise NotImplementedError("exercise: _lint_groups")


def lint_openssl_groups(config_text: str) -> list[Finding]:
    """Lint an OpenSSL-style ``Groups=`` directive for X25519MLKEM768 hygiene."""
    # EXERCISE: implement this function.
    #
    # Find the OpenSSL 'Groups =' directive, capturing everything after the
    # equals sign, then split the value on colons and lint the resulting
    # list. Raise ValueError when the directive is absent rather than
    # returning an empty finding list: a config with no group directive at
    # all is a different situation from one whose groups are wrong, and the
    # caller has to tell them apart.
    #
    # Reference: Chapter 28, 'Server configuration'
    #
    # Proved by:
    #   tests/ch28/test_tls_config_lint.py
    raise NotImplementedError("exercise: lint_openssl_groups")


def lint_nginx_groups(config_text: str) -> list[Finding]:
    """Lint an nginx ``ssl_ecdh_curve`` directive for X25519MLKEM768 hygiene."""
    # EXERCISE: implement this function.
    #
    # The same shape as the OpenSSL entry point against nginx's
    # 'ssl_ecdh_curve' directive, which is whitespace-separated rather than
    # equals-separated and ends in a semicolon the splitter strips. nginx
    # delegates group selection to its OpenSSL backend, so the value is the
    # same colon-separated preference list and the same three rules apply
    # unchanged. Raise ValueError when no such directive is present.
    #
    # Reference: Chapter 28, 'Server configuration'
    #
    # Proved by:
    #   tests/ch28/test_tls_config_lint.py
    raise NotImplementedError("exercise: lint_nginx_groups")
