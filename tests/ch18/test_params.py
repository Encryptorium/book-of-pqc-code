"""The six SHA-2 parameter sets, checked against FIPS 205 Table 2."""

import math

import pytest

from hash_cryptanalysis.params import (
    SHA2_PARAMETER_SETS,
    by_name,
    wots_ell,
    wots_ell_parts,
)

SHORT_NAMES = [ps.name.rsplit("-", 1)[-1] for ps in SHA2_PARAMETER_SETS]


def test_six_sha2_sets_in_table_2_order(sha2_sets):
    assert [ps.name.rsplit("-", 1)[-1] for ps in sha2_sets] == [
        "128s",
        "128f",
        "192s",
        "192f",
        "256s",
        "256f",
    ]


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_h_prime_matches_table_2(short, fips205_table_2):
    """h' is tabulated by FIPS 205, and h = d * h' must hold exactly."""
    ps = by_name(short)
    expected_h_prime = fips205_table_2[short][0]
    assert ps.h_prime == expected_h_prime
    assert ps.d * ps.h_prime == ps.h


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_category_matches_table_2(short, fips205_table_2):
    ps = by_name(short)
    assert ps.category == fips205_table_2[short][1]


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_t_is_two_to_the_a(short):
    ps = by_name(short)
    assert ps.t == 2**ps.a


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_n_bits_is_eight_times_n_bytes(short):
    ps = by_name(short)
    assert ps.n_bits == 8 * ps.n_bytes


@pytest.mark.parametrize(
    "n_bytes,expected_ell_1,expected_ell_2",
    [(16, 32, 3), (24, 48, 3), (32, 64, 3)],
)
def test_wots_ell_parts_at_w16(n_bytes, expected_ell_1, expected_ell_2):
    """FIPS 205 Section 5: at lgw = 4, len1 = 2n and len2 = 3, so len = 2n + 3."""
    ell_1, ell_2 = wots_ell_parts(n_bytes, 16)
    assert (ell_1, ell_2) == (expected_ell_1, expected_ell_2)
    assert ell_1 == 2 * n_bytes
    assert wots_ell(n_bytes, 16) == 2 * n_bytes + 3


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_ell_1_covers_the_digest(short):
    """The message chains must carry every bit of the n-byte digest."""
    ps = by_name(short)
    ell_1, _ = wots_ell_parts(ps.n_bytes, ps.w)
    lg_w = int(math.log2(ps.w))
    assert ell_1 * lg_w >= 8 * ps.n_bytes


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_ell_2_covers_the_maximum_checksum(short):
    """The checksum chains must carry the largest checksum ell_1 digits allow."""
    ps = by_name(short)
    ell_1, ell_2 = wots_ell_parts(ps.n_bytes, ps.w)
    max_checksum = ell_1 * (ps.w - 1)
    assert ps.w**ell_2 > max_checksum


def test_by_name_accepts_both_forms():
    assert by_name("128s") is by_name("SLH-DSA-SHA2-128s")


def test_by_name_rejects_an_unknown_set():
    with pytest.raises(KeyError):
        by_name("SLH-DSA-SHA2-512s")
