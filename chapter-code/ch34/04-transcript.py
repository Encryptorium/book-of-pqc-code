# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 34: STARKs and FRI revisited
# Section: "4.3 FRI with Fiat-Shamir challenges"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch34-starks-fri-revisited/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch34/04-transcript.py

# Block 4: pedagogical slice of starks.fri_full.fri_prove folding loop
# plus starks.transcript.Transcript.squeeze_int (stdlib only).

import hashlib

class Transcript:
    def __init__(self, sep):
        self.state = hashlib.sha256(b"ch34-tx|" + sep).digest()
        self.counter = 0

    def absorb(self, label, data):
        length = len(data).to_bytes(8, "big")
        self.state = hashlib.sha256(self.state + label + length + data).digest()

    def squeeze_int(self, label, modulus):
        ctr = self.counter.to_bytes(8, "big")
        self.counter += 1
        buf = hashlib.sha256(self.state + label + ctr).digest()
        self.state = hashlib.sha256(self.state + buf).digest()
        return int.from_bytes(buf, "big") % modulus

def fold_once(cw, dom, beta, p):
    if len(cw) != len(dom) or len(cw) & 1:
        raise ValueError("codeword must be even-length and match domain")
    half = len(cw) // 2
    two_inv = pow(2, -1, p)
    new_cw, new_dom = [], []
    # In a cyclic-group domain laid out as powers of a single generator,
    # x and -x sit half the domain apart, so cw[i + half] is f(-x).
    for i in range(half):
        fx, f_neg, x = cw[i], cw[i + half], dom[i]
        even = ((fx + f_neg) * two_inv) % p
        odd = ((fx - f_neg) * two_inv) % p
        odd = (odd * pow(x, -1, p)) % p
        new_cw.append((even + beta * odd) % p)
        new_dom.append((x * x) % p)
    return new_cw, new_dom

PRIME = 97
codeword = [95, 73, 80, 45, 24, 3, 63, 18, 38, 81, 79, 6, 9, 53, 69, 41,
            75, 50, 76, 28, 2, 78, 54, 93, 46, 92, 33, 46, 56, 12, 85, 68]
domain = [5, 43, 40, 53, 29, 36, 38, 94, 13, 73, 7, 2, 56, 16, 60, 31,
          92, 54, 57, 44, 68, 61, 59, 3, 84, 24, 90, 95, 41, 81, 37, 66]

tx = Transcript(b"ch34-stark")
betas = []
for j in range(3):
    beta = tx.squeeze_int(b"fri-beta-" + j.to_bytes(4, "big"), PRIME)
    betas.append(beta)
    codeword, domain = fold_once(codeword, domain, beta, PRIME)

print("betas mod 97:", betas)
print("folded codeword after 3 rounds:", codeword)
# ==> betas mod 97: [35, 40, 48]
# ==> folded codeword after 3 rounds: [85, 85, 85, 85]
