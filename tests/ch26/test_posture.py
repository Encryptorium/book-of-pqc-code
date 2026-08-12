"""Rotation and agility labelling (Chapter 26 lifecycle area, Exercise 3)."""

import pytest

from agility.posture import agility_property, agility_status, needs_rehash


# The four application-layer touchpoints of Chapter 25's mock application,
# carrying the two fields the labelling rule reads. Chapter 25's inventory
# records an `algorithm` for every touchpoint and a rotation policy for
# none, which is what makes the labels below all `partial`.
CH25_TOUCHPOINTS = [
    {"name": "tls_endpoint_api", "algorithm": "ECDHE-ECDSA-AES256-GCM-SHA384"},
    {"name": "jwt_signing", "algorithm": "RS256"},
    {"name": "password_hashing", "algorithm": "PBKDF2-HMAC-SHA256"},
    {"name": "webhook_hmac", "algorithm": "HMAC-SHA256"},
]


# --- needs_rehash: the lifecycle area's password case ---


def test_a_row_below_the_target_needs_rehashing():
    assert needs_rehash(600_000, 1_200_000) is True


def test_a_row_at_the_target_does_not():
    assert needs_rehash(1_200_000, 1_200_000) is False


def test_a_row_above_the_target_does_not():
    """A row can sit above the target after the target is lowered, and
    lowering an iteration count must never trigger a re-derivation that
    weakens the stored hash."""

    assert needs_rehash(2_000_000, 1_200_000) is False


def test_the_chapter_s_own_worked_numbers():
    """Chapter 25 deploys password_hashing at 600,000 iterations and
    Chapter 26 raises the question of moving to 1,200,000."""

    assert needs_rehash(600_000, 1_200_000) is True
    assert needs_rehash(1_200_000, 1_200_000) is False


# --- agility_status: the two-axis label ---


def test_both_axes_present_is_agile():
    assert agility_status({"algorithm": "HS256", "rotation_policy": "90d"}) == "agile"


def test_an_identifier_alone_is_partial():
    assert agility_status({"algorithm": "HS256"}) == "partial"


def test_a_rotation_policy_alone_is_partial():
    assert agility_status({"rotation_policy": "90d"}) == "partial"


def test_neither_axis_is_brittle():
    assert agility_status({"name": "unlabelled"}) == "brittle"


def test_an_empty_identifier_does_not_count_as_present():
    assert agility_status({"algorithm": "", "rotation_policy": ""}) == "brittle"


@pytest.mark.parametrize("touchpoint", CH25_TOUCHPOINTS, ids=lambda t: t["name"])
def test_every_ch25_touchpoint_labels_partial(touchpoint):
    """Chapter 25's inventory carries an algorithm identifier for every
    touchpoint and a rotation policy for none, so no touchpoint can reach
    `agile` and none falls to `brittle`."""

    assert agility_status(touchpoint) == "partial"


def test_no_ch25_touchpoint_reaches_agile():
    assert {agility_status(t) for t in CH25_TOUCHPOINTS} == {"partial"}


def test_the_property_uses_the_encryptorium_namespace():
    prop = agility_property({"algorithm": "HS256", "rotation_policy": "90d"})
    assert prop == {
        "name": "encryptorium:agility-status",
        "value": "agile",
    }


def test_the_property_carries_only_the_two_cyclonedx_keys():
    """A CycloneDX 1.6 `property` object is exactly `name` and `value`."""

    assert set(agility_property({"algorithm": "HS256"})) == {"name", "value"}
