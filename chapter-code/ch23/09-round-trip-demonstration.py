# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 23: SQIsign in a toy setting
# Section: "Round-trip demonstration"
# https://book.encryptorium.com/part-4-code-isogeny/ch23-sqisign-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch23/09-round-trip-demonstration.py

# Run the standalone toy. Imports use the package layout, but the
# inline blocks above re-derive every helper from standard library
# primitives so each block is self-contained.

import sys, pathlib
PKG = pathlib.Path("solutions/ch23-sqisign/src").resolve()
sys.path.insert(0, str(PKG))

from sqisign.sqisign import keygen, sign, verify

sk = keygen(b"alice")
print(sk.pk.j())
# ==> (143, 0)

sig = sign(b"the quick brown fox", sk)
print(verify(b"the quick brown fox", sig, sk.pk))
# ==> True
print(verify(b"different message", sig, sk.pk))
# ==> False
