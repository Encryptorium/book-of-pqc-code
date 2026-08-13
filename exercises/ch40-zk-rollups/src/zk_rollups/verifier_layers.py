"""Four-layer decomposition of a ZK rollup verifier contract.

Ch 31 introduces the canonical four-layer decomposition of a SNARK or
STARK proof system:

- ``L1-arithmetization``: encode the statement as an arithmetic
  circuit, AIR (algebraic intermediate representation), R1CS, or
  Plonkish gate set. Off-chain in the prover; the verifier never
  re-runs L1.
- ``L2-commitment``: the prover commits to its arithmetized witness
  with a polynomial commitment scheme (PCS) or a Merkle commitment.
  The verifier checks the commitment opening on-chain. L2 is the
  load-bearing on-chain layer for soundness.
- ``L3-protocol-logic``: the IOP (interactive oracle proof) layer.
  Sumcheck, FRI proximity, GKR, or a custom protocol. Runs off-chain
  in the prover; the verifier-contract checks transcript consistency.
- ``L4-fiat-shamir``: the Fiat-Shamir transform with a hash function
  governs the verifier transcript. The hash function is the second
  load-bearing on-chain layer; an L4 swap from SHA-256 to a wider
  hash is the first move on the operator's migration playbook.

Per-layer candidate set at chain-tip 2026:

L1 candidates (off-chain; PQ-secure regardless because L1 is just
a structural choice for how the witness is encoded; the candidate
list records the gate set, not a security property):

- ``AIR`` (algebraic intermediate representation; STARK-style)
- ``R1CS`` (rank-1 constraint system; Groth16, Aurora)
- ``Plonkish`` (PLONK and successors, custom gates)

L2 commitment candidates (on-chain; the load-bearing security axis):

- ``KZG``: pairing-based polynomial commitment (Kate, Zaverucha,
  Goldberg 2010). Binding reduces to the d-strong Diffie-Hellman
  assumption on a pairing-friendly elliptic curve. Shor breaks the
  underlying discrete log; pq_status is shor-broken.
- ``FRI``: Merkle commitment plus the Fast Reed-Solomon Interactive
  Oracle Proof of Proximity. Soundness reduces to collision
  resistance of the Merkle hash and the proximity-gap parameter.
  Grover speeds up collision-finding from 2^n to 2^{n/3} (BHT) or
  2^{2n/5} (CNPS without quantum RAM); pq_status is grover-weakened.
- ``Merkle``: plain Merkle-tree commitment used as a vector
  commitment. Same Grover-weakening as FRI on the hash.
- ``lattice-PCS``: lattice-based polynomial commitment built from
  Module-SIS. No quantum speedup beyond the classical hardness of
  Module-SIS; pq_status is pq-secure. Research-grade at chain-tip
  2026; no production rollup deployment.

L3 protocol-logic candidates (the IOP layer):

- ``Sumcheck-IOP``: sumcheck-based IOP. Soundness is information-
  theoretic at the IOP level; the layer carries no quantum
  vulnerability beyond what L2 and L4 inherit.
- ``FRI-IOP``: the FRI-based IOP layered over a Merkle commitment.
  Inherits L2's grover-weakening through the underlying hash.
- ``IPA-IOP``: inner-product-argument IOP (Bulletproofs, Halo 2).
  Soundness reduces to discrete log; Shor-broken.

L4 Fiat-Shamir hash candidates (on-chain; the second load-bearing
security axis, governing transcript binding under non-interactivity
plus extraction):

- ``SHA-256``: 256-bit output, Grover-weakened to ~85 bits of
  preimage and ~85 bits of collision resistance under the BHT
  bound (BrassardHoyerTapp 1998).
- ``SHAKE-128``: SHA-3-family extendable-output function at the
  128-bit security level. Output length is variable; for a STARK
  Fiat-Shamir at 256-bit transcript bytes the BHT bound gives
  ~85 bits of PQ collision resistance.
- ``SHAKE-256``: SHA-3-family XOF at the 256-bit security level.
  At 512-bit transcript bytes the BHT bound gives ~170 bits of
  PQ collision resistance, the conservative-assumption preference.
- ``Keccak-256``: native EVM hash opcode (KECCAK256). Same
  cryptographic security as SHA-3-256; cheaper on-chain than the
  SHA-256 precompile when measured per byte of input.

Status vocabulary (chosen to avoid collision with prose adjectives):

- ``pq-secure``: no known quantum speedup beyond polynomial.
- ``grover-weakened``: Grover gives a square-root or cube-root
  speedup against the underlying primitive.
- ``shor-broken``: Shor gives a polynomial-time attack against the
  underlying primitive's hardness assumption.
- ``pq-research``: candidate is a research-grade construction with
  no NIST standard at chain-tip 2026.
- ``off-chain``: the layer is not exposed on-chain in the rollup
  verifier-contract model; the candidate is recorded for
  completeness but the cell decision does not bind on-chain.

Two production-system anchors at chain-tip 2026 (for the chapter's
real-world framing):

- ZKsync Era (Boojum upgrade, PLONK arithmetization with FRI
  commitment) deploys L1=Plonkish, L2=FRI, L4=SHA-256.
- Starknet (ethSTARK with FRI commitment) deploys L1=AIR, L2=FRI,
  L4=SHA-256.

Both are recorded as named tuples in the module so the chapter can
reference them by name without re-deriving.

Note on outer-wrapper claims (ZKsync): public reporting indicates
ZKsync's Boojum verifier wraps the inner FRI-based proof in an
outer pairing-based proof for compression. This outer-wrapper
claim is engineering-level inference from public sources, not a
direct consequence of a primary technical specification (the same
hedge Ch 35 attaches to the same statement). The data model in
this module records only the inner four-layer decomposition; an
outer wrapper, if present, sits at a separate L2 layer that
``system_profile`` does not surface. Callers reasoning about the
ZKsync outer-wrapper PQ status should consult Ch 35 and the
chapter prose, not the raw output of ``system_profile``.
"""

from typing import Dict, List, Tuple, TypedDict


class LayerCell(TypedDict):
    pq_status: str
    deployment_status: str
    rationale: str


LAYERS: Tuple[str, ...] = (
    "L1-arithmetization",
    "L2-commitment",
    "L3-protocol-logic",
    "L4-fiat-shamir",
)

CANDIDATES_BY_LAYER: Dict[str, Tuple[str, ...]] = {
    "L1-arithmetization": ("AIR", "R1CS", "Plonkish"),
    "L2-commitment": ("KZG", "FRI", "Merkle", "lattice-PCS"),
    "L3-protocol-logic": ("Sumcheck-IOP", "FRI-IOP", "IPA-IOP"),
    "L4-fiat-shamir": ("SHA-256", "SHAKE-128", "SHAKE-256", "Keccak-256"),
}


def _cell(pq_status: str, deployment_status: str, rationale: str) -> LayerCell:
    return {
        "pq_status": pq_status,
        "deployment_status": deployment_status,
        "rationale": rationale,
    }


# Layer x candidate decision matrix. Each cell records the post-quantum
# status (the load-bearing axis), the chain-tip 2026 deployment status,
# and a one-line rationale that the chapter can cite when a table renders.
MATRIX: Dict[str, Dict[str, LayerCell]] = {
    "L1-arithmetization": {
        "AIR": _cell(
            "off-chain",
            "production",
            "STARK-style arithmetization deployed in ethSTARK and Starknet",
        ),
        "R1CS": _cell(
            "off-chain",
            "production",
            "Groth16 and Aurora arithmetization; deployed in Zcash",
        ),
        "Plonkish": _cell(
            "off-chain",
            "production",
            "PLONK and Halo 2 arithmetization; deployed in ZKsync Boojum",
        ),
    },
    "L2-commitment": {
        "KZG": _cell(
            "shor-broken",
            "production",
            "binding reduces to d-SDH on a pairing-friendly curve",
        ),
        "FRI": _cell(
            "grover-weakened",
            "production",
            "Merkle plus proximity gap; Grover gives a cube-root speedup on the hash",
        ),
        "Merkle": _cell(
            "grover-weakened",
            "production",
            "vector commitment; binding reduces to hash collision resistance",
        ),
        "lattice-PCS": _cell(
            "pq-secure",
            "pq-research",
            "Module-SIS based; research-grade at chain-tip 2026",
        ),
    },
    "L3-protocol-logic": {
        "Sumcheck-IOP": _cell(
            "off-chain",
            "production",
            "information-theoretic at the IOP layer; deployed in spartan-style provers",
        ),
        "FRI-IOP": _cell(
            "off-chain",
            "production",
            "FRI proximity layered over Merkle; off-chain logic, on-chain hash check at L2",
        ),
        "IPA-IOP": _cell(
            "shor-broken",
            "production",
            "inner-product argument; soundness reduces to discrete log",
        ),
    },
    "L4-fiat-shamir": {
        "SHA-256": _cell(
            "grover-weakened",
            "legacy",
            "256-bit output gives ~85 bits PQ under the BHT bound",
        ),
        "SHAKE-128": _cell(
            "grover-weakened",
            "production",
            "SHA-3 XOF at 128-bit security; same Grover bound on the output",
        ),
        "SHAKE-256": _cell(
            "grover-weakened",
            "production",
            "SHA-3 XOF at 256-bit security; the conservative-assumption preference",
        ),
        "Keccak-256": _cell(
            "grover-weakened",
            "production",
            "native EVM opcode; cheapest on-chain hash per input byte",
        ),
    },
}


# Production-system anchors at chain-tip 2026.
class SystemAnchor(TypedDict):
    name: str
    L1: str
    L2: str
    L3: str
    L4: str
    citation_key: str


SYSTEM_ANCHORS: Dict[str, SystemAnchor] = {
    "ZKsync-Era-Boojum": {
        "name": "ZKsync-Era-Boojum",
        "L1": "Plonkish",
        "L2": "FRI",
        "L3": "FRI-IOP",
        "L4": "SHA-256",
        "citation_key": "ZKsyncBoojum2023",
    },
    "Starknet-ethSTARK": {
        "name": "Starknet-ethSTARK",
        "L1": "AIR",
        "L2": "FRI",
        "L3": "FRI-IOP",
        "L4": "SHA-256",
        "citation_key": "BenSassonEthSTARK2021",
    },
}


def lookup(layer: str, candidate: str) -> Dict[str, object]:
    """Return the per-cell decision for a (layer, candidate) pair.

    Each cell carries the post-quantum status, the chain-tip 2026
    deployment status, and a one-line rationale.
    """
    # EXERCISE: implement this function.
    #
    # Assert the layer first, then assert the candidate against that layer's
    # entry in CANDIDATES_BY_LAYER rather than against a flat candidate set,
    # so a candidate valid at one layer is rejected at another: KZG is an L2
    # cell and must not resolve at L4. Index MATRIX by layer then candidate
    # and flatten the cell into a dict carrying layer, candidate, pq_status,
    # deployment_status, and rationale. Read the table before writing the
    # return, because pq_status is the load-bearing column: KZG and IPA-IOP
    # are shor-broken through pairing and inner-product discrete log, FRI,
    # Merkle, and every L4 hash are grover-weakened, lattice-PCS is the only
    # pq-secure cell and the only one whose deployment_status is
    # pq-research, and every L1 arithmetization cell is off-chain because
    # the verifier contract never re-runs L1.
    #
    # Reference: Chapter 40, 'Decompose the verifier into layers and pick a per-layer candidate'
    #
    # Proved by:
    #   tests/ch40/test_verifier_layers.py
    raise NotImplementedError("exercise: lookup")


def deployment_summary() -> List[Dict[str, object]]:
    """Flatten the full layer x candidate matrix into a list of cells.

    Order matches LAYERS x CANDIDATES_BY_LAYER so a chapter table renders
    deterministically. Useful for the chapter's inline Block 1 print and
    for a test that asserts the deterministic order.
    """
    out: List[Dict[str, object]] = []
    for layer in LAYERS:
        for candidate in CANDIDATES_BY_LAYER[layer]:
            out.append(lookup(layer, candidate))
    return out


def candidates_with_status(pq_status: str) -> List[Tuple[str, str]]:
    """Return every (layer, candidate) pair carrying the given pq_status.

    Useful for the chapter to enumerate, for example, every
    Shor-broken cell across all four layers in one pass.
    """
    # EXERCISE: implement this function.
    #
    # Assert pq_status against the five-value vocabulary the module defines
    # (pq-secure, grover-weakened, shor-broken, pq-research, off-chain),
    # then walk LAYERS and each layer's candidate tuple in declared order,
    # collecting the (layer, candidate) pairs whose MATRIX cell carries that
    # status. Iterate the constants rather than the matrix dict so the
    # result keeps the chapter's table order. This is the query behind the
    # chapter's cross-layer claims: shor-broken spans two layers (KZG at L2,
    # IPA-IOP at L3), pq-secure has exactly one cell, and off-chain covers
    # all three L1 candidates.
    #
    # Reference: Chapter 40, 'The Ch 31 four-layer decomposition under post-quantum primitives'
    #
    # Proved by:
    #   tests/ch40/test_verifier_layers.py
    raise NotImplementedError("exercise: candidates_with_status")


def system_profile(system_name: str) -> Dict[str, object]:
    """Return the per-layer profile for a named production system anchor.

    Each layer carries the candidate name plus the per-cell decision
    so the chapter can read off the system's chain-tip 2026 posture.
    The profile records the inner four-layer decomposition only. An
    outer-wrapper layer, if present (as on ZKsync per the Ch 35
    hedge), sits outside the data model; consult the chapter prose
    for the operator-side outer-wrapper migration framing.

    The returned dict carries an ``inner_only`` flag set to True so
    a caller cannot silently misread the inner-only scope. The flag
    is the data-model equivalent of the docstring hedge.
    """
    # EXERCISE: implement this function.
    #
    # Assert the system name, read its SYSTEM_ANCHORS row, and build a
    # profile carrying name, citation_key, an inner_only flag set to True, a
    # non-empty outer_wrapper_note, and a layers dict. The layers dict maps
    # each of the four full layer keys to a lookup of that layer against the
    # anchor's short-key candidate, so ZKsync Era Boojum resolves Plonkish,
    # FRI, FRI-IOP, SHA-256 and Starknet ethSTARK resolves AIR, FRI,
    # FRI-IOP, SHA-256. The inner_only flag is the data-model half of the
    # chapter's hedge: an outer pairing wrapper, if present, sits outside
    # this four-layer model, so a caller reading the profile alone must not
    # conclude the system carries no Shor-broken cell.
    #
    # Reference: Chapter 40, 'Decompose the verifier into layers and pick a per-layer candidate'
    #
    # Proved by:
    #   tests/ch40/test_verifier_layers.py
    raise NotImplementedError("exercise: system_profile")
