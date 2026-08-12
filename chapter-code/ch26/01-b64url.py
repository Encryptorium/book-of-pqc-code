# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 26: Crypto agility
# Section: "A JWT signer that cannot move"
# https://book.encryptorium.com/part-5-migration-deployment/ch26-crypto-agility/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch26/01-b64url.py

# Block 1: brittle vs agile JWT signer, stdlib only.
import base64, hashlib, hmac, json

SECRET = b"pedagogical-secret-bytes-only"

def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

# --- brittle: HS256 hard-coded everywhere ---
def sign_brittle(payload):
    header = b64url(b'{"typ":"JWT"}')
    body = b64url(json.dumps(payload).encode())
    signed = f"{header}.{body}".encode()
    sig = hmac.new(SECRET, signed, hashlib.sha256).digest()
    return f"{header}.{body}.{b64url(sig)}"

def verify_brittle(token):
    header, body, sig_in = token.split(".")
    signed = f"{header}.{body}".encode()
    expected = b64url(hmac.new(SECRET, signed, hashlib.sha256).digest())
    return hmac.compare_digest(sig_in, expected)

# --- agile: identifier registry, header-driven verification ---
REGISTRY = {
    "HS256": (hashlib.sha256, False),
    "HS384": (hashlib.sha384, False),
    "HS512": (hashlib.sha512, False),
    "HS1":   (hashlib.sha1,   True),     # True = deprecated
}

def sign_agile(payload, alg):
    hash_fn, deprecated = REGISTRY[alg]
    if deprecated:
        raise ValueError(f"algorithm {alg} is deprecated")
    header = b64url(json.dumps({"typ": "JWT", "alg": alg}).encode())
    body = b64url(json.dumps(payload).encode())
    signed = f"{header}.{body}".encode()
    sig = hmac.new(SECRET, signed, hash_fn).digest()
    return f"{header}.{body}.{b64url(sig)}"

def verify_agile(token):
    header, body, sig_in = token.split(".")
    alg = json.loads(base64.urlsafe_b64decode(header + "==="))["alg"]
    if alg not in REGISTRY:
        return False
    hash_fn, deprecated = REGISTRY[alg]
    if deprecated:
        return False
    signed = f"{header}.{body}".encode()
    expected = b64url(hmac.new(SECRET, signed, hash_fn).digest())
    return hmac.compare_digest(sig_in, expected)

payload = {"sub": "user-42"}
brittle = sign_brittle(payload)
agile256 = sign_agile(payload, "HS256")
agile512 = sign_agile(payload, "HS512")
print(verify_brittle(brittle), verify_agile(agile256), verify_agile(agile512))
# ==> True True True
