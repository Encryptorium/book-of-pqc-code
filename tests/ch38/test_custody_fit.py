"""Tests for wallet_rotation.custody_fit.

Covers the 6 by 4 custody-shape by primitive matrix, the lookup
function, the per-shape and per-primitive convenience accessors,
and the legacy and unfit edge cases.
"""

from wallet_rotation import custody_fit


def test_custody_shapes_are_four():
    assert custody_fit.CUSTODY_SHAPES == (
        "single-device-hot",
        "multi-device-hot",
        "hardware-only-cold",
        "multisig-cold",
    )


def test_primitives_are_six():
    assert custody_fit.PRIMITIVES == (
        "ECDSA-secp256k1",
        "ML-DSA-65",
        "SLH-DSA-128s",
        "Ed25519+ML-DSA-65",
        "XMSS-MT",
        "LMS",
    )


def test_ecdsa_is_legacy_in_every_shape(custody_shapes):
    for shape in custody_shapes:
        cell = custody_fit.lookup(shape, "ECDSA-secp256k1")
        assert cell["fit"] == "legacy", shape


def test_ml_dsa_is_fit_in_every_shape(custody_shapes):
    for shape in custody_shapes:
        cell = custody_fit.lookup(shape, "ML-DSA-65")
        assert cell["fit"] == "fit", shape
        assert cell["state_compatible"] is True
        assert cell["byte_compatible"] is True


def test_slh_dsa_is_marginal_in_hot_and_fit_in_cold():
    # Per the chapter's planning notes: SLH-DSA-128s sigs are 7856
    # bytes per FIPS 205; this marginalizes the per-spend hot path
    # and is fit on the cold path.
    cell = custody_fit.lookup("single-device-hot", "SLH-DSA-128s")
    assert cell["fit"] == "marginal"
    cell = custody_fit.lookup("multi-device-hot", "SLH-DSA-128s")
    assert cell["fit"] == "marginal"
    cell = custody_fit.lookup("hardware-only-cold", "SLH-DSA-128s")
    assert cell["fit"] == "fit"
    cell = custody_fit.lookup("multisig-cold", "SLH-DSA-128s")
    assert cell["fit"] == "fit"


def test_slh_dsa_byte_compatible_reflects_hot_path_pressure():
    # The hot-shape SLH-DSA-128s cells are marginal because of the
    # 7856-byte signature pressure. The byte_compatible flag should
    # reflect that pressure (False on hot, True on cold), not contradict
    # the fit label.
    hot_cell = custody_fit.lookup("single-device-hot", "SLH-DSA-128s")
    assert hot_cell["byte_compatible"] is False
    hot_plus_cell = custody_fit.lookup("multi-device-hot", "SLH-DSA-128s")
    assert hot_plus_cell["byte_compatible"] is False
    cold_cell = custody_fit.lookup("hardware-only-cold", "SLH-DSA-128s")
    assert cold_cell["byte_compatible"] is True
    msig_cell = custody_fit.lookup("multisig-cold", "SLH-DSA-128s")
    assert msig_cell["byte_compatible"] is True


def test_composite_is_fit_in_every_shape(custody_shapes):
    for shape in custody_shapes:
        cell = custody_fit.lookup(shape, "Ed25519+ML-DSA-65")
        assert cell["fit"] == "fit", shape


def test_xmss_mt_is_unfit_under_multi_device_and_multisig():
    # Single-device-hot is marginal: consumer single-device hot wallets
    # typically lack the tamper-resistant non-volatile state plus
    # atomic-counter discipline NIST SP 800-208 effectively requires for
    # OTS-state safety. Hardware-only cold is fit because a secure
    # element gives the required state discipline.
    cell = custody_fit.lookup("single-device-hot", "XMSS-MT")
    assert cell["fit"] == "marginal"
    assert cell["state_compatible"] is True
    cell = custody_fit.lookup("hardware-only-cold", "XMSS-MT")
    assert cell["fit"] == "fit"

    cell = custody_fit.lookup("multi-device-hot", "XMSS-MT")
    assert cell["fit"] == "unfit"
    assert cell["state_compatible"] is False

    cell = custody_fit.lookup("multisig-cold", "XMSS-MT")
    assert cell["fit"] == "unfit"
    assert cell["state_compatible"] is False


def test_lms_matches_xmss_mt_shape_compatibility(custody_shapes):
    # LMS and XMSS-MT share the same stateful-hash shape compatibility.
    for shape in custody_shapes:
        xmss_cell = custody_fit.lookup(shape, "XMSS-MT")
        lms_cell = custody_fit.lookup(shape, "LMS")
        assert xmss_cell["fit"] == lms_cell["fit"], shape
        assert xmss_cell["state_compatible"] == lms_cell["state_compatible"], shape


def test_lookup_rejects_unknown_shape():
    try:
        custody_fit.lookup("single-device-cold", "ML-DSA-65")
    except AssertionError:
        return
    raise AssertionError("expected AssertionError for unknown shape")


def test_lookup_rejects_unknown_primitive():
    try:
        custody_fit.lookup("single-device-hot", "RSA-2048")
    except AssertionError:
        return
    raise AssertionError("expected AssertionError for unknown primitive")


def test_candidates_for_shape_orders_match_primitives_tuple(primitives):
    rows = custody_fit.candidates_for_shape("single-device-hot")
    assert [row["primitive"] for row in rows] == list(primitives)


def test_shapes_for_primitive_orders_match_shapes_tuple(custody_shapes):
    rows = custody_fit.shapes_for_primitive("ML-DSA-65")
    assert [row["custody_shape"] for row in rows] == list(custody_shapes)


def test_evaluate_returns_full_matrix_in_deterministic_order(primitives, custody_shapes):
    cells = custody_fit.evaluate()
    assert len(cells) == len(primitives) * len(custody_shapes)
    expected = [
        (p, s)
        for p in primitives
        for s in custody_shapes
    ]
    actual = [(c["primitive"], c["custody_shape"]) for c in cells]
    assert actual == expected


def test_each_cell_carries_rationale():
    for cell in custody_fit.evaluate():
        assert isinstance(cell["rationale"], str)
        assert len(cell["rationale"]) > 0


# The token that must appear in each primitive's rationale. Each is unique
# to its row, so the mapping pins the row to the primitive rather than to
# its position in MATRIX.
_ROW_TOKENS = {
    "ECDSA-secp256k1": "legacy baseline",
    "ML-DSA-65": "3309",
    "SLH-DSA-128s": "7856",
    "Ed25519+ML-DSA-65": "3373",
    "XMSS-MT": "hypertree",
    "LMS": "RFC 8554",
}


def test_rationales_are_bound_to_their_primitive(primitives):
    # Without this, the rows are permutable. Every other assertion in this
    # file reaches a cell through a fit label, a compatibility flag, or a
    # count, and four of the six rows are uniform, so swapping the
    # ML-DSA-65 and Ed25519+ML-DSA-65 rows in MATRIX leaves all of them
    # green while ML-DSA-65 claims the composite's 3373-byte figure and
    # the composite claims ML-DSA-65's 3309. The rationale is the only
    # field that distinguishes those two rows, so it is what has to be
    # pinned.
    for primitive in primitives:
        token = _ROW_TOKENS[primitive]
        for cell in custody_fit.shapes_for_primitive(primitive):
            assert token in cell["rationale"], (primitive, cell["custody_shape"])


def test_row_tokens_are_unique_to_one_primitive(primitives):
    # Guards the test above: a token that appeared in two rows would let a
    # swap of those two rows pass.
    for primitive in primitives:
        token = _ROW_TOKENS[primitive]
        carriers = {
            other
            for other in primitives
            if token in custody_fit.lookup("single-device-hot", other)["rationale"]
        }
        assert carriers == {primitive}, (token, carriers)


def test_unfit_cells_have_state_compatible_false():
    for cell in custody_fit.evaluate():
        if cell["fit"] == "unfit":
            assert cell["state_compatible"] is False or cell["byte_compatible"] is False


def test_marginal_cells_remain_state_compatible():
    # Marginal labels exist for byte-budget pressure, not state-management
    # break. A "marginal" cell whose state_compatible=False would mean a
    # state-broken scheme is "operationally viable with friction", which is
    # semantically wrong. This test guards the override logic.
    for cell in custody_fit.evaluate():
        if cell["fit"] == "marginal":
            assert cell["state_compatible"] is True
