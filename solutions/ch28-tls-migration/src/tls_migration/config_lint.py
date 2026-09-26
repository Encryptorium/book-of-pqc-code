"""Configuration lint for X25519MLKEM768 advertisement in TLS server configs.

Two entry points:

- ``lint_openssl_groups`` parses a ``Groups=`` line from an OpenSSL
  configuration-file snippet.
- ``lint_nginx_groups`` parses the ``ssl_ecdh_curve`` directive from an
  nginx server-block snippet.

Both read the value as an OpenSSL 3.5 group list of explicit names:
tuples separated by ``/``, each a colon-separated list of group names,
with the ``?`` and ``*`` prefixes stripped and names compared without
regard to case. Entries apply left to right, as in OpenSSL: a ``-name``
entry removes that group, under any of its names, from the list built so
far, so a group not yet listed is unaffected and a later entry can list
it again. OpenSSL ignores a repeat of a group already listed, and the
lint keeps the repeat so it can report it. nginx hands an explicit list to OpenSSL unchanged,
so the syntax is the same. Neither entry point expands OpenSSL's
``DEFAULT`` keyword or nginx's ``auto``: a directive that relies on
them reads as ``hybrid-missing`` and has to be checked by hand. Nor
does either check that a name is one OpenSSL knows: OpenSSL rejects the
whole list over an unknown name that lacks the ``?`` prefix. Both
apply the same three rules:

- ``hybrid-missing`` (blocker): X25519MLKEM768 is in no tuple.
- ``hybrid-not-first-preference`` (major): a classical group OpenSSL 3.5
  offers in TLS 1.3 (X25519, X448, P-256, P-384 or P-521 under any of
  their names, a ``brainpool...tls13`` group, or an FFDHE group) shares
  X25519MLKEM768's tuple or sits in an earlier one. An
  OpenSSL 3.5 server works through the tuples in order and, within a
  tuple, takes a key share the client already sent before it asks for
  another, so a client that supports both groups can still negotiate
  the classical one.
- ``duplicate-codepoint`` (nit): a group appears more than once in the
  list, under the same name or under two of its names.

Malformed input (no directive at all) raises ``ValueError`` directly;
this is pedagogical tooling, not production code.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


HYBRID = "X25519MLKEM768"
CLASSICAL = (
    "X25519", "X448",
    "secp256r1", "secp384r1", "secp521r1", "prime256v1", "P-256", "P-384", "P-521",
    "brainpoolP256r1tls13", "brainpoolP384r1tls13", "brainpoolP512r1tls13",
    "ffdhe2048", "ffdhe3072", "ffdhe4096", "ffdhe6144", "ffdhe8192",
)
_CLASSICAL = {name.lower() for name in CLASSICAL}
# Every alias in OpenSSL 3.5.0's group table (providers/common/capabilities.c).
# OpenSSL resolves each name to its group before adding or removing it, so a
# removal or a duplicate is by group, not by name.
_ALIASES = {
    "prime256v1": "secp256r1", "p-256": "secp256r1",
    "p-384": "secp384r1", "p-521": "secp521r1",
    "prime192v1": "secp192r1", "p-192": "secp192r1", "p-224": "secp224r1",
    "k-163": "sect163k1", "b-163": "sect163r2", "k-233": "sect233k1",
    "b-233": "sect233r1", "k-283": "sect283k1", "b-283": "sect283r1",
    "k-409": "sect409k1", "b-409": "sect409r1", "k-571": "sect571k1",
    "b-571": "sect571r1",
}


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


def _split_groups(value: str) -> list[list[str]]:
    cleaned = value.rstrip(";").strip()
    tuples: list[list[str]] = []
    for part in cleaned.split("/"):
        names: list[str] = []
        tuples.append(names)
        for raw in part.split(":"):
            entry = raw.strip()
            name = entry.lstrip("?*-")
            if not name:
                continue
            if "-" in entry[:len(entry) - len(name)]:
                # Remove the group from the tuples built so far, as OpenSSL does.
                group = _ALIASES.get(name.lower(), name.lower())
                for listed in tuples:
                    listed[:] = [n for n in listed
                                 if _ALIASES.get(n.lower(), n.lower()) != group]
            else:
                names.append(name)
    return [names for names in tuples if names]


def _lint_groups(tuples: list[list[str]], line_number: int) -> list[Finding]:
    findings: list[Finding] = []
    hybrid = HYBRID.lower()
    hybrid_tuple = next(
        (i for i, names in enumerate(tuples) if hybrid in (n.lower() for n in names)), None
    )
    if hybrid_tuple is None:
        findings.append(Finding(
            severity="blocker",
            rule="hybrid-missing",
            message=f"{HYBRID} not present in group list",
            line_number=line_number,
        ))
        return findings

    for names in tuples[:hybrid_tuple + 1]:
        classical = next((n for n in names if n.lower() in _CLASSICAL), None)
        if classical is not None:
            findings.append(Finding(
                severity="major",
                rule="hybrid-not-first-preference",
                message=(
                    f"classical {classical} is in {HYBRID}'s tuple or an earlier one, "
                    f"so a client that supports both can negotiate {classical}"
                ),
                line_number=line_number,
            ))
            break

    seen: set[str] = set()
    for name in (n for names in tuples for n in names):
        group = _ALIASES.get(name.lower(), name.lower())
        if group in seen:
            findings.append(Finding(
                severity="nit",
                rule="duplicate-codepoint",
                message=f"{name} appears more than once in the group list",
                line_number=line_number,
            ))
        seen.add(group)
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
