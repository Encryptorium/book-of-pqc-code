# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 20: McEliece: the original PQC
# Section: "A toy McEliece round-trip"
# https://book.encryptorium.com/part-4-code-isogeny/ch20-mceliece-the-original-pqc/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch20/02-a-toy-mceliece-round-trip.py

G_pub = [[1,1,0,0,1,0,0],[0,1,1,0,1,0,1],[0,0,0,1,1,0,1],[1,0,0,1,0,1,0]]

msg = [1, 0, 1, 1]
c = [0] * 7
for i, mi in enumerate(msg):
    if mi:
        c = [x ^ y for x, y in zip(c, G_pub[i])]

e = [0, 0, 0, 0, 1, 0, 0]  # weight-1 error at position 4
ct = [x ^ y for x, y in zip(c, e)]
print("m * G_pub =", c)
print("ciphertext =", ct)
# ==> m * G_pub = [0, 1, 0, 0, 0, 1, 1]
# ==> ciphertext = [0, 1, 0, 0, 1, 1, 1]
