# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 33: Fiat-Shamir in the QROM
# Section: "Three-move sigma with Fiat-Shamir"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch33-fiat-shamir-qrom/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch33/02-lazyoracle.py

# Block 2: pedagogical slice of fiat_shamir_qrom.fiat_shamir.fs_prove
# and fs_verify (stdlib only).

import hashlib

PRIME, ORDER, G = 2027, 1013, 4  # toy group reused from Ch 32 toy_kzg

class LazyOracle:
    def __init__(self, seed=b""):
        self.seed = seed
        self.cache = {}

    def query(self, x):
        if x in self.cache:
            return self.cache[x]
        digest = hashlib.sha256(self.seed + x).digest()
        value = int.from_bytes(digest, "big") % ORDER
        self.cache[x] = value
        return value

def transcript_bytes(pk, commitment):
    return pk.to_bytes(4, "big") + commitment.to_bytes(4, "big")

def fs_prove(sk, pk, nonce, oracle):
    commitment = pow(G, nonce, PRIME)
    challenge = oracle.query(transcript_bytes(pk, commitment))
    response = (nonce + challenge * sk) % ORDER
    return commitment, response

def fs_verify(pk, commitment, response, oracle):
    challenge = oracle.query(transcript_bytes(pk, commitment))
    lhs = pow(G, response, PRIME)
    rhs = (commitment * pow(pk, challenge, PRIME)) % PRIME
    return lhs == rhs

sk = 42
pk = pow(G, sk, PRIME)
oracle = LazyOracle(seed=b"ch33-demo")
commitment, response = fs_prove(sk, pk, nonce=200, oracle=oracle)
print(fs_verify(pk, commitment, response, oracle))
# ==> True
