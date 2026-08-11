"""Tests for sparse binary vector sampling."""

import random

from hqc.sparse import sample_sparse


N = 83


def test_sparse_weight():
    rng = random.Random(42)
    vec = sample_sparse(N, 5, rng)
    assert sum(vec) == 5


def test_sparse_length():
    rng = random.Random(42)
    vec = sample_sparse(N, 3, rng)
    assert len(vec) == N


def test_sparse_binary():
    rng = random.Random(42)
    vec = sample_sparse(N, 4, rng)
    assert all(v in (0, 1) for v in vec)


def test_sparse_deterministic():
    vec1 = sample_sparse(N, 3, random.Random(99))
    vec2 = sample_sparse(N, 3, random.Random(99))
    assert vec1 == vec2


def test_sparse_different_seeds():
    vec1 = sample_sparse(N, 3, random.Random(1))
    vec2 = sample_sparse(N, 3, random.Random(2))
    assert vec1 != vec2
