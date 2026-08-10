# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 15: Many-time signatures
# Section: "WOTS+ at small parameters"
# https://book.encryptorium.com/part-3-hash-based/ch15-many-time-signatures/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch15/01-chain-f.py

import hashlib

def chain_f(x, start, steps, pk_seed, addr, n=4):
    """Iterate the chain function F for *steps* from position *start*."""
    value = x
    for i in range(start, start + steps):
        value = hashlib.sha256(
            pk_seed + addr.to_bytes(4, "big") + i.to_bytes(4, "big") + value
        ).digest()[:n]
    return value

sk_seed = b"ch15-tiny-sk"   # secret: derives the chain start value
pk_seed = b"ch15-tiny-pk"   # public: domain-separates the chain
sk_0 = hashlib.sha256(sk_seed + b"sk" + (0).to_bytes(4, "big")).digest()[:4]
print(sk_0.hex())
# ==> 2c85517f

pk_0 = chain_f(sk_0, 0, 3, pk_seed, 0)
print(pk_0.hex())
# ==> 33b2bbda
