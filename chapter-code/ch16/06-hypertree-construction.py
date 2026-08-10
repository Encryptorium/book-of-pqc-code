# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 16: FORS and the stateless hypertree
# Section: "Hypertree construction"
# https://book.encryptorium.com/part-3-hash-based/ch16-fors-and-stateless-hypertree/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch16/06-hypertree-construction.py

import hashlib

# Hypertree size computation at d=2, h'=4, w=16, n=32.
# FIPS 205 forbids floating point in parameter derivations, so ell is
# computed with integer arithmetic only.
d, h_prime, w, n = 2, 4, 16, 32

lg_w = w.bit_length() - 1               # w is a power of two
ell_1 = (8 * n + lg_w - 1) // lg_w      # ceil(8n / lg_w)
max_c = ell_1 * (w - 1)
ell_2 = 1
capacity = w
while capacity <= max_c:
    ell_2 += 1
    capacity *= w
ell = ell_1 + ell_2

total_leaves = 1 << (d * h_prime)
print(f"Total leaf positions: {total_leaves}")
# ==> Total leaf positions: 256

wots_sig_bytes = ell * n
auth_path_bytes = h_prime * n
layer_sig = wots_sig_bytes + auth_path_bytes
print(f"WOTS+ signature: {ell} chains * {n} B = {wots_sig_bytes} B")
# ==> WOTS+ signature: 67 chains * 32 B = 2144 B
print(f"Auth path: {h_prime} nodes * {n} B = {auth_path_bytes} B")
# ==> Auth path: 4 nodes * 32 B = 128 B

total_sig = d * layer_sig
print(f"Hypertree signature: {d} layers * {layer_sig} B = {total_sig} B")
# ==> Hypertree signature: 2 layers * 2272 B = 4544 B
