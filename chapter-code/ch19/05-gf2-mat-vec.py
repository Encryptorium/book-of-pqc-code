# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 19: Coding theory for cryptographers
# Section: "Syndrome table decoding"
# https://book.encryptorium.com/part-4-code-isogeny/ch19-coding-theory-for-cryptographers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch19/05-gf2-mat-vec.py

H = [
    [1, 1, 0, 1, 1, 0, 0],
    [1, 0, 1, 1, 0, 1, 0],
    [0, 1, 1, 1, 0, 0, 1],
]

def gf2_mat_vec(A, v):
    return [sum(a * x for a, x in zip(row, v)) % 2 for row in A]

# Encode the zero message, flip bits 0 and 1 (weight-2 error).
c = [0, 0, 0, 0, 0, 0, 0]
e = [1, 1, 0, 0, 0, 0, 0]
r = [(ci ^ ei) for ci, ei in zip(c, e)]
s = gf2_mat_vec(H, r)
print("syndrome of weight-2 error:", s)
# ==> syndrome of weight-2 error: [0, 1, 1]

# Syndrome (0,1,1) maps to position 2, not positions 0 and 1.
# The decoder "corrects" to the wrong codeword.
print("decoder thinks error is at position 2")
# ==> decoder thinks error is at position 2
