# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 15: Many-time signatures
# Section: "The checksum-bypass forgery"
# https://book.encryptorium.com/part-3-hash-based/ch15-many-time-signatures/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch15/08-chain-f.py

import hashlib, math

def chain_f(x, start, steps, pk_seed, addr):
    value = x
    for i in range(start, start + steps):
        value = hashlib.sha256(
            pk_seed + addr.to_bytes(4, "big") + i.to_bytes(4, "big") + value
        ).digest()
    return value

sk_seed = b"ch15-forgery-sk"
pk_seed = b"ch15-forgery-pk"
w = 16
sk_0 = hashlib.sha256(sk_seed + b"sk" + (0).to_bytes(4, "big")).digest()

# Legitimate signature value at position d=7.
sig_at_7 = chain_f(sk_0, 0, 7, pk_seed, 0)

# Adversary hashes forward one step to get position 8.
forged_at_8 = chain_f(sig_at_7, 7, 1, pk_seed, 0)

# This matches what signing with digit 8 would produce.
expected_at_8 = chain_f(sk_0, 0, 8, pk_seed, 0)
print(forged_at_8 == expected_at_8)
# ==> True
