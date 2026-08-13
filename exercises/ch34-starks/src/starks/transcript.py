"""Fiat-Shamir transcript for Chapter 34.

A ``Transcript`` accumulates prover-verifier messages into a running
SHA-256 state. Verifier challenges are derived by squeezing fresh bytes
from the state under a label plus a counter, so identical absorb
sequences produce identical challenge sequences on both sides. The
pattern mirrors Chapter 33's ``RandomOracle`` but is re-declared here
without a Chapter 33 import, so Chapter 34 remains self-contained.

Transcript discipline
---------------------

- ``absorb(label, data)`` mixes ``label || len(data) || data`` into the
  state. The label enforces domain separation between transcript
  positions and prevents a prover from shadowing one message with
  another.
- ``absorb_int(label, value, num_bytes)`` is a convenience for
  absorbing a non-negative integer of bounded size. The width is fixed
  per call to avoid the standard prefix-ambiguity pitfall.
- ``squeeze_int(label, modulus)`` returns a pseudo-uniform integer in
  ``[0, modulus)`` by hashing the current state together with a
  per-call counter.
- ``squeeze_index(label, domain_size)`` is the same mechanic, but the
  caller names the semantics explicitly to keep query indexing separate
  from challenge drawing in the prover and verifier code paths.

The transcript raises ``ValueError`` eagerly on invalid input. It never
swallows errors. The domain-separation string at construction time
guards against cross-protocol replay.
"""

from __future__ import annotations

import hashlib


class Transcript:
    """SHA-256-based Fiat-Shamir transcript.

    The internal state is the running SHA-256 digest of every absorb
    plus every squeeze produced so far. Each squeeze hashes the state
    with a fresh counter and returns the result in the requested range;
    the squeezed bytes are then absorbed back into the state so that
    subsequent squeezes are deterministic functions of the full
    history.
    """

    def __init__(self, domain_sep: bytes = b"ch34-stark") -> None:
        if not isinstance(domain_sep, (bytes, bytearray)):
            raise ValueError("domain_sep must be bytes")
        self._state = hashlib.sha256(b"ch34-transcript-v1|" + bytes(domain_sep)).digest()
        self._squeeze_counter = 0

    def absorb(self, label: bytes, data: bytes) -> None:
        """Mix ``label || len(data) || data`` into the transcript state."""
        if not isinstance(label, (bytes, bytearray)):
            raise ValueError("label must be bytes")
        if not isinstance(data, (bytes, bytearray)):
            raise ValueError("data must be bytes")
        length = len(data).to_bytes(8, "big")
        self._state = hashlib.sha256(
            self._state + bytes(label) + length + bytes(data)
        ).digest()

    def absorb_int(self, label: bytes, value: int, num_bytes: int = 8) -> None:
        """Absorb a non-negative integer with fixed byte width."""
        if num_bytes < 1:
            raise ValueError("num_bytes must be at least one")
        if value < 0:
            raise ValueError("value must be non-negative")
        if value >= 256 ** num_bytes:
            raise ValueError("value exceeds num_bytes capacity")
        self.absorb(label, value.to_bytes(num_bytes, "big"))

    def _squeeze_bytes(self, label: bytes, num_bytes: int) -> bytes:
        """Squeeze ``num_bytes`` bytes under ``label`` and absorb back."""
        # EXERCISE: implement this function.
        #
        # Take the current squeeze counter as 8 big-endian bytes and
        # increment it, then produce output by hashing the state together
        # with the label, that counter, and a per-block index, concatenating
        # digests until at least num_bytes are available. Fold the whole
        # produced string back into the state with one further hash, so the
        # next squeeze depends on every byte this one emitted, and return
        # the first num_bytes. That fold-back is what makes two squeezes
        # under the same label give different answers. Reject a non-bytes
        # label and a num_bytes below one.
        #
        # Reference: Chapter 34, '4.3 FRI with Fiat-Shamir challenges' (Block 4)
        #
        # Proved by:
        #   tests/ch34/test_transcript.py
        raise NotImplementedError("exercise: Transcript._squeeze_bytes")

    def squeeze_int(self, label: bytes, modulus: int) -> int:
        """Return a pseudo-uniform integer in ``[0, modulus)``."""
        # EXERCISE: implement this function.
        #
        # Squeeze bytes under the label and reduce them modulo modulus. Draw
        # eight bytes more than the modulus's own width needs, which pushes
        # the modular bias well below 2^-64; a deployment transcript
        # rejection-samples instead, but at the toy's parameter sizes the
        # two are indistinguishable. Reject a modulus below one.
        #
        # Reference: Chapter 34, '4.3 FRI with Fiat-Shamir challenges' (Block 4)
        #
        # Proved by:
        #   tests/ch34/test_transcript.py
        raise NotImplementedError("exercise: Transcript.squeeze_int")

    def squeeze_index(self, label: bytes, domain_size: int) -> int:
        """Return a pseudo-uniform index in ``[0, domain_size)``."""
        if domain_size < 1:
            raise ValueError("domain_size must be positive")
        return self.squeeze_int(label, domain_size)

    def state(self) -> bytes:
        """Return the current transcript digest for inspection."""
        return self._state
