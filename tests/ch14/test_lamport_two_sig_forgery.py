"""Tests for the exposure two Lamport signatures create.

After two signatures on distinct messages, the adversary holds both
halves of every secret pair at bit positions where the two message
digests differ.  These tests measure that exposure and show how far it
gets an attacker on a third message.  They do not exhibit a valid
forgery: against SHA-256 the fixed triple below leaves 65 of the 256
positions unsupplied, and the assembled signature is rejected.  A
completed forgery would need a reduced digest space, a message chosen
for the secrets already held, or a third signature.
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
    # Count only the positions where the revealed values are the real
    # secrets, checked against the published hashes. Counting differing
    # digest bits alone would restate the Hamming distance and would pass
    # against a signer that returned 256 zero strings.
    both_known = 0
    for i in range(256):
        b1 = _bit(d1, i)
        b2 = _bit(d2, i)
        if b1 == b2:
            continue
        assert hashlib.sha256(sig1[i]).digest() == pk[i][b1]
        assert hashlib.sha256(sig2[i]).digest() == pk[i][b2]
        assert sig1[i] != sig2[i], (
            f"position {i} has differing digest bits and must reveal two "
            "different secrets"
        )
        both_known += 1
    assert both_known == hd
    # For random messages the expected Hamming distance is ~128.
    assert hd > 50, f"Hamming distance {hd} is suspiciously low"


def test_third_message_attempt_falls_short_of_a_valid_signature():
    """Two signatures supply most positions of a third, and not all of them.

    This is the honest shape of the two-signature attack at a 256-bit
    digest: each position is forgeable with probability 3/4, so the
    adversary assembles ~192 of 256 valid preimages and has nothing for
    the rest.  Every position it does supply checks out against the
    public key, and the whole signature is still rejected, which is the
    assertion at the end.  The danger the chapter describes is the size
    of the forgeable message set, not this particular message.
    """
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

    # With two random-message signatures the adversary holds both halves at
    # ~128 positions and one half at ~128 positions.  For a random third
    # digest each position is forgeable with probability 3/4, giving an
    # expected forgeable count of ~192.  The threshold below is conservative.
    assert forgeable_count > 150, (
        f"Expected most positions forgeable, got {forgeable_count}/256"
    )
    assert forgeable_count < 256, (
        "this fixed triple is meant to leave positions unsupplied; a run "
        "where every position is forgeable would need a different assertion"
    )

    # Every position the adversary can supply checks out against the public
    # key.  That is the exposure, and it is not a signature.
    for i in range(256):
        needed_bit = _bit(d3, i)
        if needed_bit in known[i]:
            assert hashlib.sha256(forged_sig[i]).digest() == pk[i][needed_bit]

    # The whole thing is rejected, because the placeholders at the
    # unsupplied positions are not preimages of anything in the public key.
    assert verify(pk, m3, forged_sig) is False, (
        "a signature with placeholder positions must not verify"
    )


def test_two_signatures_expose_one_secret_pair_per_differing_bit():
    """Exposure counts differing digest bits, one double-known slot each.

    The limiting case, two digests differing at all 256 bits, would hand the
    adversary all 512 secrets. This test does not reach it and does not claim
    to: finding a SHA-256 preimage pair with complementary digests is the
    infeasible search, not a fixture. What it measures is the relation that
    holds at every distance, that the number of positions where the adversary
    now holds both halves of the one-time secret equals the Hamming distance
    between the two digests, over the highest-distance pair a small search
    finds. Each half is counted only after it is checked against the
    published hash, so the count is exposure and not a restatement of the
    distance.
    """
    sk, pk = keygen(rng=SEED)

    # Search a small candidate pool for a pair with high Hamming distance.
    # The distance is what the assertion below is about; the pool size only
    # decides how far above 128 the sampled distance lands.
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

    # Build the adversary's map out of the signatures, and keep a value only
    # once it is checked against the public key. A map keyed on digest bits
    # alone would count the same thing the Hamming distance already counts.
    known: dict[int, dict[int, bytes]] = {}
    for i in range(256):
        known[i] = {}
        for sig, digest in ((sig1, d1), (sig2, d2)):
            bit = _bit(digest, i)
            assert hashlib.sha256(sig[i]).digest() == pk[i][bit]
            known[i][bit] = sig[i]

    both_halves = sum(1 for i in range(256) if len(known[i]) == 2)
    assert both_halves == best_hd
    # ~1000 candidates put the best distance well above the 128 mean, which is
    # what makes the equality above a non-trivial sample rather than a
    # coincidence at the centre of the distribution. It is not 256.
    assert 140 < best_hd < 256, f"Best Hamming distance was {best_hd}"
