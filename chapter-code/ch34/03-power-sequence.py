# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 34: STARKs and FRI revisited
# Section: "4.2 LDE"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch34-starks-fri-revisited/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch34/03-power-sequence.py

# Block 3: pedagogical slice of starks.lde.extend_polynomial and
# starks.arithmetization.interpolate_trace (stdlib only).

PRIME = 97
TRACE_GEN = 64    # order 8
LDE_GEN = 28      # order 32
COSET_SHIFT = 5   # outside the order-32 subgroup

def power_sequence(g, n, p):
    seq, x = [1], 1
    for _ in range(n - 1):
        x = (x * g) % p
        seq.append(x)
    return seq

def lagrange_coeffs(ys, xs, p):
    n = len(ys)
    coeffs = [0] * n
    for j in range(n):
        num = [1]
        denom = 1
        for m in range(n):
            if m == j:
                continue
            new = [0] * (len(num) + 1)
            for idx, c in enumerate(num):
                new[idx] = (new[idx] - c * xs[m]) % p
                new[idx + 1] = (new[idx + 1] + c) % p
            num = new
            denom = (denom * (xs[j] - xs[m])) % p
        scale = (ys[j] * pow(denom, -1, p)) % p
        for idx, c in enumerate(num):
            coeffs[idx] = (coeffs[idx] + scale * c) % p
    return coeffs

def eval_poly(coeffs, x, p):
    result = 0
    for c in reversed(coeffs):
        result = (result * x + c) % p
    return result

trace = [1, 1, 2, 3, 5, 8, 13, 21]
trace_dom = power_sequence(TRACE_GEN, 8, PRIME)
lde_dom = [(COSET_SHIFT * x) % PRIME for x in power_sequence(LDE_GEN, 32, PRIME)]

coeffs = lagrange_coeffs(trace, trace_dom, PRIME)
codeword = [eval_poly(coeffs, x, PRIME) for x in lde_dom]

print("trace domain size:", len(trace_dom), "LDE domain size:", len(lde_dom))
print("first four codeword values:", codeword[:4])
# ==> trace domain size: 8 LDE domain size: 32
# ==> first four codeword values: [95, 73, 80, 45]
