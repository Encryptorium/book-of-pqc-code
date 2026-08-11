# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 25: Inventory first: CBOM
# Section: "From source code to CBOM JSON"
# https://book.encryptorium.com/part-5-migration-deployment/ch25-inventory-first-cbom/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch25/03-status.py

# Block 3: build the CycloneDX component for one touchpoint.
import json

VULNERABLE = "vulnerable"
# Reduced table for this single JWT example; the full package uses
# the shared three-family table from Block 2.
FAMILIES = {"RSA": VULNERABLE, "SHA-256": "grover-only"}

def status(family): return FAMILIES.get(family, "unknown")

def touchpoint_status(families):
    if not families: return "unknown"
    ordered = [status(f) for f in families]
    if VULNERABLE in ordered: return VULNERABLE
    if "unknown" in ordered: return "unknown"
    return "grover-only"

def parameter_set(params):
    # Sort keys so the identifier is stable across versions and a
    # CBOM-to-CBOM diff is meaningful.
    return "; ".join(f"{k}={params[k]}" for k in sorted(params))

def component(touchpoint):
    return {
        "type": "cryptographic-asset",
        "bom-ref": f"crypto:{touchpoint['name']}",
        "name": touchpoint["algorithm"],
        "cryptoProperties": {
            "assetType": "algorithm",
            "algorithmProperties": {
                "primitive": touchpoint["primitive"],
                "parameterSetIdentifier": parameter_set(touchpoint["parameters"]),
                "executionEnvironment": "software-plain-ram",
            },
        },
        "properties": [
            {"name": "encryptorium:location", "value": touchpoint["location"]},
            {"name": "encryptorium:exposure", "value": touchpoint["exposure"]},
            {"name": "encryptorium:owner", "value": touchpoint["owner"]},
            {"name": "encryptorium:deployed", "value": touchpoint["deployed"]},
            {"name": "encryptorium:quantum-status", "value": touchpoint_status(touchpoint["families"])},
            {"name": "encryptorium:families", "value": ",".join(touchpoint["families"])},
        ],
    }

jwt = {
    "name": "jwt_signing", "location": "auth/token-service",
    "algorithm": "RS256", "primitive": "signature",
    "parameters": {"rsa_modulus_bits": 2048, "hash": "SHA-256"},
    "families": ["RSA", "SHA-256"], "exposure": "internal",
    "deployed": "2023-01-10", "owner": "auth-team",
}
print(json.dumps(component(jwt), indent=2))
# ==> {
# ==>   "type": "cryptographic-asset",
# ==>   "bom-ref": "crypto:jwt_signing",
# ==>   "name": "RS256",
# ==>   "cryptoProperties": {
# ==>     "assetType": "algorithm",
# ==>     "algorithmProperties": {
# ==>       "primitive": "signature",
# ==>       "parameterSetIdentifier": "hash=SHA-256; rsa_modulus_bits=2048",
# ==>       "executionEnvironment": "software-plain-ram"
# ==>     }
# ==>   },
# ==>   "properties": [
# ==>     {
# ==>       "name": "encryptorium:location",
# ==>       "value": "auth/token-service"
# ==>     },
# ==>     {
# ==>       "name": "encryptorium:exposure",
# ==>       "value": "internal"
# ==>     },
# ==>     {
# ==>       "name": "encryptorium:owner",
# ==>       "value": "auth-team"
# ==>     },
# ==>     {
# ==>       "name": "encryptorium:deployed",
# ==>       "value": "2023-01-10"
# ==>     },
# ==>     {
# ==>       "name": "encryptorium:quantum-status",
# ==>       "value": "vulnerable"
# ==>     },
# ==>     {
# ==>       "name": "encryptorium:families",
# ==>       "value": "RSA,SHA-256"
# ==>     }
# ==>   ]
# ==> }
