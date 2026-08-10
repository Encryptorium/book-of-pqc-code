"""Merkle signature scheme combining Lamport OTS with a Merkle tree.

The signer generates ``2**d`` Lamport keypairs, builds a Merkle tree
over the serialized public keys, and publishes the root.  Each
signature carries a Lamport signature, the corresponding public key,
and an authentication path from the leaf to the root.
"""

import hashlib

from .lamport import keygen as lamport_keygen
from .lamport import sign as lamport_sign
from .lamport import verify as lamport_verify
from .merkle import auth_path, build_tree, root, verify_path


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _serialize_pk(pk: list[tuple[bytes, bytes]]) -> bytes:
    """Serialize a Lamport public key by concatenating all hashes."""
    parts: list[bytes] = []
    for h0, h1 in pk:
        parts.append(h0)
        parts.append(h1)
    return b"".join(parts)


def mss_keygen(d: int = 3, rng_seed: bytes | None = None):
    """Generate a Merkle signature scheme keypair.

    Parameters
    ----------
    d : int
        Tree depth.  The scheme supports ``2**d`` one-time signatures.
    rng_seed : bytes or None
        If provided, each Lamport keypair uses a deterministic seed
        derived from *rng_seed* and the leaf index.

    Returns
    -------
    all_sk : list
        A list of ``2**d`` Lamport secret keys.
    all_pk : list
        A list of ``2**d`` Lamport public keys.
    tree : list[bytes]
        The Merkle tree (1-indexed flat array).
    root_hash : bytes
        The Merkle root (the single published public key).
    """
    num_leaves = 1 << d
    all_sk = []
    all_pk = []
    leaves: list[bytes] = []
    for i in range(num_leaves):
        if rng_seed is not None:
            leaf_seed = rng_seed + i.to_bytes(4, "big")
        else:
            leaf_seed = None
        sk, pk = lamport_keygen(rng=leaf_seed)
        all_sk.append(sk)
        all_pk.append(pk)
        leaves.append(_sha256(_serialize_pk(pk)))

    tree = build_tree(leaves)
    root_hash = root(tree)
    return all_sk, all_pk, tree, root_hash


def mss_sign(all_sk, all_pk, tree, leaf_index: int, message: bytes):
    """Sign *message* using the one-time key at *leaf_index*.

    Parameters
    ----------
    all_sk : list
        All Lamport secret keys from :func:`mss_keygen`.
    all_pk : list
        All Lamport public keys from :func:`mss_keygen`.
    tree : list[bytes]
        The Merkle tree from :func:`mss_keygen`.
    leaf_index : int
        Which one-time key to consume (zero-based).
    message : bytes
        The message to sign.

    Returns
    -------
    lamport_sig : list[bytes]
        The Lamport signature (256 revealed secrets).
    lamport_pk : list[tuple[bytes, bytes]]
        The Lamport public key for this leaf.
    path : list[bytes]
        The authentication path from the leaf to the root.
    """
    sk = all_sk[leaf_index]
    pk = all_pk[leaf_index]
    lamport_sig = lamport_sign(sk, message)
    path = auth_path(tree, leaf_index)
    return lamport_sig, pk, path


def mss_verify(
    root_hash: bytes,
    message: bytes,
    lamport_sig: list[bytes],
    lamport_pk: list[tuple[bytes, bytes]],
    path: list[bytes],
    leaf_index: int,
) -> bool:
    """Verify a Merkle signature scheme signature.

    Returns *True* iff the Lamport signature is valid AND the
    authentication path leads from the leaf (hash of the Lamport public
    key) to *root_hash*.
    """
    if not lamport_verify(lamport_pk, message, lamport_sig):
        return False
    leaf = _sha256(_serialize_pk(lamport_pk))
    return verify_path(leaf, leaf_index, path, root_hash)
