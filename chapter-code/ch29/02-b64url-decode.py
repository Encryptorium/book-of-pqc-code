# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 29: PKI and code signing
# Section: "JWKS and JWT migration"
# https://book.encryptorium.com/part-5-migration-deployment/ch29-pki-code-signing/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch29/02-b64url-decode.py

# Block 2: pedagogical slice of pki_migration.jwks_verifier.verify_composite_jwt (stdlib only).
import base64
import json

COMPOSITE_KTY = "OKP-COMPOSITE"
COMPOSITE_ALG = "Ed25519+ML-DSA-65"

def b64url_decode(s):
    pad = (-len(s)) % 4
    return base64.urlsafe_b64decode(s + ("=" * pad))

def find_jwk(jwks, kid):
    for jwk in jwks["keys"]:
        if jwk.get("kid") == kid:
            return jwk
    raise KeyError(f"no JWK with kid={kid!r}")

def resolve_composite(jwt_compact, jwks):
    parts = jwt_compact.split(".")
    if len(parts) != 3:
        raise ValueError("JWT must have three dot-separated parts")
    header_b64, payload_b64, sig_b64 = parts
    header = json.loads(b64url_decode(header_b64))
    kid = header.get("kid")
    if kid is None:
        raise ValueError("JWT header missing 'kid'")
    jwk = find_jwk(jwks, kid)
    if jwk.get("kty") != COMPOSITE_KTY:
        raise ValueError(f"kid={kid!r} kty is not {COMPOSITE_KTY}")
    if jwk.get("alg") != COMPOSITE_ALG or header.get("alg") != COMPOSITE_ALG:
        raise ValueError(f"alg mismatch: jwk={jwk.get('alg')!r} header={header.get('alg')!r}")
    pk = b64url_decode(jwk["mldsa_pk"]) + b64url_decode(jwk["ed_pk"])
    signed = f"{header_b64}.{payload_b64}".encode("ascii")
    return pk, signed, b64url_decode(sig_b64)

jwks = {
    "keys": [
        {"kty": "RSA", "alg": "RS256", "kid": "rs256-2023", "n": "AA", "e": "AQAB"},
        {"kty": COMPOSITE_KTY, "alg": COMPOSITE_ALG, "kid": "composite-2026",
         "mldsa_pk": "AA", "ed_pk": "AA"},
    ],
}
# header = {"kid":"composite-2026","alg":"Ed25519+ML-DSA-65"}
jwt = ("eyJhbGciOiJFZDI1NTE5K01MLURTQS02NSIsImtpZCI6ImNvbXBvc2l0ZS0yMDI2In0"
       ".eyJzdWIiOiJhIn0.AA")

pk, signed, sig = resolve_composite(jwt, jwks)
print("pk len:", len(pk), "signed len:", len(signed), "sig len:", len(sig))
# ==> pk len: 2 signed len: 83 sig len: 1
