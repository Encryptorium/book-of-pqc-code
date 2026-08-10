# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 17: SLH-DSA (FIPS 205) from scratch
# Section: "FIPS 205 parameter sets and signature sizes"
# https://book.encryptorium.com/part-3-hash-based/ch17-slh-dsa-fips-205/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch17/05-sig-size.py

import math

def sig_size(name, n, h, d, a, k, w):
    hp = h // d
    lg_w = int(math.log2(w))
    ell_1 = math.ceil(8 * n / lg_w)
    mc = ell_1 * (w - 1)
    ell_2 = math.ceil((math.floor(math.log2(mc)) + 1) / lg_w)
    ell = ell_1 + ell_2
    r_bytes = n
    fors_bytes = k * (1 + a) * n
    ht_bytes = d * (ell + hp) * n
    total = r_bytes + fors_bytes + ht_bytes
    print(f"{name:24s}  n={n:2d}  sig={total:6,d} B  "
          f"(R={r_bytes}, FORS={fors_bytes:,d}, HT={ht_bytes:,d})")

sig_size("SLH-DSA-SHA2-128s", 16, 63, 7, 12, 14, 16)
sig_size("SLH-DSA-SHA2-128f", 16, 66, 22, 6, 33, 16)
sig_size("SLH-DSA-SHA2-192s", 24, 63, 7, 14, 17, 16)
sig_size("SLH-DSA-SHA2-192f", 24, 66, 22, 8, 33, 16)
sig_size("SLH-DSA-SHA2-256s", 32, 64, 8, 14, 22, 16)
sig_size("SLH-DSA-SHA2-256f", 32, 68, 17, 9, 35, 16)
# ==> SLH-DSA-SHA2-128s         n=16  sig= 7,856 B  (R=16, FORS=2,912, HT=4,928)
# ==> SLH-DSA-SHA2-128f         n=16  sig=17,088 B  (R=16, FORS=3,696, HT=13,376)
# ==> SLH-DSA-SHA2-192s         n=24  sig=16,224 B  (R=24, FORS=6,120, HT=10,080)
# ==> SLH-DSA-SHA2-192f         n=24  sig=35,664 B  (R=24, FORS=7,128, HT=28,512)
# ==> SLH-DSA-SHA2-256s         n=32  sig=29,792 B  (R=32, FORS=10,560, HT=19,200)
# ==> SLH-DSA-SHA2-256f         n=32  sig=49,856 B  (R=32, FORS=11,200, HT=38,624)
