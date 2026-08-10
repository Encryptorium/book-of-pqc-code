"""Lamport one-time signature scheme.

Keygen produces 2n random 32-byte secrets and their SHA-256 hashes.
Signing reveals one secret per message-digest bit.  Verification
re-hashes each revealed secret and compares against the public key.
"""

import hashlib
import os


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _message_digest(message: bytes) -> bytes:
    return _sha256(message)


def _bit(digest: bytes, i: int) -> int:
    """Return bit *i* of *digest* (MSB-first within each byte)."""
    byte_index = i // 8
    bit_offset = 7 - (i % 8)
    return (digest[byte_index] >> bit_offset) & 1


def keygen(n: int = 256, rng: bytes | None = None):
    """Generate a Lamport keypair.

    Parameters
    ----------
    n : int
        Number of bit positions (must equal the hash output length in bits).
    rng : bytes or None
        If provided, used as a deterministic seed via a counter-mode
        expansion.  If *None*, ``os.urandom`` supplies the randomness.

    Returns
    -------
    sk : list[tuple[bytes, bytes]]
        Secret key: *n* pairs of 32-byte random strings.
    pk : list[tuple[bytes, bytes]]
        Public key: *n* pairs of SHA-256 digests of the corresponding
        secret-key halves.
    """
    if rng is not None:
        # Deterministic expansion for reproducible tests.
        raw = bytearray()
        for counter in range(2 * n):
            raw.extend(
                hashlib.sha256(rng + counter.to_bytes(4, "big")).digest()
            )
        secrets = [bytes(raw[i * 32 : (i + 1) * 32]) for i in range(2 * n)]
    else:
        secrets = [os.urandom(32) for _ in range(2 * n)]

    sk = [(secrets[2 * i], secrets[2 * i + 1]) for i in range(n)]
    pk = [(_sha256(s0), _sha256(s1)) for s0, s1 in sk]
    return sk, pk


def sign(sk, message: bytes) -> list[bytes]:
    """Sign *message* under the Lamport secret key *sk*.

    Returns a list of *n* revealed secrets, one per digest bit.
    """
    n = len(sk)
    digest = _message_digest(message)
    return [sk[i][_bit(digest, i)] for i in range(n)]


def verify(pk, message: bytes, sig: list[bytes]) -> bool:
    """Verify a Lamport signature.

    Returns *True* iff every revealed secret hashes to the correct
    public-key slot for the corresponding message-digest bit.
    """
    n = len(pk)
    if len(sig) != n:
        return False
    digest = _message_digest(message)
    for i in range(n):
        if _sha256(sig[i]) != pk[i][_bit(digest, i)]:
            return False
    return True
