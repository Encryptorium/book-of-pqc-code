# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 33: Fiat-Shamir in the QROM
# Section: "A Schnorr proof compiled three ways"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch33-fiat-shamir-qrom/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch33/01-interactive-prove.py

# Block 1: pedagogical slice of
# fiat_shamir_qrom.fiat_shamir.interactive_prove and interactive_verify
# (stdlib only).

PRIME, ORDER, G = 2027, 1013, 4  # toy group reused from Ch 32 toy_kzg

def interactive_prove(sk, challenge, nonce):
    commitment = pow(G, nonce, PRIME)
    response = (nonce + challenge * sk) % ORDER
    return commitment, response

def interactive_verify(pk, commitment, challenge, response):
    lhs = pow(G, response, PRIME)
    rhs = (commitment * pow(pk, challenge, PRIME)) % PRIME
    return lhs == rhs

sk = 123
pk = pow(G, sk, PRIME)
commitment, response = interactive_prove(sk, challenge=456, nonce=789)
print(interactive_verify(pk, commitment, 456, response))
# ==> True
