"""Compression and decompression for ML-KEM ciphertexts (FIPS 203 §4.2).

The compression map $\\text{Compress}_d(x)$ rounds $x \\in \\mathbb{Z}_q$
to the nearest integer multiple of $q / 2^d$ and returns that
multiple's index in $\\{0, 1, \\dots, 2^d - 1\\}$:

.. math::

    \\text{Compress}_d(x)
    = \\left\\lfloor \\frac{2^d \\cdot x}{q} \\right\\rceil \\bmod 2^d,

where $\\lfloor \\cdot \\rceil$ is round-half-up to the nearest integer.
The inverse $\\text{Decompress}_d(y)$ takes $y \\in \\mathbb{Z}_{2^d}$
and returns $\\lfloor q \\cdot y / 2^d \\rceil$, again rounding half up.
FIPS 203 (4.7) and (4.8) carry the width as the only subscript; the
Python functions below take it as a second argument instead.

Compression is lossy. The decompression noise is bounded by
$|\\text{Decompress}_d(\\text{Compress}_d(x)) - x| \\leq
\\lceil q / 2^{d+1} \\rceil$, which at $(q, d) = (3329, 10)$ gives a
bound of $2$ and at $(q, d) = (3329, 4)$ gives a bound of $105$. The
bound is attained at $d = 10$ and is one high at $d = 4$, where the
true maximum is $104$. These bounds feed directly into the K-PKE
noise budget.

Integer-arithmetic formulae, no floating point. For odd $q = 3329$
the round-half-up step is computed exactly via
$\\lfloor (2^d x + \\lfloor q/2 \\rfloor) / q \\rfloor$ because any
residue strictly above $(q-1)/2$ rounds up.
"""

from __future__ import annotations

import numpy as np

from .ntt import Q, N


def compress(x: np.ndarray, d: int) -> np.ndarray:
    """Apply $\\text{Compress}_q(\\cdot, d)$ coefficient-wise.

    Accepts a numpy array with integer entries in $[0, q)$ and returns
    an int64 numpy array of the same shape with entries in
    $[0, 2^d)$. Raises if $d \\leq 0$ or $d \\geq 12$.
    """
    # EXERCISE: implement this function.
    #
    # Reject d outside [1, 11], then reduce the input modulo q as int64 and
    # apply the round-half-up formula ((x * 2^d) + q // 2) // q, taken
    # modulo 2^d. Adding q // 2 before the floor division is exactly what
    # makes any residue strictly above (q - 1) / 2 round up, so odd q needs
    # no floating point at all. The map is coefficient-wise, so it must work
    # on a whole array.
    #
    # Reference: Chapter 11, 'The ML-KEM math preliminaries' (FIPS 203 §4.2)
    #
    # Proved by:
    #   tests/ch11/test_compression.py
    #   tests/ch11/test_serialize_poly.py
    raise NotImplementedError("exercise: compress")


def decompress(y: np.ndarray, d: int) -> np.ndarray:
    """Apply $\\text{Decompress}_q(\\cdot, d)$ coefficient-wise.

    Accepts a numpy array with integer entries in $[0, 2^d)$ and
    returns an int64 numpy array of the same shape with entries in
    $[0, q)$.
    """
    # EXERCISE: implement this function.
    #
    # Reject d outside [1, 11], then return ((q * y) + 2^(d-1)) // 2^d as
    # int64, the round-half-up inverse of compress. No final reduction
    # modulo q is needed: the output is already below q for every y below
    # 2^d. At d = 1 this sends 1 to 1665 and 0 to 0.
    #
    # Reference: Chapter 11, 'The ML-KEM math preliminaries' (FIPS 203 §4.2)
    #
    # Proved by:
    #   tests/ch11/test_compression.py
    raise NotImplementedError("exercise: decompress")


def compression_noise_bound(d: int) -> int:
    """Return the decompression noise bound $\\lceil q / 2^{d+1} \\rceil$.

    This is the maximum absolute value (in symmetric representatives)
    of $\\text{Decompress}_q(\\text{Compress}_q(x, d), d) - x$ across
    all $x \\in \\mathbb{Z}_q$. The K-PKE noise budget has to cover
    this on top of the Module-LWE error.
    """
    # EXERCISE: implement this function.
    #
    # Return the ceiling of q / 2^(d+1), computed as (q + 2^(d+1) - 1) //
    # 2^(d+1) so it stays integer arithmetic. Compress rounds to the nearest
    # multiple of q / 2^d, so one round trip can move a value by at most
    # half that spacing. At q = 3329 the answers are 833 at d = 1, 105 at d
    # = 4, 2 at d = 10, and 1 at d = 11.
    #
    # Reference: Chapter 11, 'The ML-KEM math preliminaries' (FIPS 203 §4.2)
    #
    # Proved by:
    #   tests/ch11/test_compression.py
    raise NotImplementedError("exercise: compression_noise_bound")


def message_to_poly(message: bytes) -> np.ndarray:
    """Encode a 32-byte message as a polynomial with coefficients in
    $\\{0, \\lceil q/2 \\rceil\\}$.

    FIPS 203 uses ``Decompress_q(ByteDecode_1(m), 1)`` to lift a
    256-bit message into $R_q$, which is the same operation: each
    message bit $b$ becomes the coefficient
    $\\text{Decompress}_q(b, 1) = \\lfloor (q + 1) / 2 \\rfloor \\cdot b
    = 1665 \\cdot b$ at $q = 3329$.
    """
    # EXERCISE: implement this function.
    #
    # Assert the message is 32 bytes, then read its 256 bits with the low
    # bit of each byte first: bit i is (message[i >> 3] >> (i & 7)) & 1.
    # Coefficient i is that bit times (q + 1) // 2, which is 1665 at q =
    # 3329. This is FIPS 203's Decompress_1(ByteDecode_1(m)); the encoded
    # one is 1665 rather than 1664 because round-half-up at the midpoint q /
    # 2 = 1664.5 goes up.
    #
    # Reference: Chapter 11, 'The ML-KEM math preliminaries' (FIPS 203 §4.2)
    #
    # Proved by:
    #   tests/ch11/test_compression.py
    raise NotImplementedError("exercise: message_to_poly")


def poly_to_message(f: np.ndarray) -> bytes:
    """Decode a polynomial back to a 32-byte message.

    Applies $\\text{Compress}_q(\\cdot, 1)$ coefficient-wise, then packs
    the 256 resulting bits little-endian into 32 bytes. This is the
    inverse of ``message_to_poly`` when the noise stays inside the
    decoding region around $0$ and $\\lfloor q/2 \\rfloor$.
    """
    # EXERCISE: implement this function.
    #
    # Reduce the polynomial modulo q, assert it has 256 coefficients, and
    # run compress at d = 1 over it. Each resulting bit is 1 when the
    # coefficient sits nearer to 1665 than to 0 on the cycle. Pack the 256
    # bits into 32 bytes in the same order message_to_poly reads them, low
    # bit of each byte first.
    #
    # Reference: Chapter 11, 'K-PKE.Decrypt' (FIPS 203 §5.3)
    #
    # Proved by:
    #   tests/ch11/test_compression.py
    raise NotImplementedError("exercise: poly_to_message")
