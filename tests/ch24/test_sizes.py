"""Key-size and Kipnis-Shamir cost arithmetic, pinned to the round-2 packages."""

import math

import pytest

from multivariate.sizes import (
    ROUND2_SIZES,
    kipnis_shamir_log2_cost,
    kipnis_shamir_search_exponent,
    upper_triangular_count,
    uov_public_key_bytes,
)


def test_upper_triangular_count_small_cases():
    assert upper_triangular_count(0) == 0
    assert upper_triangular_count(1) == 1
    assert upper_triangular_count(2) == 3
    assert upper_triangular_count(5) == 15


def test_upper_triangular_count_at_uov_Is():
    assert upper_triangular_count(160) == 12_880


def test_upper_triangular_count_rejects_negative_n():
    with pytest.raises(ValueError):
        upper_triangular_count(-1)


def test_uov_Is_public_key_matches_the_specification():
    """uov-Is expanded public key is 412,160 bytes in Table 1 of the round-2 spec."""
    assert uov_public_key_bytes(n=160, m=64, elements_per_byte=2) == 412_160
    assert uov_public_key_bytes(n=160, m=64, elements_per_byte=2) == ROUND2_SIZES["uov-Is"].public_key


def test_uov_Ip_public_key_matches_the_specification():
    """uov-Ip is over GF(256), so one element per byte, and n = 112, m = 44."""
    assert uov_public_key_bytes(n=112, m=44, elements_per_byte=1) == 278_432
    assert uov_public_key_bytes(n=112, m=44, elements_per_byte=1) == ROUND2_SIZES["uov-Ip"].public_key


def test_compact_public_key_is_far_smaller_than_the_expanded_one():
    """The pkc version stores 66,576 bytes where the classic one stores 412,160."""
    expanded = ROUND2_SIZES["uov-Is"].public_key
    compact = ROUND2_SIZES["uov-Is-pkc"].public_key
    assert compact < expanded
    assert 6.1 < expanded / compact < 6.3


def test_uov_Is_signature_is_packed_nibbles_plus_a_salt():
    """96 bytes is 160 GF(16) nibbles (80 bytes) plus a 16-byte salt."""
    packed = 160 // 2
    salt = 16
    assert packed + salt == ROUND2_SIZES["uov-Is"].signature


def test_uov_public_key_bytes_rejects_zero_packing():
    with pytest.raises(ValueError):
        uov_public_key_bytes(n=10, m=2, elements_per_byte=0)


def test_balanced_parameters_have_a_vanishing_search_exponent():
    """n = 2m is the polynomial-time Kipnis-Shamir case."""
    assert kipnis_shamir_search_exponent(q=16, n=128, m=64) == 0.0


def test_search_exponent_at_uov_Is():
    """q^(n - 2m) = 16^32 = 2^128 for uov-Is."""
    assert kipnis_shamir_search_exponent(q=16, n=160, m=64) == pytest.approx(128.0)


def test_search_exponent_grows_with_the_gap():
    """Each extra vinegar variable multiplies the cost by q."""
    base = kipnis_shamir_search_exponent(q=16, n=160, m=64)
    wider = kipnis_shamir_search_exponent(q=16, n=161, m=64)
    assert wider - base == pytest.approx(math.log2(16))


def test_literature_cost_is_near_the_specification_estimate():
    """The spec tabulates 154 bits for uov-Is; the n^4 form lands within a few bits."""
    estimate = kipnis_shamir_log2_cost(q=16, n=160, m=64)
    assert 150.0 < estimate < 160.0


def test_cost_model_rejects_overbalanced_parameters():
    with pytest.raises(ValueError):
        kipnis_shamir_log2_cost(q=16, n=100, m=64)


def test_round2_sizes_are_internally_consistent():
    """Every recorded set names its source and targets a NIST level."""
    for name, entry in ROUND2_SIZES.items():
        assert entry.name == name
        assert entry.nist_level in (1, 3, 5)
        assert entry.public_key > 0
        assert entry.signature > 0
        assert entry.source


def test_mayo1_is_smaller_keyed_and_larger_signed_than_uov_Is():
    """The headline multivariate tradeoff, as the chapter's table states it."""
    uov = ROUND2_SIZES["uov-Is"]
    mayo = ROUND2_SIZES["MAYO1"]
    assert mayo.public_key < uov.public_key
    assert mayo.signature > uov.signature
