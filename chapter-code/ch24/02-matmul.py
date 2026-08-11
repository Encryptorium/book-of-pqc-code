# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 24: Multivariate signature schemes
# Section: "Toy UOV at $(n, m, q) = (5, 2, 7)$"
# https://book.encryptorium.com/part-4-code-isogeny/ch24-the-other-families/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch24/02-matmul.py

import random

Q, N, M, N_V = 7, 5, 2, 3   # field, total vars, equations, vinegar vars

def matmul(A, B):
    n, k, m = len(A), len(A[0]), len(B[0])
    return [[sum(A[i][t] * B[t][j] for t in range(k)) % Q for j in range(m)] for i in range(n)]

def transpose(A):
    return [list(row) for row in zip(*A)]

def mat_vec(A, v):
    return [sum(A[i][k] * v[k] for k in range(len(v))) % Q for i in range(len(A))]

def quadratic_eval(Mat, x):
    return sum(Mat[i][j] * x[i] * x[j] for i in range(len(x)) for j in range(len(x))) % Q

def is_invertible(A):
    n = len(A); mat = [row[:] for row in A]
    for c in range(n):
        p = next((r for r in range(c, n) if mat[r][c] != 0), None)
        if p is None: return False
        mat[c], mat[p] = mat[p], mat[c]
        inv = pow(mat[c][c], Q - 2, Q)
        for r in range(c + 1, n):
            if mat[r][c]:
                f = mat[r][c] * inv % Q
                for k in range(c, n):
                    mat[r][k] = (mat[r][k] - f * mat[c][k]) % Q
    return True

def invert_mat(A):
    n = len(A)
    mat = [row[:] + [1 if j == i else 0 for j in range(n)] for i, row in enumerate(A)]
    for c in range(n):
        p = next((r for r in range(c, n) if mat[r][c] != 0), None)
        assert p is not None, "matrix is singular over GF(Q); inversion undefined"
        mat[c], mat[p] = mat[p], mat[c]
        inv = pow(mat[c][c], Q - 2, Q)
        for k in range(2 * n): mat[c][k] = mat[c][k] * inv % Q
        for r in range(n):
            if r != c and mat[r][c]:
                f = mat[r][c]
                for k in range(2 * n):
                    mat[r][k] = (mat[r][k] - f * mat[c][k]) % Q
    return [row[n:] for row in mat]

def solve_linear(A, b):
    m = len(A); aug = [A[i][:] + [b[i]] for i in range(m)]
    for c in range(m):
        p = next((r for r in range(c, m) if aug[r][c] != 0), None)
        if p is None: return None
        aug[c], aug[p] = aug[p], aug[c]
        inv = pow(aug[c][c], Q - 2, Q)
        for k in range(m + 1): aug[c][k] = aug[c][k] * inv % Q
        for r in range(m):
            if r != c and aug[r][c]:
                f = aug[r][c]
                for k in range(m + 1):
                    aug[r][k] = (aug[r][k] - f * aug[c][k]) % Q
    return [aug[i][m] for i in range(m)]

# KeyGen. Sample T invertible; sample F with oil-oil block zero; build P.
rng = random.Random(0)
while True:
    T = [[rng.randrange(Q) for _ in range(N)] for _ in range(N)]
    if is_invertible(T): break

F = []
for _ in range(M):
    F_i = [[rng.randrange(Q) for _ in range(N)] for _ in range(N)]
    for r in range(N_V, N):
        for c in range(N_V, N):
            F_i[r][c] = 0
    F.append(F_i)

P = [matmul(matmul(transpose(T), F_i), T) for F_i in F]

# Sign. Target = toy hash. Fix vinegar; solve linear system in oil.
target = [3, 5]
rng2 = random.Random(1)
while True:
    vinegar = [rng2.randrange(Q) for _ in range(N_V)]
    L, rhs = [], []
    for i, F_i in enumerate(F):
        c_i = sum(F_i[j][k] * vinegar[j] * vinegar[k]
                  for j in range(N_V) for k in range(N_V)) % Q
        row = [sum((F_i[j][N_V + l] + F_i[N_V + l][j]) * vinegar[j]
                   for j in range(N_V)) % Q
               for l in range(M)]
        L.append(row); rhs.append((target[i] - c_i) % Q)
    oil = solve_linear(L, rhs)
    if oil is not None: break

y = vinegar + oil
signature = mat_vec(invert_mat(T), y)

# Verify. Evaluate P on the signature and check componentwise against target.
p_eval = [quadratic_eval(P_i, signature) for P_i in P]

print("target:   ", target)
print("signature:", signature)
print("P(sig):   ", p_eval)
print("verify:   ", p_eval == target)
# ==> target:    [3, 5]
# ==> signature: [4, 4, 4, 2, 3]
# ==> P(sig):    [3, 5]
# ==> verify:    True
