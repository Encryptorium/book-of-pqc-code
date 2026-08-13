# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 32: PQ-secure commitment schemes
# Section: "FRI: proximity as commitment"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch32-commitment-schemes/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch32/04-gen-domain.py

# Block 4: pedagogical slice of commitment_schemes.fri.fold_once (stdlib only).

PRIME = 97

def gen_domain(size, generator):
    # Multiplicative subgroup domain {1, g, g^2, ..., g^(size-1)}.
    out, current = [], 1
    for _ in range(size):
        out.append(current)
        current = (current * generator) % PRIME
    return out

def eval_poly(coeffs, x):
    result = 0
    for c in reversed(coeffs):
        result = (result * x + c) % PRIME
    return result

def fold_once(evals, domain, beta):
    half = len(domain) // 2
    two_inv = pow(2, -1, PRIME)
    new_evals, new_domain = [], []
    for i in range(half):
        x = domain[i]
        fx, f_neg_x = evals[i], evals[i + half]
        even = ((fx + f_neg_x) * two_inv) % PRIME
        odd = ((fx - f_neg_x) * two_inv * pow(x, -1, PRIME)) % PRIME
        new_evals.append((even + beta * odd) % PRIME)
        new_domain.append((x * x) % PRIME)
    return new_evals, new_domain

domain = gen_domain(16, generator=8)                 # order-16 subgroup of F_97^*
p = [7, 3]                                           # p(x) = 7 + 3x (degree 1)
evals = [eval_poly(p, x) for x in domain]
folded_once, domain_once = fold_once(evals, domain, beta=5)
folded_twice, domain_twice = fold_once(folded_once, domain_once, beta=11)
folded_thrice, _ = fold_once(folded_twice, domain_twice, beta=17)
print(f"after 3 folds: len = {len(folded_thrice)}, values = {folded_thrice}")
# ==> after 3 folds: len = 2, values = [22, 22]
