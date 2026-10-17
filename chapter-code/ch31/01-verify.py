# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 31: The four-layer decomposition
# Section: "Schnorr identification: three properties on one protocol"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch31-four-layer-decomposition/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch31/01-verify.py

# Block 1: pedagogical slice of Schnorr identification on a toy group
# (stdlib only): an honest run, an extraction, and a simulation.
P, N, G = 2027, 1013, 4  # G generates the subgroup of prime order N mod P


def verify(h, a, e, z):
    return pow(G, z, P) == a * pow(h, e, P) % P


def extract(e1, z1, e2, z2):
    # Two accepted answers to one commitment, for challenges e1 != e2.
    return (z1 - z2) * pow(e1 - e2, -1, N) % N


def simulate(h, e, z):
    # The commitment that makes (a, e, z) accepted, computed without x.
    return pow(G, z, P) * pow(h, -e, P) % P


x = 123                # the prover's secret
h = pow(G, x, P)       # its public key
r, e = 789, 456        # nonce and challenge, uniform in Z_N in a real run
a = pow(G, r, P)       # the prover's commitment
z = (r + e * x) % N    # its response
print(verify(h, a, e, z))
# ==> True

e2 = 31                # a second challenge to the same commitment
print(extract(e, z, e2, (r + e2 * x) % N))
# ==> 123

print(verify(h, simulate(h, e, 500), e, 500))
# ==> True

real = {(pow(G, r, P), e, (r + e * x) % N) for r in range(N)}
simulated = {(simulate(h, e, z), e, z) for z in range(N)}
print(real == simulated, len(real))
# ==> True 1013
