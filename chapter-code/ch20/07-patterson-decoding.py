# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 20: McEliece: the original PQC
# Section: "Patterson decoding"
# https://book.encryptorium.com/part-4-code-isogeny/ch20-mceliece-the-original-pqc/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch20/07-patterson-decoding.py

import sys, pathlib, random
sys.path.insert(0, str(pathlib.Path("solutions/ch20-mceliece/src")))

from mceliece.gf2m import poly_eval
from mceliece.goppa import goppa_parity_check, find_irreducible_goppa_poly, full_support
from mceliece.gf2 import generator_from_parity, vec_add
from mceliece.patterson import patterson_decode

m, irred = 4, 0b10011
rng = random.Random(42)
g_coeffs = find_irreducible_goppa_poly(m, irred, 2, rng)
support = [a for a in full_support(m) if poly_eval(g_coeffs, a, m, irred) != 0]
H = goppa_parity_check(m, irred, g_coeffs, support)
G, col_perm = generator_from_parity(H)
support_sys = [support[col_perm[i]] for i in range(len(support))]

msg = [1, 0, 1, 1, 0, 0, 1, 0]
codeword = [0] * 16
for i, mi in enumerate(msg):
    if mi:
        codeword = vec_add(codeword, G[i])

received = list(codeword)
received[3] ^= 1
received[11] ^= 1

decoded = patterson_decode(received, g_coeffs, support_sys, m, irred)
print(f"errors corrected: {sum(a^b for a,b in zip(received, decoded))}")
print(f"codeword recovered: {decoded == codeword}")
# ==> errors corrected: 2
# ==> codeword recovered: True
