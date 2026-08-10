# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 15: Many-time signatures
# Section: "WOTS+ keygen, sign, and verify at standard dimensions"
# https://book.encryptorium.com/part-3-hash-based/ch15-many-time-signatures/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch15/05-base-w.py

import hashlib, math

def base_w(data, w, out_len):
    lg_w = int(math.log2(w))
    digits = []
    for byte in data:
        for shift in range(8 - lg_w, -1, -lg_w):
            digits.append((byte >> shift) & (w - 1))
            if len(digits) == out_len:
                return digits
    return digits[:out_len]

def chain_f(x, start, steps, pk_seed, addr):
    value = x
    for i in range(start, start + steps):
        value = hashlib.sha256(
            pk_seed + addr.to_bytes(4, "big") + i.to_bytes(4, "big") + value
        ).digest()
    return value

sk_seed = b"ch15-full-sk"   # secret: derives the WOTS+ secret values
pk_seed = b"ch15-full-pk"   # public: domain-separates the chain
w, n = 16, 32
lg_w = int(math.log2(w))
ell_1 = math.ceil(8 * n / lg_w)
max_c = ell_1 * (w - 1)
ell_2 = math.ceil((math.floor(math.log2(max_c)) + 1) / lg_w)
ell = ell_1 + ell_2

sk = [hashlib.sha256(sk_seed + b"sk" + i.to_bytes(4, "big")).digest() for i in range(ell)]
pk = [chain_f(sk[i], 0, w - 1, pk_seed, i) for i in range(ell)]
print(ell)
# ==> 67
print(sk[0].hex()[:16])
# ==> 52c38cfc379ebaaf
print(pk[0].hex()[:16])
# ==> c4608f81e170d3b7
