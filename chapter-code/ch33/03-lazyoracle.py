# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 33: Fiat-Shamir in the QROM
# Section: "Multi-round Fiat-Shamir"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch33-fiat-shamir-qrom/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch33/03-lazyoracle.py

# Block 3: pedagogical slice of
# fiat_shamir_qrom.measure_and_reprogram.simulate_classical_extraction
# (stdlib only).

import hashlib

class LazyOracle:
    def __init__(self, modulus, seed=b""):
        self.modulus = modulus
        self.seed = seed
        self.cache = {}
        self.programmed = {}
        self.log = []

    def query(self, x):
        self.log.append(x)
        if x in self.cache:
            return self.cache[x]
        if x in self.programmed:
            value = self.programmed[x]
        else:
            digest = hashlib.sha256(self.seed + x).digest()
            value = int.from_bytes(digest, "big") % self.modulus
        self.cache[x] = value
        return value

    def reprogram(self, x, value):
        if x in self.cache:
            raise ValueError("cannot reprogram a queried point")
        if value < 0 or value >= self.modulus:
            raise ValueError("value outside oracle range")
        self.programmed[x] = value

def adversary(oracle):
    return tuple(oracle.query(t) for t in (b"q0", b"q1", b"q2"))

MODULUS, SEED = 1013, b"mr-demo"
first_oracle = LazyOracle(MODULUS, SEED)
first_output = adversary(first_oracle)

measured_index = 1
measured_input = first_oracle.log[measured_index]
second_oracle = LazyOracle(MODULUS, SEED)
second_oracle.reprogram(measured_input, 777)
second_output = adversary(second_oracle)

print(second_output[measured_index] == 777)
# ==> True
