"""Chapter 41 toolkit: governance, hard forks, and migration case studies.

Three modules:

- ``stakeholder_matrix`` for the three-stakeholder by three-action
  decomposition (protocol developer, validator operator,
  infrastructure service provider; propose, audit, deploy). The
  three stakeholders are this chapter's own taxonomy, run as work
  streams under the Ch 30 owner / cadence / deliverable framing.
  Reports the per-cell work-stream owner and a one-line
  coordination tempo summary.
- ``fork_choreography`` for the cross-stakeholder activation-window
  arithmetic. Distinguishes the Bitcoin BIP cycle from the Ethereum
  All-Core-Devs cycle and reports the activation-window length per
  stakeholder action under named cycle constants.
- ``governance_mosca`` for the Mosca-window calculator specialized
  to the Strand governance surface (X=4, Y=3 from the Ch 36
  fixture), with three Z scenarios named narrow, central, and wide.

Standard library only. No third-party dependencies.
"""
