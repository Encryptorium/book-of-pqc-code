# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 15: Many-time signatures
# Section: "WOTS+ at small parameters"
# https://book.encryptorium.com/part-3-hash-based/ch15-many-time-signatures/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch15/02-chain-f.py

import hashlib

def chain_f(x, start, steps, pk_seed, addr, n=4):
    value = x
    for i in range(start, start + steps):
        value = hashlib.sha256(
            pk_seed + addr.to_bytes(4, "big") + i.to_bytes(4, "big") + value
        ).digest()[:n]
    return value

sk_seed = b"ch15-tiny-sk"
pk_seed = b"ch15-tiny-pk"
sk_0 = hashlib.sha256(sk_seed + b"sk" + (0).to_bytes(4, "big")).digest()[:4]

sig_0 = chain_f(sk_0, 0, 1, pk_seed, 0)
print(sig_0.hex())
# ==> 33fb9d07

# The verifier hashes forward w - 1 - d = 3 - 1 = 2 steps.
recomputed = chain_f(sig_0, 1, 2, pk_seed, 0)
pk_0 = chain_f(sk_0, 0, 3, pk_seed, 0)
print(recomputed == pk_0)
# ==> True
