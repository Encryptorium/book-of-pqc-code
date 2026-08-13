"""Chapter 31: the four-layer decomposition of a zero-knowledge proof system.

Three modules, one per thing the chapter needs to make concrete:

- ``r1cs``: the L1 constraint format the chapter prints, plus the
  per-gate cost model that decides what arithmetizing a computation
  costs.
- ``merkle``: the L2 binary Merkle commitment the chapter prints, with
  the domain separation the printed block flags as omitted.
- ``layers``: the decomposition itself, as the layer table, the
  per-system posture table, and the two lookups that read them.

Nothing here is production cryptography, and the ``layers`` module is
not cryptography at all. See ``README.md`` for the full list of
divergences from what a deployed system does.
"""

from .layers import (
    LAYERS,
    LAYER_KEYS,
    POSTURES,
    SYSTEMS,
    Layer,
    SystemProfile,
    hash_bits_for_pq_collision,
    layer_posture,
    thinnest_layer,
)
from .merkle import (
    LEAF_TAG,
    NODE_TAG,
    H,
    commit,
    hash_leaf,
    hash_node,
    open_path,
    verify_path,
)
from .r1cs import GATES, Gate, check_r1cs, dot, gate_constraints

__all__ = [
    "GATES",
    "Gate",
    "H",
    "LAYERS",
    "LAYER_KEYS",
    "LEAF_TAG",
    "Layer",
    "NODE_TAG",
    "POSTURES",
    "SYSTEMS",
    "SystemProfile",
    "check_r1cs",
    "commit",
    "dot",
    "gate_constraints",
    "hash_bits_for_pq_collision",
    "hash_leaf",
    "hash_node",
    "layer_posture",
    "open_path",
    "thinnest_layer",
    "verify_path",
]
