# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 16: FORS and the stateless hypertree
# Section: "The few-time collision demo"
# https://book.encryptorium.com/part-3-hash-based/ch16-fors-and-stateless-hypertree/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch16/05-message-indices.py

import hashlib

def message_indices(message, k, t):
    lg_t = t.bit_length() - 1            # t is a power of two; no float log
    digest = hashlib.sha256(message).digest()
    indices = []
    bit_offset = 0
    for _ in range(k):
        value = 0
        for b in range(lg_t):
            cur = bit_offset + b
            by = cur // 8
            bi = 7 - (cur % 8)
            value = (value << 1) | ((digest[by] >> bi) & 1)
        indices.append(value)
        bit_offset += lg_t
    return indices

k, t = 6, 16
for q_max in [5, 10, 15, 20]:
    used = [set() for _ in range(k)]
    redundant = 0
    for q in range(1, q_max + 1):
        idxs = message_indices(f"msg-{q}".encode(), k, t)
        for j in range(k):
            if idxs[j] in used[j]:
                redundant += 1
            used[j].add(idxs[j])
    print(f"q={q_max:2d}: {redundant} redundant leaf exposures")
# ==> q= 5: 3 redundant leaf exposures
# ==> q=10: 18 redundant leaf exposures
# ==> q=15: 32 redundant leaf exposures
# ==> q=20: 52 redundant leaf exposures

# Distinct leaves per tree is what a reuse forgery needs, not the raw count.
k, t, q = 6, 16, 20
used = [set() for _ in range(k)]
for s in range(1, q + 1):
    for j, ix in enumerate(message_indices(f"msg-{s}".encode(), k, t)):
        used[j].add(ix)
distinct = [len(u) for u in used]
print(f"distinct leaves/tree at q={q}: {distinct}")
# ==> distinct leaves/tree at q=20: [12, 11, 10, 12, 12, 11]
coverage = 1.0
for u in distinct:
    coverage *= u / t
print(f"random-target coverage = {coverage:.4f}")
# ==> random-target coverage = 0.1246
occ = (1 - (1 - 1 / t) ** q) ** k
print(f"occupancy estimate = {occ:.4f}")
# ==> occupancy estimate = 0.1451
print(f"small-q (q/t)^k = {(q / t) ** k:.4f}")
# ==> small-q (q/t)^k = 3.8147
