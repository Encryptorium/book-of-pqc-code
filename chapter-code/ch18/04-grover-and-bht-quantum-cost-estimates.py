# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 18: Hash-based signature cryptanalysis
# Section: "Grover and BHT quantum cost estimates"
# https://book.encryptorium.com/part-3-hash-based/ch18-hash-based-signature-cryptanalysis/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch18/04-grover-and-bht-quantum-cost-estimates.py

import math

header = f"{'n_bits':>10} {'class_pre':>10} {'quant_pre':>10} {'class_coll':>11} {'bht_coll':>10} {'nist_cat':>9}"
print(header)
for n_bits, cat in [(128, 1), (192, 3), (256, 5)]:
    cp = n_bits
    qp = n_bits // 2
    cc = n_bits // 2
    bht = n_bits / 3
    print(f"{n_bits:>10} {cp:>10} {qp:>10} {cc:>11} {bht:>10.1f} {cat:>9}")
# ==>     n_bits  class_pre  quant_pre  class_coll   bht_coll  nist_cat
# ==>        128        128         64          64       42.7         1
# ==>        192        192         96          96       64.0         3
# ==>        256        256        128         128       85.3         5
