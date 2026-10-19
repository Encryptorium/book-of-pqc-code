"""Chapter 37 toolkit for the Layer 1 signature migration.

Three utilities backing the chapter's running example on the Strand
chain (Ch 36):

- ``byte_budget`` reports per-transaction signature bytes, per-block
  Bitcoin-weight throughput, and per-transaction Ethereum calldata
  gas across a fixed four-element candidate set.
- ``throughput_compare`` ranks candidates by transactions per block
  under either the Bitcoin weight budget or the Ethereum gas budget.
- ``composite_overhead`` compares a classical+PQ composite signature
  against the underlying primitives in isolation.

The candidate set, the Bitcoin block weight limit (4 million weight
units), and the Ethereum block gas limit (60 million, the client
default EIP-7935 recommends) are deliberately fixed.
The chapter's two inline blocks operate over these constants.
"""

from . import byte_budget, composite_overhead, throughput_compare

__all__ = ["byte_budget", "composite_overhead", "throughput_compare"]
