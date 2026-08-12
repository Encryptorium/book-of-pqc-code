"""The four-state approval registry of Chapter 26, Block 3, and the two
rules the chapter states in prose: state-to-operation and dated approval."""

import hashlib
import hmac

import pytest

from agility.registry import (
    POLICY,
    REGISTRY,
    STATES,
    approved_at,
    permits,
    sign,
)


def test_the_four_state_names_are_the_sp_800_131a_ones():
    assert set(STATES) == {
        "acceptable",
        "deprecated",
        "legacy-use",
        "disallowed",
    }


def test_every_registry_entry_carries_a_known_state():
    for alg, entry in REGISTRY.items():
        assert entry["state"] in STATES, alg


def test_every_policy_target_is_in_the_registry():
    for touchpoint, alg in POLICY.items():
        assert alg in REGISTRY, touchpoint


def test_sign_returns_the_identifier_alongside_the_mac():
    alg, sig = sign("webhook_hmac", b"key", b"body")
    assert alg == "HMAC-SHA256"
    assert len(sig) == 32


def test_sign_agrees_with_a_direct_hmac_call():
    _, sig = sign("webhook_hmac", b"key", b"body")
    assert sig == hmac.new(b"key", b"body", hashlib.sha256).digest()


def test_sign_uses_the_algorithm_the_policy_names_not_a_default():
    alg, sig = sign("internal_bus", b"key", b"body")
    assert alg == "HMAC-SHA512"
    assert len(sig) == 64


def test_sign_refuses_a_deprecated_algorithm():
    with pytest.raises(ValueError, match="HMAC-SHA1 is deprecated"):
        sign("legacy_connector", b"key", b"body")


def test_sign_refuses_a_disallowed_algorithm():
    POLICY["temp_md5"] = "HMAC-MD5"
    try:
        with pytest.raises(ValueError, match="HMAC-MD5 is disallowed"):
            sign("temp_md5", b"key", b"body")
    finally:
        del POLICY["temp_md5"]


# --- permits: the asymmetry that makes four states worth having ---


@pytest.mark.parametrize("operation", ["protect", "process"])
def test_acceptable_permits_everything(operation):
    assert permits("acceptable", operation) is True


@pytest.mark.parametrize("operation", ["protect", "process"])
def test_deprecated_still_permits_everything(operation):
    """Deprecated carries risk, not a prohibition. Block 3's signer
    refuses it as a local policy choice, which is stricter than the
    state itself requires."""

    assert permits("deprecated", operation) is True


def test_legacy_use_permits_processing_only():
    assert permits("legacy-use", "process") is True
    assert permits("legacy-use", "protect") is False


@pytest.mark.parametrize("operation", ["protect", "process"])
def test_disallowed_permits_nothing(operation):
    assert permits("disallowed", operation) is False


def test_permits_rejects_an_unknown_state():
    with pytest.raises(ValueError, match="unknown approval state"):
        permits("retired", "protect")


def test_permits_rejects_an_unknown_operation():
    with pytest.raises(ValueError, match="unknown operation"):
        permits("acceptable", "sign")


# --- approved_at: a list you cannot date is a list you cannot gate ---


ENTRY = {"effective": "2025-01-01", "expires": "2030-12-31"}


def test_a_date_inside_the_window_is_approved():
    assert approved_at(ENTRY, "2026-08-12") is True


def test_the_boundary_dates_are_inclusive():
    assert approved_at(ENTRY, "2025-01-01") is True
    assert approved_at(ENTRY, "2030-12-31") is True


def test_a_date_before_the_effective_date_is_not_approved():
    assert approved_at(ENTRY, "2024-12-31") is False


def test_a_date_after_the_expiry_date_is_not_approved():
    assert approved_at(ENTRY, "2031-01-01") is False


def test_an_entry_with_no_expiry_never_expires():
    assert approved_at({"effective": "2025-01-01"}, "2099-01-01") is True


def test_an_entry_with_no_dates_is_always_approved():
    """An undated entry is the brittle pattern: there is no moment at
    which it becomes wrong, so no CI gate can ever fail on it."""

    assert approved_at({}, "1999-01-01") is True
