"""Mock five-touchpoint application used to drive the CBOM generator.

The module declares the cryptographic metadata that a small Python web
service would expose if one went through its source, its deployment
config, and its runtime dependencies by hand. It does not perform any
cryptographic operation; it is the inventory view of the app, not the
app itself.

Five touchpoints are declared:

1. ``tls_endpoint_api``           -- the external TLS termination on a
                                      public API, cipher suite
                                      ECDHE-ECDSA-AES256-GCM-SHA384.
2. ``jwt_signing``                -- RS256 JWT signing for session
                                      tokens (RSA-2048).
3. ``password_hashing``           -- PBKDF2-HMAC-SHA256 for user
                                      passwords, 600 000 iterations.
4. ``webhook_hmac``               -- HMAC-SHA256 for outgoing webhook
                                      payload signing.
5. ``blockchain_validator_sig``   -- ECDSA-secp256k1 signing key the
                                      service uses to author Layer 1
                                      blockchain transactions in its
                                      role as a chain operator.

Every touchpoint is a ``dict`` with a fixed schema:

* ``name``          stable identifier, lowercase snake_case.
* ``location``      free-form string locating the use in the
                    architecture.
* ``algorithm``     canonical IANA / NIST-style name.
* ``primitive``     CycloneDX cryptoProperties primitive
                    ("signature", "key-agree", "kdf", "mac", "encrypt").
* ``parameters``    dict of algorithm-specific parameters.
* ``families``      list of short family labels used by the
                    vulnerability lookup.
* ``exposure``      adversarial-visibility label ("public" or
                    "internal"); the priority matrix reads this,
                    not the key's physical location.
* ``deployed``      ISO-8601 date the touchpoint first went live.
* ``owner``         team owning the touchpoint.
"""

from __future__ import annotations

from typing import Any


TOUCHPOINTS: list[dict[str, Any]] = [
    {
        "name": "tls_endpoint_api",
        "location": "edge/api.example.com",
        "algorithm": "ECDHE-ECDSA-AES256-GCM-SHA384",
        "primitive": "key-agree",
        "parameters": {
            "tls_version": "1.2",
            "curve": "P-256",
            "aead": "AES-256-GCM",
            "signature": "ECDSA-P-256",
        },
        "families": ["ECDHE", "ECDSA", "AES", "SHA-384"],
        "exposure": "public",
        "deployed": "2022-06-15",
        "owner": "platform-team",
    },
    {
        "name": "jwt_signing",
        "location": "auth/token-service",
        "algorithm": "RS256",
        "primitive": "signature",
        "parameters": {
            "rsa_modulus_bits": 2048,
            "hash": "SHA-256",
        },
        "families": ["RSA", "SHA-256"],
        "exposure": "internal",
        "deployed": "2023-01-10",
        "owner": "auth-team",
    },
    {
        "name": "password_hashing",
        "location": "auth/user-service",
        "algorithm": "PBKDF2-HMAC-SHA256",
        "primitive": "kdf",
        "parameters": {
            "iterations": 600_000,
            "salt_bytes": 16,
            "dk_bytes": 32,
            "hash": "SHA-256",
        },
        "families": ["PBKDF2", "HMAC", "SHA-256"],
        "exposure": "internal",
        "deployed": "2024-03-01",
        "owner": "auth-team",
    },
    {
        "name": "webhook_hmac",
        "location": "webhooks/outgoing-signer",
        "algorithm": "HMAC-SHA256",
        "primitive": "mac",
        "parameters": {
            "key_bytes": 32,
            "hash": "SHA-256",
        },
        "families": ["HMAC", "SHA-256"],
        "exposure": "internal",
        "deployed": "2023-08-20",
        "owner": "integrations-team",
    },
    {
        "name": "blockchain_validator_sig",
        "location": "chain/validator-keystore",
        "algorithm": "ECDSA-secp256k1",
        "primitive": "signature",
        "parameters": {
            "curve": "secp256k1",
            "hash": "SHA-256",
        },
        "families": ["ECDSA", "SHA-256"],
        "exposure": "public",
        "deployed": "2024-01-15",
        "owner": "chain-ops",
    },
]
