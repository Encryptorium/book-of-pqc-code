# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 15: Many-time signatures
# Section: "WOTS+ keygen, sign, and verify at standard dimensions"
# https://book.encryptorium.com/part-3-hash-based/ch15-many-time-signatures/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch15/06-base-w.py

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

sk_seed = b"ch15-full-sk"
pk_seed = b"ch15-full-pk"
w, n = 16, 32
lg_w = int(math.log2(w))
ell_1 = math.ceil(8 * n / lg_w)
max_c = ell_1 * (w - 1)
ell_2 = math.ceil((math.floor(math.log2(max_c)) + 1) / lg_w)
ell = ell_1 + ell_2

sk = [hashlib.sha256(sk_seed + b"sk" + i.to_bytes(4, "big")).digest() for i in range(ell)]
pk = [chain_f(sk[i], 0, w - 1, pk_seed, i) for i in range(ell)]

message = b"XMSS test message"
digest = hashlib.sha256(message).digest()
msg_digits = base_w(digest, w, ell_1)
c = sum(w - 1 - d for d in msg_digits)
c_shifted = c << (8 * 2 - ell_2 * lg_w)
c_bytes = c_shifted.to_bytes(2, "big")
csum_digits = base_w(c_bytes, w, ell_2)
all_digits = msg_digits + csum_digits

sig = [chain_f(sk[i], 0, all_digits[i], pk_seed, i) for i in range(ell)]
print(sig[0].hex()[:16])
# ==> fcf28dd604c58b8f
