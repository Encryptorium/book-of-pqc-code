"""Component accounting reproduces every published FIPS 205 signature size.

The chapter checks this at SLH-DSA-SHA2-128s only, where 491 n-byte strings give
7,856 bytes. Agreement at all six sets is the stronger claim, because a formula
that happens to land on one row by coincidence will not land on six.
"""

import pytest

from hash_cryptanalysis.multitarget import (
    fors_signature_elements,
    signature_bytes,
    signature_elements,
    wots_signature_elements,
    xmss_auth_elements,
)
from hash_cryptanalysis.params import SHA2_PARAMETER_SETS, by_name

SHORT_NAMES = [ps.name.rsplit("-", 1)[-1] for ps in SHA2_PARAMETER_SETS]


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_signature_bytes_matches_table_2(short, fips205_table_2):
    ps = by_name(short)
    assert signature_bytes(ps) == fips205_table_2[short][2]


def test_128s_component_breakdown():
    """The chapter's own breakdown: 1 + 182 + 245 + 63 = 491 strings, 7,856 bytes."""
    ps = by_name("128s")
    assert fors_signature_elements(ps) == 182
    assert wots_signature_elements(ps) == 245
    assert xmss_auth_elements(ps) == 63
    assert signature_elements(ps) == 491
    assert signature_bytes(ps) == 7_856


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_xmss_auth_elements_equals_h(short):
    """d layers of h' nodes each is h nodes, which is why the column reads h."""
    ps = by_name(short)
    assert xmss_auth_elements(ps) == ps.h


@pytest.mark.parametrize("short", SHORT_NAMES)
def test_components_sum_to_the_total(short):
    ps = by_name(short)
    parts = (
        1
        + fors_signature_elements(ps)
        + wots_signature_elements(ps)
        + xmss_auth_elements(ps)
    )
    assert parts == signature_elements(ps)


def test_fast_sets_are_larger_than_small_sets_at_equal_n():
    """The f/s split is a size-for-speed trade, and it shows up in the totals."""
    for small, fast in (("128s", "128f"), ("192s", "192f"), ("256s", "256f")):
        assert signature_bytes(by_name(fast)) > signature_bytes(by_name(small))
