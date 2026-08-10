"""Tests demonstrating the checksum-bypass forgery.

Test 1: without the checksum, an adversary who sees a signature can
forge by hashing chain values forward (increasing digit values).

Test 2: with the checksum, the same attack fails because increasing a
message digit forces a decrease in a checksum digit, which requires
inverting the hash function.
"""

import hashlib

from wots_xmss.wots import (
    _ell_params,
    base_w,
    chain,
    checksum,
    wots_keygen,
    wots_sign,
    wots_sign_no_checksum,
    wots_verify,
    wots_verify_no_checksum,
)


SK_SEED = b"checksum-forgery-demo-sk"
PK_SEED = b"checksum-forgery-demo-pk"
W = 16
N = 32


def test_forgery_succeeds_without_checksum():
    """Without the checksum, an adversary can forge by hashing forward.

    The adversary sees a signature where digit d[i] < w-1 at some
    position i.  By hashing sig[i] forward one step, the adversary
    obtains the chain value for digit d[i]+1.  This forged value
    verifies against the no-checksum scheme.
    """
    sk, pk = wots_keygen(SK_SEED, PK_SEED, w=W, n=N)
    message = b"original message"
    sig_nc = wots_sign_no_checksum(sk, message, PK_SEED, w=W, n=N)
    pk_nc = pk[:len(sig_nc)]

    # Find a position where the digit is < w-1 (almost certainly exists).
    digest = hashlib.sha256(message).digest()
    ell_1 = len(sig_nc)
    msg_digits = base_w(digest, W, ell_1)

    forge_pos = None
    for i, d in enumerate(msg_digits):
        if d < W - 1:
            forge_pos = i
            break
    assert forge_pos is not None, "no forgeable position found"

    original_digit = msg_digits[forge_pos]

    # Forge: hash forward one step from the signature value.
    forged_value = chain(
        sig_nc[forge_pos], original_digit, 1, PK_SEED, forge_pos
    )

    # Build a forged message whose digit at forge_pos is original_digit + 1.
    # Instead of finding such a message, verify directly that the forged
    # chain value matches the chain endpoint for digit original_digit + 1.
    expected = chain(sk[forge_pos], 0, original_digit + 1, PK_SEED, forge_pos)
    assert forged_value == expected, "forged chain value should match"

    # Verify forward to the public key endpoint: the forged value
    # should hash forward w-1-(original_digit+1) steps to pk[forge_pos].
    recomputed = chain(
        forged_value,
        original_digit + 1,
        W - 1 - (original_digit + 1),
        PK_SEED,
        forge_pos,
    )
    assert recomputed == pk_nc[forge_pos], "forged value reaches the pk endpoint"


def test_forgery_fails_with_checksum():
    """With the checksum, increasing a message digit forces a checksum
    digit to decrease.  The adversary cannot hash backward on the
    checksum chains, so the forged signature fails verification against
    a message whose digits actually require the increased value.

    The adversary's strategy: take the original signature, hash forward
    on one message chain (increasing that digit), and keep the checksum
    chains unchanged.  Then verify against a message whose digest has
    the increased digit at that position.  The checksum for the new
    message is lower than the original, so at least one checksum chain
    position must decrease.  The adversary cannot produce that lower
    chain value, and verification fails.
    """
    sk, pk = wots_keygen(SK_SEED, PK_SEED, w=W, n=N)
    message = b"original message"
    sig = wots_sign(sk, message, PK_SEED, w=W, n=N)

    # Compute the digits for the original message.
    digest = hashlib.sha256(message).digest()
    ell_1, ell_2, ell = _ell_params(N, W)
    msg_digits = base_w(digest, W, ell_1)
    csum_digits_orig = checksum(msg_digits, W)
    all_digits = msg_digits + csum_digits_orig

    # Find a position where the digit is < W - 1.
    forge_pos = None
    for i, d in enumerate(msg_digits):
        if d < W - 1:
            forge_pos = i
            break
    assert forge_pos is not None

    # Build a modified message digit array with one digit increased.
    forged_msg_digits = list(msg_digits)
    forged_msg_digits[forge_pos] += 1
    forged_csum_digits = checksum(forged_msg_digits, W)

    # The checksum decreased: at least one checksum digit is now lower.
    forged_csum_val = sum(W - 1 - d for d in forged_msg_digits)
    orig_csum_val = sum(W - 1 - d for d in msg_digits)
    assert forged_csum_val == orig_csum_val - 1

    # The adversary can hash forward on the message chain at forge_pos.
    forged_sig = list(sig)
    forged_sig[forge_pos] = chain(
        sig[forge_pos], all_digits[forge_pos], 1, PK_SEED, forge_pos
    )
    # But the adversary keeps the original checksum chain values unchanged
    # (cannot hash backward to produce the lower checksum positions).

    # Build a fake message that would produce forged_msg_digits.
    # We cannot easily find such a message, so instead we directly
    # verify that the forged signature fails when the verifier computes
    # the correct (lower) checksum digits for forged_msg_digits.
    # The verifier would compute forged_csum_digits for the new message
    # and try to chain the checksum sig values forward by (w-1-d') steps.
    # Since the original checksum digit was higher (d_orig) and the new
    # one is lower (d_new < d_orig), the adversary's chain value is at
    # position d_orig, and the verifier chains forward w-1-d_new steps,
    # overshooting the public key endpoint.
    forged_all_digits = forged_msg_digits + forged_csum_digits

    # Manually verify: for message chains, the forged value at forge_pos
    # should work (adversary hashed forward correctly).
    msg_chain_ok = chain(
        forged_sig[forge_pos],
        forged_all_digits[forge_pos],
        W - 1 - forged_all_digits[forge_pos],
        PK_SEED,
        forge_pos,
    ) == pk[forge_pos]
    assert msg_chain_ok, "message chain forgery should succeed"

    # For checksum chains, at least one chain fails because the adversary
    # holds a value at position d_orig but needs position d_new < d_orig.
    csum_chain_failures = 0
    for j in range(ell_1, ell):
        recomputed = chain(
            forged_sig[j],  # original sig value at checksum position
            forged_all_digits[j],  # new (lower) digit
            W - 1 - forged_all_digits[j],
            PK_SEED,
            j,
        )
        if recomputed != pk[j]:
            csum_chain_failures += 1
    assert csum_chain_failures > 0, "at least one checksum chain must fail"


def test_checksum_decreases_on_digit_increase():
    """Increasing a message digit by delta decreases the checksum by delta."""
    msg_digits = [7, 3, 15, 0, 10]
    c1 = sum(W - 1 - d for d in msg_digits)

    # Increase digit 1 from 3 to 5 (delta = 2).
    modified = list(msg_digits)
    modified[1] = 5
    c2 = sum(W - 1 - d for d in modified)

    assert c2 == c1 - 2
