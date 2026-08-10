# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 18: Hash-based signature cryptanalysis
# Section: "FORS reuse thresholds across the parameter sets"
# https://book.encryptorium.com/part-3-hash-based/ch18-hash-based-signature-cryptanalysis/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch18/05-log2-fors-forgery.py

import math

params_fors = [
    ("SLH-DSA-128s", 14, 12),
    ("SLH-DSA-128f", 33, 6),
    ("SLH-DSA-192s", 17, 14),
    ("SLH-DSA-192f", 33, 8),
    ("SLH-DSA-256s", 22, 14),
    ("SLH-DSA-256f", 35, 9),
]

def log2_fors_forgery(q, k, t):
    if q == 0:
        return float("-inf")
    log_miss = q * math.log1p(-1.0 / t)   # ln (1 - 1/t)^q
    covered = -math.expm1(log_miss)        # 1 - (1 - 1/t)^q
    return k * math.log2(covered)

def first_q_at_or_above(k, t, threshold_bits):
    lo, hi = 0, 1
    while log2_fors_forgery(hi, k, t) < -threshold_bits:
        hi *= 2
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if log2_fors_forgery(mid, k, t) < -threshold_bits:
            lo = mid
        else:
            hi = mid
    return hi

print("single-signature forgery: log2(P) = -a*k")
header = f"{'name':<16} {'k':>3} {'a':>3} {'t':>6} {'log2_P':>8}"
print(header)
for nm, k, a in params_fors:
    t = 2**a
    print(f"{nm:<16} {k:>3} {a:>3} {t:>6} {-a*k:>8}")
print()
print("exact first q with P >= 2^-128 and >= 2^-64")
header2 = f"{'name':<16} {'k':>3} {'t':>6} {'q@2^-128':>9} {'q@2^-64':>9}"
print(header2)
for nm, k, a in params_fors:
    t = 2**a
    q128 = first_q_at_or_above(k, t, 128)
    q64 = first_q_at_or_above(k, t, 64)
    print(f"{nm:<16} {k:>3} {t:>6} {q128:>9} {q64:>9}")
# ==> single-signature forgery: log2(P) = -a*k
# ==> name               k   a      t   log2_P
# ==> SLH-DSA-128s      14  12   4096     -168
# ==> SLH-DSA-128f      33   6     64     -198
# ==> SLH-DSA-192s      17  14  16384     -238
# ==> SLH-DSA-192f      33   8    256     -264
# ==> SLH-DSA-256s      22  14  16384     -308
# ==> SLH-DSA-256f      35   9    512     -315
# ==>
# ==> exact first q with P >= 2^-128 and >= 2^-64
# ==> name               k      t  q@2^-128   q@2^-64
# ==> SLH-DSA-128s      14   4096         8       176
# ==> SLH-DSA-128f      33     64         5        20
# ==> SLH-DSA-192s      17  16384        89      1253
# ==> SLH-DSA-192f      33    256        18        78
# ==> SLH-DSA-256s      22  16384       293      2341
# ==> SLH-DSA-256f      35    512        43       170
