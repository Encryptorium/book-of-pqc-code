"""Toy SIDH key exchange over supersingular elliptic curves.

This package implements a pedagogical SIDH (Supersingular Isogeny
Diffie-Hellman) key exchange at p = 431.  SIDH was broken by Castryck
and Decru in 2022; this code is for educational purposes only.
"""

from isogenies.sidh import sidh_exchange, sidh_params

__all__ = ["sidh_exchange", "sidh_params"]
