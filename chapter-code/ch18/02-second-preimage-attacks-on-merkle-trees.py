# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 18: Hash-based signature cryptanalysis
# Section: "Second-preimage attacks on Merkle trees"
# https://book.encryptorium.com/part-3-hash-based/ch18-hash-based-signature-cryptanalysis/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch18/02-second-preimage-attacks-on-merkle-trees.py

import hashlib
import struct

left  = hashlib.sha256(b"node-left").digest()[:16]
right = hashlib.sha256(b"node-right").digest()[:16]

h_level1 = hashlib.sha256(left + right).hexdigest()[:16]
h_level2 = hashlib.sha256(left + right).hexdigest()[:16]
print(f"without ADRS: level 1 == level 2 ? {h_level1 == h_level2}")
# ==> without ADRS: level 1 == level 2 ? True

adrs1 = struct.pack(">I", 1) + b"\x00" * 28
adrs2 = struct.pack(">I", 2) + b"\x00" * 28
h_adrs1 = hashlib.sha256(adrs1 + left + right).hexdigest()[:16]
h_adrs2 = hashlib.sha256(adrs2 + left + right).hexdigest()[:16]
print(f"with ADRS:    level 1 == level 2 ? {h_adrs1 == h_adrs2}")
# ==> with ADRS:    level 1 == level 2 ? False
