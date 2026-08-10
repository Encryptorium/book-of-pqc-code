# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 18: Hash-based signature cryptanalysis
# Section: "Multi-target preimage on SLH-DSA-128s"
# https://book.encryptorium.com/part-3-hash-based/ch18-hash-based-signature-cryptanalysis/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch18/01-multi-target-preimage-on-slh-dsa-128s.py

import math

n_bytes = 16
n_bits = 8 * n_bytes
k, a = 14, 12
t = 2**a
w = 16

lg_w = int(math.log2(w))
ell_1 = math.ceil(8 * n_bytes / lg_w)
mc = ell_1 * (w - 1)
ell_2 = math.ceil((math.floor(math.log2(mc)) + 1) / lg_w)
ell = ell_1 + ell_2
d = 7

revealed_fors = k * (1 + a)
revealed_wots = d * ell
h = 63
randomizer = 1
sig_elements = randomizer + revealed_fors + revealed_wots + h
sig_bytes = sig_elements * n_bytes
fors_wots_elems = revealed_fors + revealed_wots

fors_instance_targets = k * t
wots_layer_targets = d * ell
per_instance_total = fors_instance_targets + wots_layer_targets

adv = math.log2(per_instance_total)
eff_no_adrs = n_bits - adv

print(f"FORS signature values (n-byte): {revealed_fors}")
# ==> FORS signature values (n-byte): 182
print(f"WOTS+ chain values (n-byte)   : {revealed_wots}")
# ==> WOTS+ chain values (n-byte)   : 245
print(f"XMSS auth-path nodes (n-byte) : {h}")
# ==> XMSS auth-path nodes (n-byte) : 63
print(f"randomizer R (n-byte)         : {randomizer}")
# ==> randomizer R (n-byte)         : 1
print(f"signature n-byte strings      : {sig_elements}")
# ==> signature n-byte strings      : 491
print(f"signature size (bytes)        : {sig_bytes:,}")
# ==> signature size (bytes)        : 7,856
print(f"FORS+WOTS+ signature elems    : {fors_wots_elems}")
# ==> FORS+WOTS+ signature elems    : 427
print(f"FORS targets per instance     : {fors_instance_targets:,}")
# ==> FORS targets per instance     : 57,344
print(f"WOTS+ targets per instance    : {wots_layer_targets}")
# ==> WOTS+ targets per instance    : 245
print(f"per-instance total            : {per_instance_total:,}")
# ==> per-instance total            : 57,589
print(f"multi-target advantage        : {adv:.1f} bits")
# ==> multi-target advantage        : 15.8 bits
print(f"effective security (no ADRS)  : {eff_no_adrs:.1f} bits")
# ==> effective security (no ADRS)  : 112.2 bits
print(f"single-target preimage bound  : {n_bits} bits")
# ==> single-target preimage bound  : 128 bits
