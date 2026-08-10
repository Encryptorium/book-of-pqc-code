"""ADRS (address) structure for SLH-DSA (FIPS 205 Section 4.2).

The ADRS is a mutable 32-byte structure that domain-separates every
hash call in SLH-DSA.  Each hash function receives the ADRS as a
tweak, ensuring that identical inputs at different positions in the
tree produce different outputs.

Field layout (all values big-endian, per FIPS 205 Section 4.2):

    Bytes 0-3:   layer address
    Bytes 4-15:  tree address (12 bytes)
    Bytes 16-19: type
    Bytes 20-23: keypair address (WOTS/FORS types) / padding (TREE)
    Bytes 24-27: chain address (WOTS_HASH) / tree height (TREE, FORS_TREE)
    Bytes 28-31: hash address (WOTS_HASH) / tree index (TREE, FORS_TREE)

``set_type`` zeros bytes 20-31 (the context-dependent fields).
"""

from __future__ import annotations

import struct


# ADRS type constants (FIPS 205 Section 4.2)
WOTS_HASH = 0
WOTS_PK = 1
TREE = 2
FORS_TREE = 3
FORS_ROOTS = 4
WOTS_PRF = 5
FORS_PRF = 6


class ADRS:
    """Mutable 32-byte SLH-DSA address structure."""

    __slots__ = ("_data",)

    def __init__(self) -> None:
        self._data = bytearray(32)

    # -- Field accessors (big-endian) --------------------------------------

    def set_layer_address(self, v: int) -> None:
        struct.pack_into(">I", self._data, 0, v)

    def get_layer_address(self) -> int:
        # EXERCISE: implement this function.
        #
        # Read the 4-byte big-endian integer at bytes 0 to 3.
        # struct.unpack_from returns a tuple, so index element zero.
        #
        # Reference: Chapter 17, 'The address structure' (FIPS 205 Section 4.2)
        #
        # Proved by:
        #   tests/ch17/test_adrs.py
        raise NotImplementedError("exercise: ADRS.get_layer_address")

    def set_tree_address(self, v: int) -> None:
        # 12-byte big-endian integer at bytes 4-15
        self._data[4:16] = v.to_bytes(12, "big")

    def get_tree_address(self) -> int:
        # EXERCISE: implement this function.
        #
        # Read bytes 4 to 15 back as one 12-byte big-endian integer with
        # int.from_bytes.
        #
        # Reference: Chapter 17, 'The address structure' (FIPS 205 Section 4.2)
        #
        # Proved by:
        #   tests/ch17/test_adrs.py
        raise NotImplementedError("exercise: ADRS.get_tree_address")

    def set_type(self, v: int) -> None:
        """Set the type field and zero bytes 20-31 (context-dependent)."""
        struct.pack_into(">I", self._data, 16, v)
        self._data[20:32] = b"\x00" * 12

    def get_type(self) -> int:
        # EXERCISE: implement this function.
        #
        # Read the 4-byte big-endian integer at bytes 16 to 19. The seven
        # values are the module constants WOTS_HASH through FORS_PRF, 0
        # through 6.
        #
        # Reference: Chapter 17, 'The address structure' (FIPS 205 Section 4.2)
        #
        # Proved by:
        #   tests/ch17/test_adrs.py
        raise NotImplementedError("exercise: ADRS.get_type")

    def set_keypair_address(self, v: int) -> None:
        struct.pack_into(">I", self._data, 20, v)

    def get_keypair_address(self) -> int:
        return struct.unpack_from(">I", self._data, 20)[0]

    def set_chain_address(self, v: int) -> None:
        struct.pack_into(">I", self._data, 24, v)

    def get_chain_address(self) -> int:
        # EXERCISE: implement this function.
        #
        # Read the 4-byte big-endian integer at bytes 24 to 27.
        #
        # Reference: Chapter 17, 'The address structure' (FIPS 205 Section 4.2)
        #
        # Proved by:
        #   tests/ch17/test_adrs.py
        raise NotImplementedError("exercise: ADRS.get_chain_address")

    def set_hash_address(self, v: int) -> None:
        struct.pack_into(">I", self._data, 28, v)

    def get_hash_address(self) -> int:
        # EXERCISE: implement this function.
        #
        # Read the 4-byte big-endian integer at bytes 28 to 31.
        #
        # Reference: Chapter 17, 'The address structure' (FIPS 205 Section 4.2)
        #
        # Proved by:
        #   tests/ch17/test_adrs.py
        raise NotImplementedError("exercise: ADRS.get_hash_address")

    def set_tree_height(self, v: int) -> None:
        struct.pack_into(">I", self._data, 24, v)

    def get_tree_height(self) -> int:
        # EXERCISE: implement this function.
        #
        # Read the 4-byte big-endian integer at bytes 24 to 27, the TREE and
        # FORS_TREE reading of the same bytes get_chain_address returns.
        #
        # Reference: Chapter 17, 'The address structure' (FIPS 205 Section 4.2)
        #
        # Proved by:
        #   tests/ch17/test_adrs.py
        raise NotImplementedError("exercise: ADRS.get_tree_height")

    def set_tree_index(self, v: int) -> None:
        struct.pack_into(">I", self._data, 28, v)

    def get_tree_index(self) -> int:
        # EXERCISE: implement this function.
        #
        # Read the 4-byte big-endian integer at bytes 28 to 31, the TREE and
        # FORS_TREE reading of the same bytes get_hash_address returns.
        #
        # Reference: Chapter 17, 'The address structure' (FIPS 205 Section 4.2)
        #
        # Proved by:
        #   tests/ch17/test_adrs.py
        raise NotImplementedError("exercise: ADRS.get_tree_index")

    # -- Serialization -----------------------------------------------------

    def to_bytes(self) -> bytes:
        """Return the full 32-byte ADRS."""
        # EXERCISE: implement this function.
        #
        # Return the 32 bytes as an immutable bytes object rather than the
        # backing bytearray, so a caller cannot reach through the return
        # value and mutate the address. This is the form the SHAKE parameter
        # sets hash: they absorb the full 32-byte address, where the SHA2
        # sets absorb the 22-byte compressed form instead.
        #
        # Reference: Chapter 17, 'Compressed ADRS' (FIPS 205 Section 11.1, the SHAKE instantiation, which absorbs the full address; Section 11.2 defines the 22-byte compressed form the SHA2 sets use)
        #
        # Proved by:
        #   tests/ch17/test_adrs.py
        raise NotImplementedError("exercise: ADRS.to_bytes")

    def compress(self) -> bytes:
        """Return the 22-byte compressed ADRS for SHA-256 instantiation.

        Compressed form (FIPS 205 Section 11.2):
            ADRS[3] || ADRS[8:16] || ADRS[19] || ADRS[20:32]
        """
        return (
            bytes([self._data[3]])
            + bytes(self._data[8:16])
            + bytes([self._data[19]])
            + bytes(self._data[20:32])
        )

    # -- Copy --------------------------------------------------------------

    def copy(self) -> ADRS:
        """Return an independent copy."""
        a = ADRS()
        a._data[:] = self._data
        return a

    def __repr__(self) -> str:
        return (
            f"ADRS(layer={self.get_layer_address()}, "
            f"tree={self.get_tree_address()}, "
            f"type={self.get_type()}, "
            f"kp={self.get_keypair_address()})"
        )
