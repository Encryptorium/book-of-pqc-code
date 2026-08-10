"""WOTS+ one-time signature scheme.

Implements base-w encoding, checksum computation, hash-chain keygen,
signing, and verification.  The chain function uses a simplified domain
separation (pk_seed || chain_index || step_index || value) rather than the
full ADRS structure of RFC 8391.

Seed usage follows RFC 8391 §3.1.7 / FIPS 205 Algorithm 6: the secret key
is derived from a private sk_seed (never revealed); the chain function uses
a public pk_seed that domain-separates hashing and is safe to publish along
with the public key.  These two seeds must be kept distinct.
"""

import hashlib
import math


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


# ── Base-w encoding ──────────────────────────────────────────────────

def base_w(data: bytes, w: int, out_len: int) -> list[int]:
    """Encode *data* as a list of *out_len* base-*w* digits.

    *w* must be a power of two.  Digits are extracted MSB-first within
    each byte, matching the convention in RFC 8391 Section 2.6.
    """
    assert w >= 2 and (w & (w - 1)) == 0, f"w must be a power of two, got {w}"
    lg_w = int(math.log2(w))
    digits: list[int] = []
    for byte in data:
        for shift in range(8 - lg_w, -1, -lg_w):
            digits.append((byte >> shift) & (w - 1))
            if len(digits) == out_len:
                return digits
    return digits[:out_len]


# ── Checksum ─────────────────────────────────────────────────────────

def _ell_params(n: int, w: int) -> tuple[int, int, int]:
    """Return (ell_1, ell_2, ell) for hash output *n* bytes, base *w*."""
    assert w >= 2 and (w & (w - 1)) == 0, f"w must be a power of two, got {w}"
    lg_w = int(math.log2(w))
    ell_1 = math.ceil(8 * n / lg_w)
    max_checksum = ell_1 * (w - 1)
    ell_2 = math.ceil((math.floor(math.log2(max_checksum)) + 1) / lg_w)
    return ell_1, ell_2, ell_1 + ell_2


def checksum(msg_digits: list[int], w: int) -> list[int]:
    """Compute the WOTS+ checksum over *msg_digits* and encode in base *w*.

    The checksum is ``sum(w - 1 - d for d in msg_digits)``, encoded as
    ``ell_2`` base-*w* digits (big-endian byte order).
    """
    # EXERCISE: implement this function.
    #
    # Sum w - 1 - d over the message digits. That total falls by exactly
    # delta whenever any message digit rises by delta, which is the whole
    # point of the checksum. Then encode it as ell_2 base-w digits, where
    # ell_2 = ceil((floor(log2(len(msg_digits) * (w - 1))) + 1) / lg_w). The
    # encoding needs one wrinkle: base_w reads from the most significant
    # end, so left-shift the sum by 8 * ceil(ell_2 * lg_w / 8) - ell_2 *
    # lg_w bits before calling to_bytes, otherwise the low digits fall off
    # the end of the byte array. At w = 16 and 64 message digits, ell_2 is 3
    # and the shift is 4 bits.
    #
    # Reference: Chapter 15, 'The checksum' (RFC 8391 Section 3.1.5, Algorithm 5)
    #
    # Proved by:
    #   tests/ch15/test_wots_checksum_forgery.py
    #   tests/ch15/test_wots_sign_verify.py
    raise NotImplementedError("exercise: checksum")


# ── Chain function ───────────────────────────────────────────────────

def chain(x: bytes, start: int, steps: int, pk_seed: bytes, addr: int) -> bytes:
    """Iterate the chain function *steps* times from position *start*.

    Each step hashes ``pk_seed || addr (4 bytes) || step_index (4 bytes) || x``
    where *step_index* counts from *start* upward.  *pk_seed* is the public
    chain-domain seed (safe to publish; it is the verifier's domain separator).
    """
    value = x
    for i in range(start, start + steps):
        value = _sha256(
            pk_seed + addr.to_bytes(4, "big") + i.to_bytes(4, "big") + value
        )
    return value


# ── WOTS+ keygen / sign / verify ─────────────────────────────────────

def wots_keygen(
    sk_seed: bytes, pk_seed: bytes, w: int = 16, n: int = 32
) -> tuple[list[bytes], list[bytes]]:
    """Generate a WOTS+ keypair.

    Parameters
    ----------
    sk_seed : bytes
        Private seed used to derive the *ell* secret key values via PRF.
        Must be kept secret; never included in the public key or signature.
    pk_seed : bytes
        Public seed that domain-separates the chain function (RFC 8391
        §3.1.7 / FIPS 205 Algorithm 6).  The verifier needs this value;
        it is safe to publish alongside the public key.
    w : int
        Winternitz parameter.
    n : int
        Hash output length in bytes.

    Returns
    -------
    sk : list[bytes]
        *ell* PRF-derived *n*-byte secret values.
    pk : list[bytes]
        *ell* chain endpoints (each secret hashed ``w - 1`` times with pk_seed).
    """
    ell_1, ell_2, ell = _ell_params(n, w)
    sk: list[bytes] = []
    for i in range(ell):
        sk.append(_sha256(sk_seed + b"sk" + i.to_bytes(4, "big")))

    pk = [chain(sk[i], 0, w - 1, pk_seed, i) for i in range(ell)]
    return sk, pk


def wots_sign(
    sk: list[bytes],
    message: bytes,
    pk_seed: bytes,
    w: int = 16,
    n: int = 32,
) -> list[bytes]:
    """Sign *message* under the WOTS+ secret key *sk*.

    *pk_seed* is the public chain-domain seed; the secret values are
    already embedded in *sk*.

    Returns *ell* chain values, one per digit of the encoded message
    plus checksum.
    """
    ell_1, ell_2, ell = _ell_params(n, w)
    digest = _sha256(message)
    msg_digits = base_w(digest, w, ell_1)
    csum_digits = checksum(msg_digits, w)
    digits = msg_digits + csum_digits

    sig = [chain(sk[i], 0, digits[i], pk_seed, i) for i in range(ell)]
    return sig


def wots_verify(
    pk: list[bytes],
    message: bytes,
    sig: list[bytes],
    pk_seed: bytes,
    w: int = 16,
    n: int = 32,
) -> bool:
    """Verify a WOTS+ signature.

    For each digit *d_i*, hash the signature value forward ``w - 1 - d_i``
    steps and compare against the public-key endpoint.  *pk_seed* is the
    public chain-domain seed.
    """
    ell_1, ell_2, ell = _ell_params(n, w)
    if len(sig) != ell:
        return False

    digest = _sha256(message)
    msg_digits = base_w(digest, w, ell_1)
    csum_digits = checksum(msg_digits, w)
    digits = msg_digits + csum_digits

    for i in range(ell):
        if chain(sig[i], digits[i], w - 1 - digits[i], pk_seed, i) != pk[i]:
            return False
    return True


# ── Checksum-bypass helpers (for the forgery demonstration) ──────────

def wots_sign_no_checksum(
    sk: list[bytes],
    message: bytes,
    pk_seed: bytes,
    w: int = 16,
    n: int = 32,
) -> list[bytes]:
    """Sign using only message digits (no checksum).

    This produces a short signature of *ell_1* chain values.  Without the
    checksum, the signature is vulnerable to forgery by digit increase.
    *pk_seed* is the public chain-domain seed.
    """
    # EXERCISE: implement this function.
    #
    # The deliberately broken variant used by the forgery demonstration.
    # Sign exactly as wots_sign does but stop at the ell_1 message digits:
    # no checksum digits, no checksum chains, so the result is ell_1 values
    # rather than ell. This is the scheme in which an adversary holding the
    # value at position d can hash forward to position d + 1 and forge on
    # any digest whose digits are componentwise larger.
    #
    # Reference: Chapter 15, 'The checksum-bypass forgery'
    #
    # Proved by:
    #   tests/ch15/test_wots_checksum_forgery.py
    raise NotImplementedError("exercise: wots_sign_no_checksum")


def wots_verify_no_checksum(
    pk: list[bytes],
    message: bytes,
    sig: list[bytes],
    pk_seed: bytes,
    w: int = 16,
    n: int = 32,
) -> bool:
    """Verify using only message digits (no checksum).

    *pk* must be the first *ell_1* entries of the full public key.
    *pk_seed* is the public chain-domain seed.
    """
    # EXERCISE: implement this function.
    #
    # The matching verifier for wots_sign_no_checksum: reject a signature
    # that is not ell_1 long, then chain each of the ell_1 values forward w
    # - 1 - d steps against the first ell_1 public-key entries. The caller
    # passes that truncated public key. Nothing here detects the
    # forward-hashed forgery, which is the point: only the checksum chains
    # can, because raising a message digit lowers the checksum and no one
    # can walk a chain backward.
    #
    # Reference: Chapter 15, 'The checksum-bypass forgery'
    #
    # Proved by:
    #   tests/ch15/test_wots_checksum_forgery.py
    raise NotImplementedError("exercise: wots_verify_no_checksum")
