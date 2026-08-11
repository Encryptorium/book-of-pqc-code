# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 20: McEliece: the original PQC
# Section: "Full McEliece keygen, encrypt, decrypt"
# https://book.encryptorium.com/part-4-code-isogeny/ch20-mceliece-the-original-pqc/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch20/08-full-mceliece-keygen-encrypt-decrypt.py

import sys, pathlib, random
sys.path.insert(0, str(pathlib.Path("solutions/ch20-mceliece/src")))
from mceliece import keygen, encrypt, decrypt

pub, sec = keygen(m=4, t=2, irred=0b10011, rng=random.Random(42))
print(f"public key: {pub['k']}x{pub['n']} matrix ({pub['k']*pub['n']} bits = {pub['k']*pub['n']//8} bytes)")

msg = [1, 0, 1, 1, 0, 0, 1, 0]
ct = encrypt(pub, msg, rng=random.Random(99))
recovered = decrypt(sec, ct)
print(f"message:   {msg}")
print(f"recovered: {recovered}")
print(f"match: {msg == recovered}")
# ==> public key: 8x16 matrix (128 bits = 16 bytes)
# ==> message:   [1, 0, 1, 1, 0, 0, 1, 0]
# ==> recovered: [1, 0, 1, 1, 0, 0, 1, 0]
# ==> match: True
