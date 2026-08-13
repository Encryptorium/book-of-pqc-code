# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 41: Governance, hard forks, and migration case studies
# Section: "Quantify the cross-stakeholder activation window"
# https://book.encryptorium.com/part-7-pqc-blockchain/ch41-governance-hard-forks-case-studies/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch41/02-quantify-the-cross-stakeholder-activation-window.py

# Block 2: pedagogical slice of governance.fork_choreography
# (stdlib only). Constants are illustrative anchors at chain-tip
# 2026; a production hard fork measures against its own
# coordination history.

# Bitcoin BIP cycle.
BIP_PROPOSAL_REVIEW_WEEKS = 16
BIP_ECONOMIC_ACTOR_LEAD_WEEKS = 26

# Ethereum All Core Devs cycle.
ACD_PROPOSAL_REVIEW_WEEKS = 12
ACD_CLIENT_TEAM_RELEASE_WEEKS = 8

# Cross-cycle critical-path component. Chain-neutral name: Ethereum-
# side validator-set rotation + Bitcoin-side full-node / miner /
# mining-pool readiness against the activation height.
CONSENSUS_PARTICIPANT_UPDATE_WEEKS = 4

# Off-critical-path parallel component.
INFRASTRUCTURE_LEAD_WEEKS = 8

btc_window_weeks = (
    BIP_PROPOSAL_REVIEW_WEEKS
    + BIP_ECONOMIC_ACTOR_LEAD_WEEKS
    + CONSENSUS_PARTICIPANT_UPDATE_WEEKS
)
eth_window_weeks = (
    ACD_PROPOSAL_REVIEW_WEEKS
    + ACD_CLIENT_TEAM_RELEASE_WEEKS
    + CONSENSUS_PARTICIPANT_UPDATE_WEEKS
)

print(f"bitcoin_bip_cycle activation_window_weeks={btc_window_weeks}")
print(f"ethereum_acd_cycle activation_window_weeks={eth_window_weeks}")
print(f"bitcoin years={btc_window_weeks/52:.3f}")
print(f"ethereum years={eth_window_weeks/52:.3f}")
print(f"infrastructure_lead_weeks (off critical path)={INFRASTRUCTURE_LEAD_WEEKS}")
# ==> bitcoin_bip_cycle activation_window_weeks=46
# ==> ethereum_acd_cycle activation_window_weeks=24
# ==> bitcoin years=0.885
# ==> ethereum years=0.462
# ==> infrastructure_lead_weeks (off critical path)=8
