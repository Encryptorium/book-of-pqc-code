# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 20: McEliece: the original PQC
# Section: "Generator matrix and verification"
# https://book.encryptorium.com/part-4-code-isogeny/ch20-mceliece-the-original-pqc/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch20/06-gf16-mul.py

import random

def gf16_mul(a, b):
    result = 0
    for _ in range(4):
        if b & 1: result ^= a
        b >>= 1; a <<= 1
        if a & 16: a ^= 0b10011
    return result

def gf16_inv(a):
    for x in range(1, 16):
        if gf16_mul(a, x) == 1: return x

def poly_eval_gf16(coeffs, x):
    result = 0
    for c in reversed(coeffs):
        result = gf16_mul(result, x) ^ c
    return result

# Reproduce the Goppa code from the previous block.
rng = random.Random(42)
while True:
    c0, c1 = rng.randint(0, 15), rng.randint(0, 15)
    g = [c0, c1, 1]
    if all(poly_eval_gf16(g, a) != 0 for a in range(16)):
        break
support = list(range(16))
t, n = 2, 16
h = [gf16_inv(poly_eval_gf16(g, a)) for a in support]
V = []
for i in range(t):
    row = []
    for j in range(n):
        lj_pow = 1
        for _ in range(i): lj_pow = gf16_mul(lj_pow, support[j])
        row.append(gf16_mul(lj_pow, h[j]))
    V.append(row)
H = []
for row in V:
    for bit in range(4):
        H.append([(entry >> bit) & 1 for entry in row])

# Gaussian elimination with column pivoting.
def gauss_systematic(H):
    rows, cols = len(H), len(H[0])
    M = [list(row) for row in H]
    col_perm = list(range(cols))
    for i in range(rows):
        pivot = None
        for j in range(i, cols):
            for r in range(i, rows):
                if M[r][j] == 1:
                    if r != i: M[i], M[r] = M[r], M[i]
                    pivot = j; break
            if pivot is not None: break
        # Column swap: bring the pivot into column i so the left n-k
        # columns can form the identity block of [I_{n-k} | B].
        if pivot != i:
            for r in range(rows):
                M[r][i], M[r][pivot] = M[r][pivot], M[r][i]
            col_perm[i], col_perm[pivot] = col_perm[pivot], col_perm[i]
        for r in range(rows):
            if r != i and M[r][i] == 1:
                for c in range(cols): M[r][c] ^= M[i][c]
    return M, col_perm

H_sys, col_perm = gauss_systematic(H)
nk = len(H_sys)
k = n - nk

# G = [B^T | I_k] from H_sys = [I_{n-k} | B].
B = [[H_sys[r][nk+c] for c in range(k)] for r in range(nk)]
Bt = [list(col) for col in zip(*B)]
Ik = [[1 if i==j else 0 for j in range(k)] for i in range(k)]
G = [Bt[r] + Ik[r] for r in range(k)]

# Verify G * H^T = 0 in permuted column ordering.
H_perm = [[H[r][col_perm[c]] for c in range(n)] for r in range(nk)]
Ht = [list(col) for col in zip(*H_perm)]
GHt = [[sum(G[r][i]*Ht[i][c] for i in range(n))%2 for c in range(nk)]
       for r in range(k)]
print(f"G shape: {k} x {n}")
print(f"G * H^T = 0: {all(all(x==0 for x in row) for row in GHt)}")
# ==> G shape: 8 x 16
# ==> G * H^T = 0: True
