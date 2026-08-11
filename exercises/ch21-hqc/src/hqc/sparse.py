"""Sparse binary vector sampling with fixed Hamming weight."""

import random


def sample_sparse(n: int, w: int, rng: random.Random) -> list[int]:
    """Return a length-*n* binary vector with exactly *w* ones."""
    positions = rng.sample(range(n), w)
    vec = [0] * n
    for p in positions:
        vec[p] = 1
    return vec
