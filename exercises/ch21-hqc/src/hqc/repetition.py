"""Repetition code: encode and decode via majority vote.

Each message bit is repeated *r* times.  The codeword is zero-padded to
length *n*.  Decoding uses majority vote per block of *r* bits.
"""


def rep_encode(message: list[int], r: int, n: int) -> list[int]:
    """Encode *message* by repeating each bit *r* times, pad to length *n*."""
    codeword = []
    for bit in message:
        codeword.extend([bit] * r)
    # Zero-pad to length n
    codeword.extend([0] * (n - len(codeword)))
    return codeword


def rep_decode(received: list[int], r: int, n: int) -> list[int]:
    """Decode by majority vote on each block of *r* consecutive bits."""
    k = n // r
    message = []
    for i in range(k):
        block = received[i * r : (i + 1) * r]
        ones = sum(block)
        message.append(1 if ones > r // 2 else 0)
    return message
