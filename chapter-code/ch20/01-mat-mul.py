# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 20: McEliece: the original PQC
# Section: "A toy McEliece round-trip"
# https://book.encryptorium.com/part-4-code-isogeny/ch20-mceliece-the-original-pqc/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch20/01-mat-mul.py

# Generator matrix G for the [7,4] Goppa code (systematic form [B^T | I_4]).
G = [[0,1,1,1,0,0,0],[1,1,0,0,1,0,0],[1,1,1,0,0,1,0],[1,0,1,0,0,0,1]]

# Scrambling matrix S (invertible 4x4 over GF(2)) and its inverse.
S = [[1,0,0,0],[1,1,0,0],[0,1,1,0],[0,0,1,1]]
S_inv = [[1,0,0,0],[1,1,0,0],[1,1,1,0],[1,1,1,1]]

# Column permutation.
perm = [2, 0, 4, 1, 6, 3, 5]

def mat_mul(A, B):
    Bt = [list(col) for col in zip(*B)]
    return [[sum(a*b for a,b in zip(ra,cb))%2 for cb in Bt] for ra in A]

# G_pub = S * G * P.
SG = mat_mul(S, G)
perm_inv = [0]*7
for i, j in enumerate(perm):
    perm_inv[j] = i
G_pub = [[SG[r][perm_inv[c]] for c in range(7)] for r in range(4)]

print("G_pub:")
for row in G_pub:
    print(" ", row)
# ==> G_pub:
# ==>   [1, 1, 0, 0, 1, 0, 0]
# ==>   [0, 1, 1, 0, 1, 0, 1]
# ==>   [0, 0, 0, 1, 1, 0, 1]
# ==>   [1, 0, 0, 1, 0, 1, 0]
