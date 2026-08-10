# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 19: Coding theory for cryptographers
# Section: "The [7,4,3] Hamming code"
# https://book.encryptorium.com/part-4-code-isogeny/ch19-coding-theory-for-cryptographers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch19/02-gf2-mat-vec.py

H = [
    [1, 1, 0, 1, 1, 0, 0],
    [1, 0, 1, 1, 0, 1, 0],
    [0, 1, 1, 1, 0, 0, 1],
]

def gf2_mat_vec(A, v):
    return [sum(a * x for a, x in zip(row, v)) % 2 for row in A]

c = [1, 0, 1, 1, 0, 1, 0]
r = list(c)
r[2] ^= 1  # flip bit 2

s = gf2_mat_vec(H, r)
print("received:", r)
print("syndrome:", s)
# ==> received: [1, 0, 0, 1, 0, 1, 0]
# ==> syndrome: [0, 1, 1]
