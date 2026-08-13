# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 32: PQ-secure commitment schemes
# Section: "KZG: trapdoor in the structured reference string"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch32-commitment-schemes/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch32/02-shor-recover-tau.py

# Block 2: pedagogical slice of toy_kzg.shor_recover_tau and forge_opening (stdlib only).

PRIME = 2027
ORDER = 1013
GEN = 4

def shor_recover_tau(srs):
    # Recover tau from (g, g^tau). Classical brute force here; Shor is poly(log q).
    g_tau = srs[1]
    for candidate in range(1, ORDER):
        if pow(GEN, candidate, PRIME) == g_tau:
            return candidate
    raise ValueError("tau not recoverable")

def forge_opening(C, z, y_fake, tau):
    # Given tau, W = (C * g^{-y_fake})^(1 / (tau - z)) in the order-ORDER subgroup.
    # Edge case: at z == tau the formula divides by zero, forcing y == p(tau);
    # the forger picks any z != tau.
    if (tau - z) % ORDER == 0:
        raise ValueError("z == tau: verification forces y = p(tau), no forgery possible at this point")
    numerator = (C * pow(GEN, (-y_fake) % ORDER, PRIME)) % PRIME
    inv_tz = pow((tau - z) % ORDER, -1, ORDER)
    return pow(numerator, inv_tz, PRIME)

# Prover's honest state from Block 1 (reproduced here; blocks run in isolation).
def srs_setup(degree, tau):
    powers, tau_power = [], 1
    for _ in range(degree + 1):
        powers.append(pow(GEN, tau_power, PRIME))
        tau_power = (tau_power * tau) % ORDER
    return powers

def commit(coeffs, srs):
    r = 1
    for c, power in zip(coeffs, srs):
        r = (r * pow(power, c, PRIME)) % PRIME
    return r

tau_true = 777
srs = srs_setup(degree=4, tau=tau_true)
C = commit([2, 3, 5, 7, 11], srs)

recovered = shor_recover_tau(srs)
y_fake = 42
W_fake = forge_opening(C, z=100, y_fake=y_fake, tau=recovered)
print(f"recovered tau = {recovered}, forged W = {W_fake}")
# ==> recovered tau = 777, forged W = 1376
