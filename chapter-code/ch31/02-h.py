# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 31: The four-layer decomposition
# Section: "The four layers in a toy running example"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch31-four-layer-decomposition/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch31/02-h.py

# Block 2: pedagogical slice of a Merkle commitment at L2 (stdlib only).
# Production trees domain-separate leaves and internal nodes,
# e.g. H(b"\x00" + leaf) vs H(b"\x01" + left + right); omitted here.
import hashlib


def H(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def commit(leaves):
    if len(leaves) == 0 or (len(leaves) & (len(leaves) - 1)) != 0:
        raise ValueError("leaves must be a nonempty power of two")
    nodes = [H(leaf) for leaf in leaves]
    while len(nodes) > 1:
        nodes = [H(nodes[i] + nodes[i + 1]) for i in range(0, len(nodes), 2)]
    return nodes[0]


def open_path(leaves, index):
    path = []
    nodes = [H(leaf) for leaf in leaves]
    while len(nodes) > 1:
        path.append(nodes[index ^ 1])
        nodes = [H(nodes[i] + nodes[i + 1]) for i in range(0, len(nodes), 2)]
        index //= 2
    return path


def verify_path(leaf, index, path, root):
    # The index is public input, so the verifier derives the left/right
    # position at each level from it rather than trusting the prover.
    acc = H(leaf)
    for sibling in path:
        acc = H(sibling + acc) if index & 1 else H(acc + sibling)
        index //= 2
    return acc == root


leaves = [b"x0", b"x1", b"x2", b"x3"]
root = commit(leaves)
path = open_path(leaves, 2)
print(verify_path(b"x2", 2, path, root))
# ==> True
