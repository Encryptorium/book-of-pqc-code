# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 28: TLS 1.3 migration
# Section: "Server configuration"
# https://book.encryptorium.com/part-5-migration-deployment/ch28-tls-migration/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch28/02-lint-nginx.py

# Block 2: pedagogical slice of lint_nginx_groups (stdlib only).
import re

HYBRID = "X25519MLKEM768"

def lint_nginx(config_text):
    for i, raw in enumerate(config_text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"ssl_ecdh_curve\s+(.+)$", line)
        if m:
            groups = [g.strip() for g in m.group(1).rstrip(";").split(":")]
            if HYBRID not in groups:
                return [("blocker", "hybrid-missing", i)]
            return []
    raise ValueError("no ssl_ecdh_curve directive")

good = "server {\n    ssl_ecdh_curve X25519MLKEM768:X25519:secp256r1;\n}"
bad = "server {\n    ssl_ecdh_curve X25519:secp256r1;\n}"

print("good:", lint_nginx(good))
print("bad:", lint_nginx(bad))
# ==> good: []
# ==> bad: [('blocker', 'hybrid-missing', 2)]
