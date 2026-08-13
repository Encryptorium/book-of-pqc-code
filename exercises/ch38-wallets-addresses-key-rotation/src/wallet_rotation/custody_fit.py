"""Custody-shape by primitive fit lookup.

The chapter's running example operates over a fixed 6 by 4 matrix of
custody-shape by signing-primitive fit decisions. Each cell carries
a fit label drawn from {legacy, fit, marginal, unfit} and two
underlying compatibility flags (state-management compatible, byte
budget compatible) that produce the fit label.

The four custody shapes:

- ``single-device-hot``: a phone or laptop wallet that signs on
  demand. One device, one signing key set, one local state file.
- ``multi-device-hot``: a wallet whose seed derives child keys
  across multiple devices (phone + desktop + browser plug-in).
  Each device signs from the shared seed; state cannot be
  synchronized across devices in real time.
- ``hardware-only-cold``: a hardware wallet (secure element)
  that signs rarely, with state stored locally on the device.
- ``multisig-cold``: an M-of-N cold-storage arrangement where each
  cosigner holds an independent key and partial signatures
  combine off-chain. Each cosigner has independent state.

The six candidate primitives match Ch 37 plus the two stateful
hash-based schemes (XMSS-MT, LMS) that re-enter consideration for
hardware-only single-device custody.

Fit labels:

- ``legacy``: the pre-migration baseline. Deployed today; the
  source of the wallet migration, not a migration target.
- ``fit``: operationally viable as a migration target with no
  significant friction.
- ``marginal``: operationally viable but with measurable friction
  (signature size on per-spend hot wallets, signing speed on
  constrained hardware, or composite byte overhead).
- ``unfit``: operationally broken under the shape's assumptions.

The compatibility flags capture the underlying rationale:

- ``state_compatible``: whether the primitive's state-management
  model survives the custody shape.
- ``byte_compatible``: whether the primitive's per-spend signature
  size fits the shape's frequency of use.
"""

from typing import Dict, List, Tuple, TypedDict


class FitCell(TypedDict):
    fit: str
    state_compatible: bool
    byte_compatible: bool
    rationale: str


CUSTODY_SHAPES: Tuple[str, ...] = (
    "single-device-hot",
    "multi-device-hot",
    "hardware-only-cold",
    "multisig-cold",
)

PRIMITIVES: Tuple[str, ...] = (
    "ECDSA-secp256k1",
    "ML-DSA-65",
    "SLH-DSA-128s",
    "Ed25519+ML-DSA-65",
    "XMSS-MT",
    "LMS",
)


def _row(
    state_compat: Dict[str, bool],
    byte_compat: Dict[str, bool],
    legacy_shapes: Tuple[str, ...] = (),
    marginal_shapes: Tuple[str, ...] = (),
    rationale: str = "",
) -> Dict[str, FitCell]:
    """Build one row of the matrix from the per-shape compatibility flags.

    Each cell takes its label from the compatibility flags:
    ``state_compat[shape]`` and ``byte_compat[shape]`` together produce
    ``unfit`` whenever either flag is False; both True yield ``fit``.
    Two overrides apply on top: ``legacy_shapes`` overrides the cell
    label to ``legacy`` (the pre-migration baseline); ``marginal_shapes``
    overrides the cell label to ``marginal`` (the cell is operationally
    viable but with measurable byte-budget or signing-time pressure).
    """
    row: Dict[str, FitCell] = {}
    for shape in CUSTODY_SHAPES:
        s_ok = state_compat[shape]
        b_ok = byte_compat[shape]
        if shape in legacy_shapes:
            label = "legacy"
        elif not s_ok or not b_ok:
            label = "unfit"
        else:
            label = "fit"
        row[shape] = {
            "fit": label,
            "state_compatible": s_ok,
            "byte_compatible": b_ok,
            "rationale": rationale,
        }
    for shape in marginal_shapes:
        row[shape]["fit"] = "marginal"
    return row


# ECDSA-secp256k1 is the pre-migration baseline; mark every shape "legacy".
_ECDSA = _row(
    state_compat={shape: True for shape in CUSTODY_SHAPES},
    byte_compat={shape: True for shape in CUSTODY_SHAPES},
    legacy_shapes=CUSTODY_SHAPES,
    rationale="legacy baseline; deployed but Shor-vulnerable, the source of the migration",
)

# ML-DSA-65 is stateless and signature size is moderate; fits all four shapes.
_ML_DSA_65 = _row(
    state_compat={shape: True for shape in CUSTODY_SHAPES},
    byte_compat={shape: True for shape in CUSTODY_SHAPES},
    rationale="stateless lattice signature; 3309-byte sig per FIPS 204 fits hot and cold",
)

# SLH-DSA-128s is stateless. The 7856-byte signature pressures the per-spend
# hot path; both hot shapes carry byte_compatible=False, then upgrade from
# unfit to marginal via the marginal_shapes override (the scheme works,
# but the byte budget marginalizes per-spend use).
_SLH_DSA_128s = _row(
    state_compat={shape: True for shape in CUSTODY_SHAPES},
    byte_compat={
        "single-device-hot": False,
        "multi-device-hot": False,
        "hardware-only-cold": True,
        "multisig-cold": True,
    },
    marginal_shapes=("single-device-hot", "multi-device-hot"),
    rationale="stateless hash signature; 7856-byte sig per FIPS 205 marginalizes per-spend hot use",
)

# Ed25519+ML-DSA-65 composite is stateless. Composite carries 3373-byte sigs;
# fits all shapes but at a byte cost relative to ML-DSA-65 alone.
_COMPOSITE = _row(
    state_compat={shape: True for shape in CUSTODY_SHAPES},
    byte_compat={shape: True for shape in CUSTODY_SHAPES},
    rationale="composite is stateless; 3373-byte composite sig fits all four shapes during cutover",
)

# XMSS-MT is stateful. Hardware-only single-device shapes sustain a local
# state file inside a secure element; multi-device and multisig shapes
# break under state sync requirements. The single-device hot shape is
# downgraded to marginal because consumer-grade single-device hot wallets
# typically lack the tamper-resistant non-volatile state plus
# atomic-counter discipline NIST SP 800-208 effectively requires.
_XMSS_MT = _row(
    state_compat={
        "single-device-hot": True,
        "multi-device-hot": False,
        "hardware-only-cold": True,
        "multisig-cold": False,
    },
    byte_compat={shape: True for shape in CUSTODY_SHAPES},
    marginal_shapes=("single-device-hot",),
    rationale="stateful hypertree; single-device hot is marginal pending hardware-backed atomic counter; multi-device and multisig break under one-time-key index reuse",
)

# LMS is stateful. Same shape compatibility as XMSS-MT, including the
# marginal-on-single-device-hot downgrade for the same NVRAM atomic-counter
# discipline reason.
_LMS = _row(
    state_compat={
        "single-device-hot": True,
        "multi-device-hot": False,
        "hardware-only-cold": True,
        "multisig-cold": False,
    },
    byte_compat={shape: True for shape in CUSTODY_SHAPES},
    marginal_shapes=("single-device-hot",),
    rationale="stateful Merkle tree per RFC 8554; same single-device-hot marginal label and multi-device/multisig break as XMSS-MT",
)

MATRIX: Dict[str, Dict[str, FitCell]] = {
    "ECDSA-secp256k1": _ECDSA,
    "ML-DSA-65": _ML_DSA_65,
    "SLH-DSA-128s": _SLH_DSA_128s,
    "Ed25519+ML-DSA-65": _COMPOSITE,
    "XMSS-MT": _XMSS_MT,
    "LMS": _LMS,
}


def lookup(custody_shape: str, primitive: str) -> Dict[str, object]:
    """Return the fit cell for the (custody shape, primitive) pair.

    The cell carries the fit label, the two compatibility flags, and
    a one-line rationale derived from the primitive's state model
    and byte budget.
    """
    # EXERCISE: implement this function.
    #
    # Assert the shape and the primitive separately so a typo names which
    # argument was wrong, index MATRIX by primitive then by shape, and
    # return a flat dict carrying custody_shape, primitive, fit,
    # state_compatible, byte_compatible, and rationale. The cell's label was
    # already resolved when the module built the matrix; this function does
    # not re-derive it. Read the table before writing the return: the ECDSA
    # row is legacy in all four columns because it is the source of the
    # migration rather than a target, SLH-DSA-128s is marginal on the two
    # hot columns under its 7856-byte signature, and XMSS-MT and LMS are
    # unfit on multi-device-hot and multisig-cold because no one-time-key
    # index survives being coordinated across independent devices.
    #
    # Reference: Chapter 38, 'Pick the candidate per custody shape'
    #
    # Proved by:
    #   tests/ch38/test_custody_fit.py
    raise NotImplementedError("exercise: lookup")


def candidates_for_shape(custody_shape: str) -> List[Dict[str, object]]:
    """Return every primitive's fit cell for the named custody shape.

    The order matches PRIMITIVES so a chapter table renders
    deterministically.
    """
    assert custody_shape in CUSTODY_SHAPES, f"unknown custody shape: {custody_shape!r}"
    return [lookup(custody_shape, p) for p in PRIMITIVES]


def shapes_for_primitive(primitive: str) -> List[Dict[str, object]]:
    """Return every custody shape's fit cell for the named primitive.

    The order matches CUSTODY_SHAPES.
    """
    assert primitive in PRIMITIVES, f"unknown primitive: {primitive!r}"
    return [lookup(s, primitive) for s in CUSTODY_SHAPES]


def evaluate() -> List[Dict[str, object]]:
    """Flatten the full 6 by 4 matrix into a list of fit cells.

    Useful for the chapter's inline Block 1 pretty-print and for a
    test that asserts the deterministic order of candidates.
    """
    out: List[Dict[str, object]] = []
    for primitive in PRIMITIVES:
        for shape in CUSTODY_SHAPES:
            out.append(lookup(shape, primitive))
    return out
