# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 19: Coding theory for cryptographers
# Section: "The [7,4,3] Hamming code"
# https://book.encryptorium.com/part-4-code-isogeny/ch19-coding-theory-for-cryptographers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch19/01-gf2-encode.py

# Generator matrix G for the [7,4,3] Hamming code (systematic form).
G = [
    [1, 0, 0, 0, 1, 1, 0],
    [0, 1, 0, 0, 1, 0, 1],
    [0, 0, 1, 0, 0, 1, 1],
    [0, 0, 0, 1, 1, 1, 1],
]

def gf2_encode(message, G):
    n = len(G[0])
    codeword = [0] * n
    for i, bit in enumerate(message):
        if bit:
            codeword = [(c ^ g) for c, g in zip(codeword, G[i])]
    return codeword

m = [1, 0, 1, 1]
c = gf2_encode(m, G)
print("codeword:", c)
# ==> codeword: [1, 0, 1, 1, 0, 1, 0]
