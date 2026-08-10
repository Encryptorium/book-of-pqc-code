# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 17: SLH-DSA (FIPS 205) from scratch
# Section: "The address structure"
# https://book.encryptorium.com/part-3-hash-based/ch17-slh-dsa-fips-205/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch17/02-new-adrs.py

import hashlib, struct

def new_adrs():
    return bytearray(32)

def set_type_clear(ad, v):
    struct.pack_into(">I", ad, 16, v)
    ad[20:32] = b"\x00" * 12

def set_kp(ad, v):
    struct.pack_into(">I", ad, 20, v)

ad = new_adrs()
set_kp(ad, 42)
print(f"Before set_type: kp = {struct.unpack_from('>I', ad, 20)[0]}")
set_type_clear(ad, 2)  # TREE
print(f"After set_type:  kp = {struct.unpack_from('>I', ad, 20)[0]}")
# ==> Before set_type: kp = 42
# ==> After set_type:  kp = 0
