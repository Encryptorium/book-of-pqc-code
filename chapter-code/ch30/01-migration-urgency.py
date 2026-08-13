# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 30: Running a PQ migration program
# Section: "Discovery and assessment (2025-2028)"
# https://book.encryptorium.com/part-5-migration-deployment/ch30-running-a-pq-migration-program/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch30/01-migration-urgency.py

# Block 1: pedagogical slice of migration_program.risk_rollup.migration_urgency (stdlib only).
# The score ranks quantum migration urgency, not general operational risk; a
# quantum-safe touchpoint can still have weak ownership, telemetry, or rollback
# discipline that this rollup does not measure.
QUANTUM_MULT = {"vulnerable": 3, "grover-only": 1, "quantum-safe": 0}
EXPOSURE_MULT = {"public": 2, "internal": 1}

WEIGHTS = {
    "inventory": 0.20,
    "data_sensitivity": 0.15,
    "standards_compliance": 0.10,
    "migration_readiness": 0.20,
    "vendor_supply_chain": 0.15,
    "timeline_urgency": 0.10,
    "governance_policy": 0.10,
}

CBOM = [
    {"name": "tls_endpoint_api", "quantum_status": "quantum-safe",
     "exposure": "public", "readiness": {d: 5 for d in WEIGHTS}},
    {"name": "jwt_signing", "quantum_status": "quantum-safe",
     "exposure": "internal", "readiness": {d: 5 for d in WEIGHTS}},
    {"name": "password_hashing", "quantum_status": "grover-only",
     "exposure": "internal",
     "readiness": {"inventory": 4, "data_sensitivity": 2,
                   "standards_compliance": 4, "migration_readiness": 3,
                   "vendor_supply_chain": 4, "timeline_urgency": 3,
                   "governance_policy": 4}},
    {"name": "webhook_hmac", "quantum_status": "grover-only",
     "exposure": "internal",
     "readiness": {"inventory": 4, "data_sensitivity": 3,
                   "standards_compliance": 4, "migration_readiness": 4,
                   "vendor_supply_chain": 4, "timeline_urgency": 4,
                   "governance_policy": 4}},
    {"name": "blockchain_validator_sig", "quantum_status": "vulnerable",
     "exposure": "public",
     "readiness": {"inventory": 4, "data_sensitivity": 2,
                   "standards_compliance": 1, "migration_readiness": 1,
                   "vendor_supply_chain": 2, "timeline_urgency": 1,
                   "governance_policy": 2}},
]

def migration_urgency(touchpoints, weights):
    scored = []
    for t in touchpoints:
        qm = QUANTUM_MULT[t["quantum_status"]]
        em = EXPOSURE_MULT[t["exposure"]]
        gap = sum((5 - t["readiness"][d]) * w for d, w in weights.items())
        scored.append((t["name"], qm * em * gap))
    scored.sort(key=lambda item: (-item[1], item[0]))
    return scored

for name, score in migration_urgency(CBOM, WEIGHTS):
    print(f"{name:<24} {score:.2f}")
# ==> blockchain_validator_sig 18.00
# ==> password_hashing         1.60
# ==> webhook_hmac             1.15
# ==> jwt_signing              0.00
# ==> tls_endpoint_api         0.00
