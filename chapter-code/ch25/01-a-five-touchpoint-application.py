# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 25: Inventory first: CBOM
# Section: "A five-touchpoint application"
# https://book.encryptorium.com/part-5-migration-deployment/ch25-inventory-first-cbom/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch25/01-a-five-touchpoint-application.py

# Block 1: the five cryptographic touchpoints.
TOUCHPOINTS = [
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
        "parameters": {"rsa_modulus_bits": 2048, "hash": "SHA-256"},
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
        "parameters": {"key_bytes": 32, "hash": "SHA-256"},
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
        "parameters": {"curve": "secp256k1", "hash": "SHA-256"},
        "families": ["ECDSA", "SHA-256"],
        "exposure": "public",
        "deployed": "2024-01-15",
        "owner": "chain-ops",
    },
]

print(len(TOUCHPOINTS), [t["primitive"] for t in TOUCHPOINTS])
# ==> 5 ['key-agree', 'signature', 'kdf', 'mac', 'signature']
