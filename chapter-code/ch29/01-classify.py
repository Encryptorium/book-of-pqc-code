# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 29: PKI and code signing
# Section: "CA-hierarchy migration"
# https://book.encryptorium.com/part-5-migration-deployment/ch29-pki-code-signing/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch29/01-classify.py

# Block 1: pedagogical slice of pki_migration.chain_analyzer.analyze_chain (stdlib only).
CLASSICAL = {
    "1.2.840.113549.1.1.11",  # sha256WithRSAEncryption (RFC 8017)
    "1.2.840.10045.4.3.2",    # ecdsa-with-SHA256 (RFC 5758); P-256 default
    "1.2.840.10045.4.3.3",    # ecdsa-with-SHA384 (RFC 5758); P-384 default
    "1.3.101.112",            # id-Ed25519 (RFC 8410)
}
SINGLE_PQ = {
    "2.16.840.1.101.3.4.3.18",  # id-ml-dsa-65 (RFC 9881)
    "2.16.840.1.101.3.4.3.20",  # id-slh-dsa-sha2-128s (RFC 9909)
}
COMPOSITE = {
    "1.3.6.1.5.5.7.6.48",       # id-MLDSA65-Ed25519-SHA512 (Ch 27-settled)
}

def classify(oid):
    if oid in CLASSICAL:
        return "classical"
    if oid in SINGLE_PQ:
        return "single-pq"
    if oid in COMPOSITE:
        return "composite"
    return "unknown"

def analyze(chain):
    # chain is leaf-first: chain[0] is the leaf, chain[-1] is the root.
    classes = tuple(classify(oid) for oid in chain)
    unique = set(classes)
    if not classes:
        return classes, "empty"
    if "unknown" in unique:
        return classes, "unknown-oid-present"
    if unique == {"classical"}:
        return classes, "classical-only"
    if unique == {"single-pq"}:
        return classes, "single-pq-only"
    if unique == {"composite"}:
        return classes, "composite-only"
    leaf = classes[0]
    if leaf in {"composite", "single-pq"} and "classical" in unique:
        return classes, "mixed-classical-above-pq-leaf"   # deployment bug
    return classes, "mixed-transition"                    # rollout in progress

good = [
    "1.3.6.1.5.5.7.6.48",       # leaf, composite
    "1.3.6.1.5.5.7.6.48",       # intermediate, composite
    "1.3.6.1.5.5.7.6.48",       # root, composite
]
bug = [
    "1.3.6.1.5.5.7.6.48",       # leaf, composite
    "1.2.840.113549.1.1.11",    # intermediate, classical (RSA-SHA256)
    "1.3.6.1.5.5.7.6.48",       # root, composite
]
rollout = [
    "1.2.840.10045.4.3.2",      # leaf, classical (ECDSA-P256/SHA-256)
    "1.3.6.1.5.5.7.6.48",       # intermediate, composite
    "1.3.6.1.5.5.7.6.48",       # root, composite
]

print("good:", analyze(good)[1])
print("bug:", analyze(bug)[1])
print("rollout:", analyze(rollout)[1])
# ==> good: composite-only
# ==> bug: mixed-classical-above-pq-leaf
# ==> rollout: mixed-transition
