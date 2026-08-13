"""Chapter 40 toolkit: ZK rollup verifier-contract migration.

Three modules:

- ``verifier_layers`` for the Ch 31 four-layer decomposition
  (L1 arithmetization, L2 commitment + consistency, L3 protocol
  logic, L4 non-interactivity + extraction) over a per-layer
  candidate set, reporting post-quantum status per cell.
- ``gas_budget`` for the per-proof gas-cost arithmetic across
  candidate verifier configurations against Ethereum's per-block
  gas budget.
- ``verifier_mosca`` for the Mosca-window calculator specialized
  to the Strand on-chain-verifier surface (X=3, Y=2 from the
  Ch 36 fixture), with three Z scenarios named narrow, central,
  and wide.

Standard library only. No third-party dependencies.
"""
