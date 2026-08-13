# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 41: Governance, hard forks, and migration case studies
# Section: "Decompose the stakeholder set into three groups and pick a per-action work-stream owner"
# https://book.encryptorium.com/part-7-pqc-blockchain/ch41-governance-hard-forks-case-studies/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch41/01-decompose-the-stakeholder-set-into-three-groups.py

# Block 1: pedagogical slice of governance.stakeholder_matrix
# (stdlib only).
STAKEHOLDERS = (
    "protocol-developer",
    "validator-operator",
    "infrastructure-service-provider",
)
ACTIONS = ("propose", "audit", "deploy")

# (work_stream_owner, coordination_role) per (stakeholder, action).
MATRIX = {
    ("protocol-developer", "propose"): (
        "core-development-team", "primary",
    ),
    ("protocol-developer", "audit"): (
        "core-development-team", "primary",
    ),
    ("protocol-developer", "deploy"): (
        "core-development-team", "co-owner",
    ),
    ("validator-operator", "propose"): (
        "validator-coordinator", "downstream-consumer",
    ),
    ("validator-operator", "audit"): (
        "validator-coordinator", "co-owner",
    ),
    ("validator-operator", "deploy"): (
        "validator-coordinator", "primary",
    ),
    ("infrastructure-service-provider", "propose"): (
        "rpc-provider-and-indexer-team", "downstream-consumer",
    ),
    ("infrastructure-service-provider", "audit"): (
        "rpc-provider-and-indexer-team", "co-owner",
    ),
    ("infrastructure-service-provider", "deploy"): (
        "rpc-provider-and-indexer-team", "primary",
    ),
}

primaries_per_action = {action: [] for action in ACTIONS}
for (stakeholder, action), (owner, role) in MATRIX.items():
    if role == "primary":
        primaries_per_action[action].append(stakeholder)

for action in ACTIONS:
    print(f"{action}: {primaries_per_action[action]}")
# ==> propose: ['protocol-developer']
# ==> audit: ['protocol-developer']
# ==> deploy: ['validator-operator', 'infrastructure-service-provider']
