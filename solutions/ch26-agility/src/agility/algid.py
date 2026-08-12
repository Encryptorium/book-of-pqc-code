"""Namespaced algorithm-identifier parsing (Chapter 26, Block 2).

An identifier packages the primitive, its parameter set, and any flags
into one string: ``RSA-PSS/SHA-256/salt=32``. The first segment is the
primitive; each later segment is either ``key=value`` or a bare flag,
which parses to ``True``.

The real identifier spaces this models are tighter or looser at either
end. TLS ``SignatureScheme`` codepoints are a fixed registry of
two-byte values; the CycloneDX 1.6 ``parameterSetIdentifier`` field that
Chapter 25 emits is free-form text. Both carry enough for a verifier to
route without the caller naming the primitive itself.
"""

from __future__ import annotations

from typing import Union


def parse_algid(algid: str) -> tuple[str, dict[str, Union[str, bool]]]:
    """Split a namespaced identifier into its primitive and parameters."""

    parts = algid.split("/")
    primitive = parts[0]
    params: dict[str, Union[str, bool]] = {}
    for kv in parts[1:]:
        k, _, v = kv.partition("=")
        params[k] = v if v else True
    return primitive, params
