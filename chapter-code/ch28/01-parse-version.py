# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 28: TLS 1.3 migration
# Section: "Fleet assessment"
# https://book.encryptorium.com/part-5-migration-deployment/ch28-tls-migration/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch28/01-parse-version.py

# Block 1: pedagogical slice of fleet_assessment.classify (stdlib only).
LIBRARY_MINIMUMS = {
    "openssl": (3, 5, 0),
    "go-crypto-tls": (1, 24, 0),
}

def parse_version(value):
    return tuple(int(p) for p in value.split("."))

def classify(inventory):
    rows = []
    for component, library, version in inventory:
        parsed = parse_version(version)
        minimum = LIBRARY_MINIMUMS.get(library)
        if minimum is None:
            rows.append((component, library, version, "blocked"))
        elif parsed >= minimum:
            rows.append((component, library, version, "ready"))
        else:
            rows.append((component, library, version, "gated"))
    return rows

inventory = [
    ("edge-lb", "openssl", "3.5.2"),
    ("app-server", "openssl", "3.3.0"),
    ("backend-peer", "go-crypto-tls", "1.24.1"),
    ("sidecar", "envoy", "1.30.0"),
]

for row in classify(inventory):
    print(" | ".join(str(x) for x in row))
# ==> edge-lb | openssl | 3.5.2 | ready
# ==> app-server | openssl | 3.3.0 | gated
# ==> backend-peer | go-crypto-tls | 1.24.1 | ready
# ==> sidecar | envoy | 1.30.0 | blocked
