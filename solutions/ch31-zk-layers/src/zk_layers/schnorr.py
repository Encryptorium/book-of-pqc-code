"""Schnorr identification on a toy group, for Chapter 31's opening.

Chapter 31 opens on the smallest proof Part VI uses and shows its three
properties on one protocol. ``verify``, ``extract`` and ``simulate`` are
the chapter's printed block verbatim:

- completeness: an honest run passes ``verify``;
- knowledge soundness: two accepted answers to one commitment give
  the secret away, and ``extract`` computes it from them;
- zero knowledge: ``simulate`` builds an accepted transcript without the
  secret, and its transcripts are distributed exactly as the real ones.

The group is the one Chapters 32 and 33 use: the subgroup of prime order
``N = 1013`` that ``G = 4`` generates in the integers modulo
``P = 2027 = 2 * 1013 + 1``. It is small enough for a test to list every
transcript for a challenge, which is how the suite compares the real and
simulated distributions as sets.

``verify`` trusts its public key to lie in that subgroup, as an honestly
generated key does. Chapter 33's verifier checks the key before anything
else.
"""

P, N, G = 2027, 1013, 4  # G generates the subgroup of prime order N mod P


def verify(h, a, e, z):
    return pow(G, z, P) == a * pow(h, e, P) % P


def extract(e1, z1, e2, z2):
    # Two accepted answers to one commitment, for challenges e1 != e2.
    return (z1 - z2) * pow(e1 - e2, -1, N) % N


def simulate(h, e, z):
    # The commitment that makes (a, e, z) accepted, computed without x.
    return pow(G, z, P) * pow(h, -e, P) % P
