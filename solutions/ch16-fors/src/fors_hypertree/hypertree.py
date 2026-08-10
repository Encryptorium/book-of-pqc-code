"""Multi-layer hypertree built from WOTS+ Merkle subtrees.

A hypertree of total height ``d * h_prime`` consists of *d* layers.
Each layer is a collection of Merkle trees whose leaves are WOTS+
compressed public keys (via L-tree).  The bottom layer signs the
message directly; each upper layer signs the root of the subtree
below it.  The top-layer root is the hypertree public key.

All WOTS+, L-tree, and Merkle operations are inlined from the Ch 15
implementations to keep this module self-contained (no import from
wots_xmss).
"""

import hashlib
import math


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


# -- WOTS+ (inlined from Ch 15) ----------------------------------------

def _base_w(data: bytes, w: int, out_len: int) -> list[int]:
    """Encode *data* as base-*w* digits (MSB-first per byte)."""
    lg_w = int(math.log2(w))
    digits: list[int] = []
    for byte in data:
        for shift in range(8 - lg_w, -1, -lg_w):
            digits.append((byte >> shift) & (w - 1))
            if len(digits) == out_len:
                return digits
    return digits[:out_len]


def _ell_params(n: int, w: int) -> tuple[int, int, int]:
    """Return (ell_1, ell_2, ell) for hash output *n* bytes, base *w*."""
    lg_w = int(math.log2(w))
    ell_1 = math.ceil(8 * n / lg_w)
    max_checksum = ell_1 * (w - 1)
    ell_2 = math.ceil((math.floor(math.log2(max_checksum)) + 1) / lg_w)
    return ell_1, ell_2, ell_1 + ell_2


def _checksum(msg_digits: list[int], w: int) -> list[int]:
    """Compute the WOTS+ checksum and encode in base *w*."""
    c = sum(w - 1 - d for d in msg_digits)
    lg_w = int(math.log2(w))
    max_checksum = len(msg_digits) * (w - 1)
    ell_2 = math.ceil((math.floor(math.log2(max_checksum)) + 1) / lg_w)
    total_bits = ell_2 * lg_w
    num_bytes = math.ceil(total_bits / 8)
    shift = 8 * num_bytes - total_bits
    c_shifted = c << shift
    c_bytes = c_shifted.to_bytes(num_bytes, "big")
    return _base_w(c_bytes, w, ell_2)


def _chain(x: bytes, start: int, steps: int, seed: bytes, addr: int) -> bytes:
    """Iterate the WOTS+ chain function *steps* times from *start*."""
    value = x
    for i in range(start, start + steps):
        value = _sha256(
            seed + addr.to_bytes(4, "big") + i.to_bytes(4, "big") + value
        )
    return value


def _wots_keygen(
    seed: bytes, w: int = 16, n: int = 32
) -> tuple[list[bytes], list[bytes]]:
    """Generate a WOTS+ keypair from *seed*."""
    _, _, ell = _ell_params(n, w)
    sk: list[bytes] = []
    for i in range(ell):
        sk.append(_sha256(seed + b"sk" + i.to_bytes(4, "big")))
    pk = [_chain(sk[i], 0, w - 1, seed, i) for i in range(ell)]
    return sk, pk


def _wots_sign(
    sk: list[bytes], message: bytes, seed: bytes, w: int = 16, n: int = 32
) -> list[bytes]:
    """Sign *message* under the WOTS+ secret key *sk*."""
    ell_1, _, ell = _ell_params(n, w)
    digest = _sha256(message)
    msg_digits = _base_w(digest, w, ell_1)
    csum_digits = _checksum(msg_digits, w)
    digits = msg_digits + csum_digits
    return [_chain(sk[i], 0, digits[i], seed, i) for i in range(ell)]


def _wots_verify(
    pk: list[bytes], message: bytes, sig: list[bytes],
    seed: bytes, w: int = 16, n: int = 32
) -> bool:
    """Verify a WOTS+ signature."""
    ell_1, _, ell = _ell_params(n, w)
    if len(sig) != ell:
        return False
    digest = _sha256(message)
    msg_digits = _base_w(digest, w, ell_1)
    csum_digits = _checksum(msg_digits, w)
    digits = msg_digits + csum_digits
    for i in range(ell):
        if _chain(sig[i], digits[i], w - 1 - digits[i], seed, i) != pk[i]:
            return False
    return True


# -- L-tree (inlined from Ch 15) ----------------------------------------

def _ltree(pk_values: list[bytes], seed: bytes) -> bytes:
    """Compress *pk_values* into a single hash via an L-tree."""
    nodes = list(pk_values)
    level = 0
    while len(nodes) > 1:
        next_level: list[bytes] = []
        i = 0
        pair_index = 0
        while i + 1 < len(nodes):
            combined = _sha256(
                seed
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


# -- Merkle tree (1-indexed flat array) ---------------------------------

def _build_tree(leaves: list[bytes]) -> list[bytes]:
    """Build a complete binary Merkle tree from *leaves*."""
    num_leaves = len(leaves)
    tree: list[bytes] = [b""] * (2 * num_leaves)
    for i, leaf in enumerate(leaves):
        tree[num_leaves + i] = leaf
    for i in range(num_leaves - 1, 0, -1):
        tree[i] = _sha256(tree[2 * i] + tree[2 * i + 1])
    return tree


def _auth_path(tree: list[bytes], leaf_index: int) -> list[bytes]:
    """Extract the authentication path for *leaf_index*."""
    num_leaves = len(tree) // 2
    depth = int(math.log2(num_leaves))
    node = num_leaves + leaf_index
    path: list[bytes] = []
    for _ in range(depth):
        path.append(tree[node ^ 1])
        node //= 2
    return path


def _verify_path(
    leaf: bytes, leaf_index: int, path: list[bytes], root: bytes
) -> bool:
    """Verify that *leaf* at *leaf_index* hashes to *root*."""
    current = leaf
    idx = leaf_index
    for sibling in path:
        if idx % 2 == 0:
            current = _sha256(current + sibling)
        else:
            current = _sha256(sibling + current)
        idx //= 2
    return current == root


# -- Hypertree keygen / sign / verify -----------------------------------

def hypertree_keygen(
    seed: bytes,
    d: int = 2,
    h_prime: int = 4,
    w: int = 16,
    n: int = 32,
) -> tuple[dict, bytes]:
    """Generate a hypertree keypair.

    Parameters
    ----------
    seed : bytes
        Master seed for deterministic key derivation.
    d : int
        Number of layers (default 2).
    h_prime : int
        Subtree height at each layer (default 4).  Total tree height
        is ``d * h_prime``.
    w : int
        Winternitz parameter (default 16).
    n : int
        Hash output length in bytes (default 32).

    Returns
    -------
    sk_structure : dict
        All WOTS+ keys and Merkle trees organized by layer and subtree
        position.
    pk : bytes
        The top-layer Merkle root (*n* bytes).
    """
    leaves_per_subtree = 1 << h_prime

    # Build from bottom layer (layer 0) up to top layer (layer d-1).
    # At each layer, the leaf values are either:
    #   - layer 0: caller-provided (for standalone hypertree, we generate
    #     dummy leaf data so the tree structure can be tested independently)
    #   - layer j > 0: the roots of the subtrees from layer j-1

    layers: list[dict] = []

    for layer in range(d):
        if layer == 0:
            num_subtrees = 1 << ((d - 1) * h_prime)
        else:
            num_subtrees = 1 << ((d - 1 - layer) * h_prime)

        layer_data: dict = {"subtrees": {}}

        for pos in range(num_subtrees):
            # Derive a unique seed for each subtree's WOTS+ keys
            subtree_seed = _sha256(
                seed + b"ht"
                + layer.to_bytes(4, "big")
                + pos.to_bytes(4, "big")
            )

            wots_sks: list[list[bytes]] = []
            wots_pks: list[list[bytes]] = []
            leaf_hashes: list[bytes] = []

            for leaf_idx in range(leaves_per_subtree):
                leaf_seed = subtree_seed + b"leaf" + leaf_idx.to_bytes(4, "big")
                sk, pk = _wots_keygen(leaf_seed, w=w, n=n)
                wots_sks.append(sk)
                wots_pks.append(pk)
                leaf_hashes.append(_ltree(pk, leaf_seed))

            tree = _build_tree(leaf_hashes)
            root = tree[1]

            layer_data["subtrees"][pos] = {
                "wots_sks": wots_sks,
                "wots_pks": wots_pks,
                "tree": tree,
                "root": root,
                "seed": subtree_seed,
            }

        layers.append(layer_data)

    pk = layers[d - 1]["subtrees"][0]["root"]
    return {"layers": layers, "d": d, "h_prime": h_prime}, pk


def hypertree_sign(
    sk_structure: dict,
    leaf_index: int,
    message: bytes,
    seed: bytes,
    d: int = 2,
    h_prime: int = 4,
    w: int = 16,
    n: int = 32,
) -> list[tuple[list[bytes], list[bytes], list[bytes]]]:
    """Sign *message* at *leaf_index* in the hypertree.

    Returns *d* layers, each a tuple of
    ``(wots_sig, wots_pk, auth_path)``.

    Layer 0: WOTS+ signs the message; auth path is in the bottom subtree.
    Layer j > 0: WOTS+ signs the root of the layer-(j-1) subtree.
    """
    layers = sk_structure["layers"]
    sig_layers: list[tuple[list[bytes], list[bytes], list[bytes]]] = []

    # The leaf_index encodes positions at all layers.
    # Bottom h_prime bits -> leaf within the layer-0 subtree.
    # Next h_prime bits -> which layer-0 subtree = leaf in layer-1 subtree.
    # And so on.

    current_message = message
    remaining_index = leaf_index

    for layer in range(d):
        within_subtree = remaining_index & ((1 << h_prime) - 1)
        subtree_pos = remaining_index >> h_prime

        subtree_data = layers[layer]["subtrees"][subtree_pos]
        leaf_seed = (
            subtree_data["seed"] + b"leaf" + within_subtree.to_bytes(4, "big")
        )

        wots_sig = _wots_sign(
            subtree_data["wots_sks"][within_subtree],
            current_message,
            leaf_seed,
            w=w, n=n,
        )
        wots_pk = subtree_data["wots_pks"][within_subtree]
        path = _auth_path(subtree_data["tree"], within_subtree)

        sig_layers.append((wots_sig, wots_pk, path))

        # The next layer signs this subtree's root
        current_message = subtree_data["root"]
        remaining_index = subtree_pos

    return sig_layers


def hypertree_verify(
    pk: bytes,
    leaf_index: int,
    message: bytes,
    sig_layers: list[tuple[list[bytes], list[bytes], list[bytes]]],
    seed: bytes,
    d: int = 2,
    h_prime: int = 4,
    w: int = 16,
    n: int = 32,
) -> bool:
    """Verify a hypertree signature.

    Walks from layer 0 upward.  At each layer, verifies the WOTS+
    signature, L-tree-compresses the pk to a leaf hash, and verifies the
    auth path to the subtree root.  The final subtree root must match *pk*.
    """
    if len(sig_layers) != d:
        return False

    current_message = message
    remaining_index = leaf_index

    for layer in range(d):
        within_subtree = remaining_index & ((1 << h_prime) - 1)
        subtree_pos = remaining_index >> h_prime

        wots_sig, wots_pk, path = sig_layers[layer]

        # Reconstruct the subtree seed for verification
        subtree_seed = _sha256(
            seed + b"ht"
            + layer.to_bytes(4, "big")
            + subtree_pos.to_bytes(4, "big")
        )
        leaf_seed = subtree_seed + b"leaf" + within_subtree.to_bytes(4, "big")

        # Verify WOTS+ signature
        if not _wots_verify(wots_pk, current_message, wots_sig, leaf_seed, w=w, n=n):
            return False

        # L-tree compress the WOTS+ public key to get the leaf hash
        leaf_hash = _ltree(wots_pk, leaf_seed)

        # Verify the authentication path
        # Reconstruct the subtree root
        current = leaf_hash
        idx = within_subtree
        for sibling in path:
            if idx % 2 == 0:
                current = _sha256(current + sibling)
            else:
                current = _sha256(sibling + current)
            idx //= 2

        subtree_root = current

        # The next layer's message is this subtree's root
        current_message = subtree_root
        remaining_index = subtree_pos

    # The final subtree root must match the hypertree public key
    return current_message == pk
