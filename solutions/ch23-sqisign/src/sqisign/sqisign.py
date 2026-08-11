"""Toy SQIsign at p = 431 with explicit simplifications.

This is a pedagogical toy that captures the SHAPE of SQIsign but
substitutes BFS over the supersingular isogeny graph for the scheme's
quaternion-side search.  Real SQIsign finds the connecting isogeny by
sampling a bounded-norm quaternion from an ideal intersection and
translating it back to an isogeny; BFS would be infeasible at
cryptographic primes.  Round-1 SQIsign used the KLPT algorithm here
(Kohel et al. 2014), and round 2 removed that material outright:
see specification v2.0.1 section 1.3.

Toy structure:

  KeyGen:
    Pick a random walk W_sec from E_0.  Walk it to obtain the secret
    curve E_sec.  Public key = E_sec (or its j-invariant).

  Sign(m):
    Derive a deterministic walk W_chal from Hash(m, pk).  Walk it
    from E_0 to obtain the challenge curve E_chal.  Use BFS to find
    a connecting isogeny path sigma from E_chal to E_sec.  Output
    sigma as the signature.

  Verify(m, sigma):
    Recompute E_chal from Hash(m, pk).  Walk sigma from E_chal.
    Check that the resulting curve has the same j-invariant as E_sec.

Simplifications relative to real SQIsign:
  - BFS replaces the quaternion-side ideal search that finds the
    response isogeny.
  - The signature is a sequence of (degree, kernel_x_coord) steps
    rather than interpolation data (point images carried as a
    change-of-basis matrix alongside an auxiliary curve).
  - No zero-knowledge proof structure (real SQIsign uses Fiat-Shamir
    on a sigma protocol).
  - Parameters are tiny (p = 431, walk length 4-6 steps).

References:
  The SQIsign Team 2025.  SQIsign specification v2.0.1 (round 2).
  De Feo, Kohel, Leroux, Petit, Wesolowski 2020.  SQIsign.
  Kohel, Lauter, Petit, Tignol 2014.  KLPT, used by round 1 only.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional

from sqisign.fp2 import fp2_eq
from sqisign.curve import Fp2, Point, j_invariant
from sqisign.deuring import A0, B0
from sqisign.graph import neighbors, find_path, walk_path
from sqisign.velu import velu_isogeny


P = 431
SECRET_WALK_LENGTH = 4   # number of isogeny steps in keygen
CHALLENGE_WALK_LENGTH = 3  # number of isogeny steps in challenge derivation


@dataclass
class PublicKey:
    """A public key is a pair (a, b) defining E_pk: y^2 = x^3 + a*x + b."""
    a: Fp2
    b: Fp2

    def j(self) -> Fp2:
        return j_invariant(self.a, self.b, P)


@dataclass
class SecretKey:
    """The secret key includes the public coefficients and the walk that
    produced them, expressed as (degree, kernel_index) pairs.

    kernel_index selects among the enumerated kernels of the given degree
    on the current curve at that step, in the canonical neighbor order.
    """
    pk: PublicKey
    walk: list[tuple[int, int]]


# A signature is a sequence of (degree, kernel_generator) steps.
Signature = list[tuple[int, Point]]


def _hash_to_walk(message: bytes, pk: PublicKey, length: int) -> list[tuple[int, int]]:
    """Derive a deterministic walk from Hash(message, pk).

    The walk is a list of (degree, kernel_index) pairs.  Each step uses
    one byte from the SHA-256 digest: high bit picks degree (2 or 3),
    remaining bits pick kernel_index modulo the available kernel count.
    """
    h = hashlib.sha256()
    h.update(message)
    h.update(pk.a[0].to_bytes(2, "big"))
    h.update(pk.a[1].to_bytes(2, "big"))
    h.update(pk.b[0].to_bytes(2, "big"))
    h.update(pk.b[1].to_bytes(2, "big"))
    digest = h.digest()
    # Repeat digest if longer walk is requested.
    while len(digest) < length:
        digest = digest + hashlib.sha256(digest).digest()

    walk: list[tuple[int, int]] = []
    for i in range(length):
        byte = digest[i]
        degree = 2 if (byte & 0x80) == 0 else 3
        kernel_index = byte & 0x7F
        walk.append((degree, kernel_index))
    return walk


def _walk_with_indices(a: Fp2, b: Fp2, walk: list[tuple[int, int]]
                       ) -> tuple[Fp2, Fp2, list[tuple[int, Point]]]:
    """Walk a sequence of (degree, kernel_index) steps from (a, b).

    At each step, enumerate neighbors of the current curve and pick the
    one at position kernel_index modulo the count of degree-`degree`
    neighbors.  Returns the final (a, b) and the resolved path
    (degree, kernel_generator) pairs.
    """
    resolved: list[tuple[int, Point]] = []
    cur_a, cur_b = a, b
    for degree, idx in walk:
        edges = [e for e in neighbors(cur_a, cur_b, P) if e[0] == degree]
        if not edges:
            raise RuntimeError(f"no degree-{degree} edges from current curve")
        chosen = edges[idx % len(edges)]
        _deg, kernel_gen, na, nb = chosen
        resolved.append((degree, kernel_gen))
        cur_a, cur_b = na, nb
    return cur_a, cur_b, resolved


# ---- SQIsign protocol -------------------------------------------------------

def keygen(seed: bytes = b"") -> SecretKey:
    """Generate a (PublicKey, SecretKey) pair via a deterministic random walk.

    The walk is derived from the seed (default empty), so calling
    keygen with the same seed always returns the same key.
    """
    h = hashlib.sha256(seed).digest()
    walk = []
    for i in range(SECRET_WALK_LENGTH):
        byte = h[i % len(h)]
        degree = 2 if (byte & 0x80) == 0 else 3
        kernel_index = byte & 0x7F
        walk.append((degree, kernel_index))
    a_pk, b_pk, _ = _walk_with_indices(A0, B0, walk)
    pk = PublicKey(a=a_pk, b=b_pk)
    return SecretKey(pk=pk, walk=walk)


def sign(message: bytes, sk: SecretKey) -> Signature:
    """Sign a message: derive E_chal, find connecting isogeny to E_pk."""
    chal_walk = _hash_to_walk(message, sk.pk, CHALLENGE_WALK_LENGTH)
    a_chal, b_chal, _ = _walk_with_indices(A0, B0, chal_walk)
    path = find_path(a_chal, b_chal, sk.pk.a, sk.pk.b, P, max_depth=8)
    if path is None:
        raise RuntimeError(
            "BFS failed to connect challenge curve to public key curve"
        )
    return path


def verify(message: bytes, signature: Signature, pk: PublicKey) -> bool:
    """Verify a signature against a public key."""
    chal_walk = _hash_to_walk(message, pk, CHALLENGE_WALK_LENGTH)
    a_chal, b_chal, _ = _walk_with_indices(A0, B0, chal_walk)
    a_end, b_end = walk_path(a_chal, b_chal, signature, P)
    return fp2_eq(j_invariant(a_end, b_end, P), pk.j(), P)
