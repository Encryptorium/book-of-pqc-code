"""Tests for starks.transcript."""

from __future__ import annotations

import pytest

from starks.transcript import Transcript


def test_deterministic_given_identical_absorbs():
    t1 = Transcript(b"test-ds")
    t2 = Transcript(b"test-ds")
    t1.absorb(b"a", b"hello")
    t2.absorb(b"a", b"hello")
    assert t1.squeeze_int(b"c", 1000) == t2.squeeze_int(b"c", 1000)
    assert t1.squeeze_int(b"c", 1000) == t2.squeeze_int(b"c", 1000)


def test_different_domain_seps_diverge():
    t1 = Transcript(b"ds-A")
    t2 = Transcript(b"ds-B")
    t1.absorb(b"a", b"data")
    t2.absorb(b"a", b"data")
    assert t1.squeeze_int(b"c", 1000) != t2.squeeze_int(b"c", 1000)


def test_different_labels_diverge():
    t = Transcript(b"ds")
    t.absorb(b"a", b"data")
    x = t.squeeze_int(b"L1", 1000)
    y = t.squeeze_int(b"L2", 1000)
    assert x != y


def test_squeeze_index_bounded():
    t = Transcript(b"ds")
    t.absorb(b"a", b"data")
    for k in range(100):
        idx = t.squeeze_index(b"q-" + k.to_bytes(4, "big"), 32)
        assert 0 <= idx < 32


def test_absorb_int_roundtrip():
    t1 = Transcript(b"ds")
    t2 = Transcript(b"ds")
    t1.absorb_int(b"v", 12345, num_bytes=4)
    t2.absorb(b"v", (12345).to_bytes(4, "big"))
    # Both transcripts should hash b"v" || length-prefix || bytes.
    # absorb_int builds the same byte sequence as the manual absorb
    # (length prefix is identical because num_bytes is the same).
    assert t1.state() == t2.state()


def test_absorb_negative_value_raises():
    t = Transcript(b"ds")
    with pytest.raises(ValueError):
        t.absorb_int(b"v", -1)


def test_absorb_oversized_value_raises():
    t = Transcript(b"ds")
    with pytest.raises(ValueError):
        t.absorb_int(b"v", 2 ** 16, num_bytes=2)


def test_absorb_zero_num_bytes_raises():
    t = Transcript(b"ds")
    with pytest.raises(ValueError):
        t.absorb_int(b"v", 0, num_bytes=0)


def test_squeeze_zero_modulus_raises():
    t = Transcript(b"ds")
    with pytest.raises(ValueError):
        t.squeeze_int(b"x", 0)


def test_squeeze_index_zero_domain_raises():
    t = Transcript(b"ds")
    with pytest.raises(ValueError):
        t.squeeze_index(b"x", 0)


def test_non_bytes_domain_sep_raises():
    with pytest.raises(ValueError):
        Transcript("not-bytes")  # type: ignore[arg-type]


def test_non_bytes_label_raises():
    t = Transcript(b"ds")
    with pytest.raises(ValueError):
        t.absorb("label", b"data")  # type: ignore[arg-type]


def test_non_bytes_data_raises():
    t = Transcript(b"ds")
    with pytest.raises(ValueError):
        t.absorb(b"label", 5)  # type: ignore[arg-type]


def test_squeeze_absorbs_back():
    # After squeezing, a subsequent absorb must produce a different
    # state than if the squeeze had not happened (the squeeze folds
    # the squeezed bytes back into the state).
    t1 = Transcript(b"ds")
    t1.absorb(b"a", b"x")
    _ = t1.squeeze_int(b"q", 97)
    t1.absorb(b"b", b"y")
    state_with_squeeze = t1.state()

    t2 = Transcript(b"ds")
    t2.absorb(b"a", b"x")
    t2.absorb(b"b", b"y")
    state_without_squeeze = t2.state()

    assert state_with_squeeze != state_without_squeeze
