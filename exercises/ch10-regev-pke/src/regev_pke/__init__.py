"""Chapter 10: Regev encryption from scratch.

A pedagogical Python package for Regev's public-key encryption scheme
over flat LWE. Four public symbols:

- RegevParams: dataclass (n, q, m, noise_bound) with structural asserts
- keygen: sample (A, b = A s + e) and return ((A, b), s)
- encrypt: turn a message bit into a ciphertext (c1, c2)
- decrypt: round (c2 - c1 @ s) mod q to the nearer of 0 or floor(q/2)

The inline numpy code blocks of Chapter 10 are pedagogical slices of
these four functions. Chapter 11 rebuilds the same shape over
Module-LWE rather than importing it; nothing outside tests/ch10/
imports regev_pke.
"""

from .params import RegevParams
from .keygen import keygen
from .encrypt import encrypt
from .decrypt import decrypt

__all__ = [
    "RegevParams",
    "keygen",
    "encrypt",
    "decrypt",
]
