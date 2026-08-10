# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 15: Many-time signatures
# Section: "The checksum-bypass forgery"
# https://book.encryptorium.com/part-3-hash-based/ch15-many-time-signatures/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch15/09-the-checksum-bypass-forgery.py

import hashlib

w = 16
msg_digits = [7, 3, 15, 0, 10, 5, 12, 8]
c_original = sum(w - 1 - d for d in msg_digits)
print(c_original)
# ==> 60

# Increase digit 0 from 7 to 8.
modified = list(msg_digits)
modified[0] = 8
c_modified = sum(w - 1 - d for d in modified)
print(c_modified)
# ==> 59

print(c_original - c_modified)
# ==> 1
