"""Tests for L-tree compression of WOTS+ public keys."""

import hashlib

from wots_xmss.ltree import ltree


SEED = b"ltree-test-seed"


def _make_values(count: int) -> list[bytes]:
    """Generate *count* deterministic 32-byte values."""
    return [
        hashlib.sha256(SEED + i.to_bytes(4, "big")).digest()
        for i in range(count)
    ]


def test_ltree_power_of_two():
    """L-tree of 4 values produces a single 32-byte root."""
    values = _make_values(4)
    root = ltree(values, SEED)
    assert len(root) == 32


def test_ltree_odd_count_3():
    """L-tree of 3 values handles odd-node promotion."""
    values = _make_values(3)
    root = ltree(values, SEED)
    assert len(root) == 32


def test_ltree_odd_count_5():
    """L-tree of 5 values handles promotion at the first level."""
    values = _make_values(5)
    root = ltree(values, SEED)
    assert len(root) == 32


def test_ltree_67_values():
    """L-tree of 67 values (the WOTS+ ell at w=16, n=32)."""
    values = _make_values(67)
    root = ltree(values, SEED)
    assert len(root) == 32


def test_ltree_deterministic():
    """Same inputs produce the same root."""
    values = _make_values(67)
    r1 = ltree(values, SEED)
    r2 = ltree(values, SEED)
    assert r1 == r2


def test_ltree_different_seed():
    """Different seeds produce different roots."""
    values = _make_values(67)
    r1 = ltree(values, b"seed-a")
    r2 = ltree(values, b"seed-b")
    assert r1 != r2


def test_ltree_single_value():
    """L-tree of 1 value returns that value unchanged."""
    values = _make_values(1)
    root = ltree(values, SEED)
    assert root == values[0]


def test_ltree_two_values():
    """L-tree of 2 values is a single hash of the pair."""
    values = _make_values(2)
    root = ltree(values, SEED)
    expected = hashlib.sha256(
        SEED
        + (0).to_bytes(4, "big")
        + (0).to_bytes(4, "big")
        + values[0]
        + values[1]
    ).digest()
    assert root == expected
