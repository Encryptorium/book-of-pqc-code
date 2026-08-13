"""Chapter 32: toy implementations of the four commitment-scheme families.

Four modules, one per commitment family analyzed at L2 of the four-layer
decomposition (Chapter 31):

- ``toy_kzg``: pedagogical KZG-like polynomial commitment with simulated
  Shor trapdoor recovery and opening forgery.
- ``merkle``: q-ary Merkle commitment with configurable hash output width
  and BHT/CNPS quantum-collision-bit helpers.
- ``fri``: toy FRI commitment with Reed-Solomon codeword construction,
  folding rounds, and query-based consistency checks.
- ``lattice_pcs``: Module-SIS vector commitment demonstrating the
  binding reduction and hiding-via-error pattern.

Every module is pedagogical. Production constructions of KZG, FRI, and
lattice PCS require machinery (pairing-friendly curves, production
Fiat-Shamir compilations, full evaluation protocols) that Chapter 32
deliberately does not build. The purpose is to expose the attack
surface and design pattern of each family, not to produce working
cryptographic primitives.
"""

from . import toy_kzg
from . import merkle
from . import fri
from . import lattice_pcs

__all__ = ["toy_kzg", "merkle", "fri", "lattice_pcs"]
