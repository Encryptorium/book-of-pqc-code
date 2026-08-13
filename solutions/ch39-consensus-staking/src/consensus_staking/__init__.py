"""Chapter 39 toolkit: consensus and staking signature migration.

Three modules:

- ``aggregation_overhead`` for the per-validator-set byte budget
  across the five-candidate set (BLS-BLS12-381 baseline, ML-DSA-65,
  SLH-DSA-128s, FN-DSA-512, threshold ML-DSA).
- ``threshold_compare`` for the threshold-scheme by candidate
  support matrix at chain-tip 2026.
- ``consensus_mosca`` for the Mosca-window calculator specialized
  to the Strand consensus surface (X=2, Y=1 from the Ch 36
  fixture).

Standard library only. No third-party dependencies.
"""
