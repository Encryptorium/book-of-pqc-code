"""Chapter 38 toolkit for wallet derivation under post-quantum signing.

Three utilities backing the chapter's running example on the Strand
wallet surface (Ch 36):

- ``derivation_tree`` walks a BIP-32-style derivation path under a
  parameterized signature primitive and reports which BIP-32
  derivation properties (deterministic child pubkey from parent
  pubkey, watch-only wallets, hardened versus non-hardened) survive
  per primitive.
- ``custody_fit`` maps each (custody shape, primitive) pair in a
  6 x 4 matrix to a fit decision (fit, marginal, unfit) over the
  six-candidate set (the four from Ch 37 plus XMSS-MT and LMS).
- ``mosca_wallet`` specializes the Ch 36 Mosca-window calculation
  to the wallet surface and recommends a rotation cadence under
  a stated arrival scenario.

The candidate set, the four custody shapes, and the four cadence
options are deliberately fixed. The chapter's three inline blocks
operate over these constants.
"""

from . import custody_fit, derivation_tree, mosca_wallet

__all__ = ["custody_fit", "derivation_tree", "mosca_wallet"]
