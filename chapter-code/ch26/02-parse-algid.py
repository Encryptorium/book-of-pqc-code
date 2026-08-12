# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 26: Crypto agility
# Section: "Math preliminaries: identifiers, MTI, deprecation signaling"
# https://book.encryptorium.com/part-5-migration-deployment/ch26-crypto-agility/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch26/02-parse-algid.py

# Block 2: a namespaced identifier parser.
def parse_algid(algid):
    parts = algid.split("/")
    primitive = parts[0]
    params = {}
    for kv in parts[1:]:
        k, _, v = kv.partition("=")
        params[k] = v if v else True
    return primitive, params

print(parse_algid("RSA-PSS/SHA-256/salt=32"))
print(parse_algid("ML-DSA-65"))
print(parse_algid("HMAC-SHA256/deprecated"))
# ==> ('RSA-PSS', {'SHA-256': True, 'salt': '32'})
# ==> ('ML-DSA-65', {})
# ==> ('HMAC-SHA256', {'deprecated': True})
