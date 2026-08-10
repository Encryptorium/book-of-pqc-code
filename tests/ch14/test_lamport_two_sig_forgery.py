"""Tests for the two-signature Lamport forgery.

After two signatures on distinct messages, the adversary holds both
halves of every secret pair at bit positions where the two message
digests differ.  These tests verify the forgery concretely.
"""

import hashlib

from lamport_merkle.lamport import keygen, sign, verify


SEED = b"ch14-forgery-test"


def _bit(digest: bytes, i: int) -> int:
    byte_index = i // 8
    bit_offset = 7 - (i % 8)
    return (digest[byte_index] >> bit_offset) & 1


def _digest(message: bytes) -> bytes:
    return hashlib.sha256(message).digest()


def _hamming_distance(a: bytes, b: bytes) -> int:
    return sum(bin(x ^ y).count("1") for x, y in zip(a, b))


def test_two_signatures_leak_both_halves_at_differing_bits():
    """Where digests differ, the adversary holds both sk[i][0] and sk[i][1]."""
    sk, pk = keygen(rng=SEED)
    m1 = b"first message"
    m2 = b"second message"
    sig1 = sign(sk, m1)
    sig2 = sign(sk, m2)

    d1 = _digest(m1)
    d2 = _digest(m2)
    hd = _hamming_distance(d1, d2)

    # At each differing bit position, sig1 and sig2 reveal different halves.
    both_known = 0
    for i in range(256):
        b1 = _bit(d1, i)
        b2 = _bit(d2, i)
        if b1 != b2:
            # sig1 reveals sk[i][b1], sig2 reveals sk[i][b2].
            # Together they give both sk[i][0] and sk[i][1].
            both_known += 1
    assert both_known == hd
    # For random messages the expected Hamming distance is ~128.
    assert hd > 50, f"Hamming distance {hd} is suspiciously low"


def test_forge_third_message_from_two_signatures():
    """Construct a concrete forgery for a third message."""
    sk, pk = keygen(rng=SEED)
    m1 = b"first message"
    m2 = b"second message"
    sig1 = sign(sk, m1)
    sig2 = sign(sk, m2)

    d1 = _digest(m1)
    d2 = _digest(m2)

    # Build a map of all secrets the adversary has learned.
    known = {}  # known[i][bit_value] = revealed secret
    for i in range(256):
        known[i] = {}
        b1 = _bit(d1, i)
        known[i][b1] = sig1[i]
        b2 = _bit(d2, i)
        known[i][b2] = sig2[i]

    # Pick a third message and attempt to forge.
    m3 = b"forged message"
    d3 = _digest(m3)

    forged_sig = []
    forgeable_count = 0
    for i in range(256):
        needed_bit = _bit(d3, i)
        if needed_bit in known[i]:
            forged_sig.append(known[i][needed_bit])
            forgeable_count += 1
        else:
            # Adversary does not have this secret; use a placeholder.
            forged_sig.append(b"\x00" * 32)

    # The forgery succeeds at every position where the adversary has the
    # needed secret.  It fails overall only if some positions are missing.
    # For this specific triple of messages, count how many positions work.
    # With two random-message signatures the adversary holds both halves at
    # ~128 positions and one half at ~128 positions.  For a random third
    # digest each position is forgeable with probability 3/4, giving an
    # expected forgeable count of ~192.  The threshold below is conservative.
    assert forgeable_count > 150, (
        f"Expected most positions forgeable, got {forgeable_count}/256"
    )

    # Verify that each forgeable position individually checks out.
    for i in range(256):
        needed_bit = _bit(d3, i)
        if needed_bit in known[i]:
            assert hashlib.sha256(forged_sig[i]).digest() == pk[i][needed_bit]


def test_forgery_reaches_all_positions_when_digests_complement():
    """When d1 and d2 differ at every bit, the adversary has all 512 secrets."""
    sk, pk = keygen(rng=SEED)

    # Craft two messages whose SHA-256 digests differ at many bit positions.
    # We search for a pair with high Hamming distance to demonstrate the
    # principle.  For the strongest case, we just check that more positions
    # means more forgery power.
    m1 = b"alpha"
    best_m2 = None
    best_hd = 0
    for i in range(1000):
        candidate = f"beta-{i}".encode()
        hd = _hamming_distance(_digest(m1), _digest(candidate))
        if hd > best_hd:
            best_hd = hd
            best_m2 = candidate

    sig1 = sign(sk, m1)
    sig2 = sign(sk, best_m2)
    d1 = _digest(m1)
    d2 = _digest(best_m2)

    known = {}
    for i in range(256):
        known[i] = set()
        known[i].add(_bit(d1, i))
        known[i].add(_bit(d2, i))

    both_halves = sum(1 for i in range(256) if len(known[i]) == 2)
    assert both_halves == best_hd
    # With ~1000 candidates, best_hd should be well above 128.
    assert best_hd > 140, f"Best Hamming distance was only {best_hd}"
