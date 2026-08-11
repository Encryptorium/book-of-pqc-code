# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 20: McEliece: the original PQC
# Section: "Round-trip across 50 key seeds"
# https://book.encryptorium.com/part-4-code-isogeny/ch20-mceliece-the-original-pqc/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch20/09-round-trip-across-50-key-seeds.py

import sys, pathlib, random
sys.path.insert(0, str(pathlib.Path("solutions/ch20-mceliece/src")))
from mceliece import keygen, encrypt, decrypt

failures = 0
for seed in range(50):
    r = random.Random(seed)
    p, s = keygen(m=4, t=2, irred=0b10011, rng=r)
    trial_msg = [r.randint(0, 1) for _ in range(p['k'])]
    c = encrypt(p, trial_msg, rng=random.Random(seed + 1000))
    if decrypt(s, c) != trial_msg:
        failures += 1
print(f"50 seeds, random messages: {failures} failures")
# ==> 50 seeds, random messages: 0 failures
