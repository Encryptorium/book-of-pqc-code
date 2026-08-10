"""L-tree compression for WOTS+ public keys.

An L-tree is a binary hash tree that compresses *ell* public-key chain
endpoints into a single *n*-byte value.  When *ell* is not a power of
two, the last node at each level is promoted to the next level without
hashing.
"""

import hashlib


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def ltree(pk_values: list[bytes], pk_seed: bytes) -> bytes:
    """Compress *pk_values* into a single hash via an L-tree.

    At each level, adjacent nodes are paired and hashed.  If the count
    is odd, the last node is promoted unchanged.  The hash at each step
    is ``SHA256(pk_seed || level (4 B) || pair_index (4 B) || left || right)``.
    *pk_seed* is the public chain-domain seed (the verifier's domain separator).
    """
    nodes = list(pk_values)
    level = 0
    while len(nodes) > 1:
        next_level: list[bytes] = []
        i = 0
        pair_index = 0
        while i + 1 < len(nodes):
            combined = _sha256(
                pk_seed
                + level.to_bytes(4, "big")
                + pair_index.to_bytes(4, "big")
                + nodes[i]
                + nodes[i + 1]
            )
            next_level.append(combined)
            i += 2
            pair_index += 1
        if i < len(nodes):
            next_level.append(nodes[i])
        nodes = next_level
        level += 1
    return nodes[0]
