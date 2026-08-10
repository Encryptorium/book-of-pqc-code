"""Tests for base-w encoding at w=4, w=16, and w=256."""

from wots_xmss.wots import base_w


def test_base_w_16_single_byte():
    """0xAB in base 16 is [10, 11]."""
    result = base_w(b"\xAB", 16, 2)
    assert result == [10, 11]


def test_base_w_16_two_bytes():
    """0xABCD in base 16 is [10, 11, 12, 13]."""
    result = base_w(b"\xAB\xCD", 16, 4)
    assert result == [10, 11, 12, 13]


def test_base_w_4_single_byte():
    """0xAB = 10101011 in base 4 is [2, 2, 2, 3]."""
    result = base_w(b"\xAB", 4, 4)
    assert result == [2, 2, 2, 3]


def test_base_w_256_single_byte():
    """In base 256, each byte is one digit."""
    result = base_w(b"\xAB", 256, 1)
    assert result == [0xAB]


def test_base_w_256_two_bytes():
    result = base_w(b"\x00\xFF", 256, 2)
    assert result == [0, 255]


def test_base_w_16_all_zeros():
    result = base_w(b"\x00\x00", 16, 4)
    assert result == [0, 0, 0, 0]


def test_base_w_16_all_ones():
    result = base_w(b"\xFF\xFF", 16, 4)
    assert result == [15, 15, 15, 15]


def test_base_w_truncation():
    """out_len shorter than full encoding truncates."""
    result = base_w(b"\xAB\xCD", 16, 3)
    assert result == [10, 11, 12]


def test_base_w_4_full_byte():
    """0xFF = 11111111 in base 4 is [3, 3, 3, 3]."""
    result = base_w(b"\xFF", 4, 4)
    assert result == [3, 3, 3, 3]


def test_base_w_4_zero_byte():
    result = base_w(b"\x00", 4, 4)
    assert result == [0, 0, 0, 0]
