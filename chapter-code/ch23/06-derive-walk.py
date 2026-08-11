# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 23: SQIsign in a toy setting
# Section: "Toy SQIsign: keygen"
# https://book.encryptorium.com/part-4-code-isogeny/ch23-sqisign-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch23/06-derive-walk.py

import hashlib

# Stand-in for the standalone package's keygen.
# The chapter shows the structure; the full keygen lives in
# the ch23-sqisign package under solutions/.

SECRET_WALK_LENGTH = 4

def derive_walk(seed, length):
    h = hashlib.sha256(seed).digest()
    while len(h) < length:
        h = h + hashlib.sha256(h).digest()
    walk = []
    for i in range(length):
        byte = h[i]
        degree = 2 if (byte & 0x80) == 0 else 3
        kernel_index = byte & 0x7F
        walk.append((degree, kernel_index))
    return walk

walk = derive_walk(b"alice", SECRET_WALK_LENGTH)
print(walk)
# ==> [(2, 43), (3, 88), (2, 6), (3, 73)]
