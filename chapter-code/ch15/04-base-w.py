# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 15: Many-time signatures
# Section: "The checksum"
# https://book.encryptorium.com/part-3-hash-based/ch15-many-time-signatures/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch15/04-base-w.py

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

w = 16
ell_1 = 64
digest = hashlib.sha256(b"XMSS test message").digest()
msg_digits = base_w(digest, w, ell_1)

c = sum(w - 1 - d for d in msg_digits)
print(c)
# ==> 481

# Left-shift c so the ell_2 digits fill the MSB of the byte encoding,
# matching RFC 8391 Section 3.1.5, Algorithm 5.
ell_2 = 3
lg_w = 4
total_bits = ell_2 * lg_w  # 12 bits
num_bytes = 2              # ceil(12 / 8)
shift = 8 * num_bytes - total_bits  # 4
c_shifted = c << shift
c_bytes = c_shifted.to_bytes(num_bytes, "big")
csum_digits = base_w(c_bytes, w, ell_2)
print(csum_digits)
# ==> [1, 14, 1]
