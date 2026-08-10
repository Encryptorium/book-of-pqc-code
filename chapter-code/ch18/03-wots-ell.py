# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 18: Hash-based signature cryptanalysis
# Section: "Multi-target preimage across all FIPS 205 parameter sets"
# https://book.encryptorium.com/part-3-hash-based/ch18-hash-based-signature-cryptanalysis/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch18/03-wots-ell.py

import math

def wots_ell(n_bytes, w):
    lg_w = int(math.log2(w))
    ell_1 = math.ceil(8 * n_bytes / lg_w)
    mc = ell_1 * (w - 1)
    ell_2 = math.ceil((math.floor(math.log2(mc)) + 1) / lg_w)
    return ell_1 + ell_2

params = [
    ("SLH-DSA-SHA2-128s", 16, 63, 7, 12, 14, 16),
    ("SLH-DSA-SHA2-128f", 16, 66, 22, 6, 33, 16),
    ("SLH-DSA-SHA2-192s", 24, 63, 7, 14, 17, 16),
    ("SLH-DSA-SHA2-192f", 24, 66, 22, 8, 33, 16),
    ("SLH-DSA-SHA2-256s", 32, 64, 8, 14, 22, 16),
    ("SLH-DSA-SHA2-256f", 32, 68, 17, 9, 35, 16),
]

header = f"{'name':<22} {'n':>3} {'targets':>10} {'adv':>6} {'no_adrs':>8} {'adrs':>5} {'cat':>4}"
print(header)
for nm, n, h, d, a, k, w in params:
    t = 2**a
    ell = wots_ell(n, w)
    targets = k * t + d * ell
    adv = math.log2(targets)
    n_bits = 8 * n
    eff_no_adrs = n_bits - adv
    eff_adrs = n_bits
    cat_num = {128: 1, 192: 3, 256: 5}[n_bits]
    print(f"{nm:<22} {n_bits:>3} {targets:>10,} {adv:>6.1f} {eff_no_adrs:>8.1f} {eff_adrs:>5} {cat_num:>4}")
# ==> name                     n    targets    adv  no_adrs  adrs  cat
# ==> SLH-DSA-SHA2-128s      128     57,589   15.8    112.2   128    1
# ==> SLH-DSA-SHA2-128f      128      2,882   11.5    116.5   128    1
# ==> SLH-DSA-SHA2-192s      192    278,885   18.1    173.9   192    3
# ==> SLH-DSA-SHA2-192f      192      9,570   13.2    178.8   192    3
# ==> SLH-DSA-SHA2-256s      256    360,984   18.5    237.5   256    5
# ==> SLH-DSA-SHA2-256f      256     19,059   14.2    241.8   256    5
