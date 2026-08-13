# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 32: PQ-secure commitment schemes
# Section: "KZG: trapdoor in the structured reference string"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch32-commitment-schemes/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch32/01-srs-setup.py

# Block 1: pedagogical slice of commitment_schemes.toy_kzg.setup and commit (stdlib only).

PRIME = 2027       # 2 * 1013 + 1 (safe prime)
ORDER = 1013       # prime order of the subgroup
GEN = 4            # generator of the order-1013 subgroup

def srs_setup(degree, tau):
    powers = []
    tau_power = 1
    for _ in range(degree + 1):
        powers.append(pow(GEN, tau_power, PRIME))
        tau_power = (tau_power * tau) % ORDER
    return powers

def commit(coeffs, srs):
    result = 1
    for c, power in zip(coeffs, srs):
        result = (result * pow(power, c, PRIME)) % PRIME
    return result

tau = 500
srs = srs_setup(degree=4, tau=tau)
p = [7, 11, 13, 17, 19]              # p(x) = 7 + 11x + 13x^2 + 17x^3 + 19x^4
C = commit(p, srs)
print(f"|SRS| = {len(srs)}, C = {C}")
# ==> |SRS| = 5, C = 1499
