# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 20: McEliece: the original PQC
# Section: "A toy McEliece round-trip"
# https://book.encryptorium.com/part-4-code-isogeny/ch20-mceliece-the-original-pqc/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch20/03-mat-vec.py

ct = [0, 1, 0, 0, 1, 1, 1]

# Parity-check matrix H for the [7,4] Goppa code.
H = [[0,1,1,0,1,0,1],[1,0,0,0,1,1,1],[1,1,0,1,0,0,1]]

def mat_vec(A, v):
    return [sum(a*x for a,x in zip(row, v))%2 for row in A]

# Step 1: undo permutation P.
perm = [2, 0, 4, 1, 6, 3, 5]
perm_inv = [0]*7
for i, j in enumerate(perm):
    perm_inv[j] = i
c_unperm = [0]*7
for i in range(7):
    c_unperm[perm_inv[i]] = ct[i]

# Step 2: syndrome decode.
s = mat_vec(H, c_unperm)
error_pos = None
for j in range(7):
    if [H[r][j] for r in range(3)] == s:
        error_pos = j
        break
c_unperm[error_pos] ^= 1

# Step 3: extract scrambled message (last k=4 bits).
m_scrambled = c_unperm[3:]

# Step 4: undo S.  m = m_scrambled * S^{-1}.
S_inv = [[1,0,0,0],[1,1,0,0],[1,1,1,0],[1,1,1,1]]
recovered = [sum(m_scrambled[i]*S_inv[i][j] for i in range(4))%2 for j in range(4)]

print("m * S =", m_scrambled)
print("recovered:", recovered)
# ==> m * S = [1, 1, 0, 1]
# ==> recovered: [1, 0, 1, 1]
