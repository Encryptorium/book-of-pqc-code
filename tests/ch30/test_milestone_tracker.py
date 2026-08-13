"""Tests for ``migration_program.milestone_tracker``."""

import pytest

from migration_program import Milestone, MilestoneReport, report


def test_empty_list_reports_zero() -> None:
    r = report([], "2026-04-17")
    assert isinstance(r, MilestoneReport)
    assert r.total == 0
    assert r.completed == 0
    assert r.percent_complete == 0.0
    assert r.slipped == ()


def test_single_completed_milestone() -> None:
    ms = [Milestone(name="cbom_complete", target_date="2026-12-31", completed=True)]
    r = report(ms, "2026-04-17")
    assert r.total == 1
    assert r.completed == 1
    assert r.percent_complete == 1.0
    assert r.slipped == ()


def test_single_pending_future_milestone() -> None:
    ms = [Milestone(name="first_wave", target_date="2028-12-31", completed=False)]
    r = report(ms, "2026-04-17")
    assert r.total == 1
    assert r.completed == 0
    assert r.percent_complete == 0.0
    assert r.slipped == ()  # not slipped yet; target is in the future


def test_slipped_milestone_flagged() -> None:
    ms = [Milestone(name="owners_assigned", target_date="2025-12-31", completed=False)]
    r = report(ms, "2026-04-17")
    assert r.slipped == tuple(ms)
    assert r.completed == 0


def test_full_program_mix(program_milestones: list[Milestone]) -> None:
    r = report(program_milestones, "2026-04-17")
    assert r.total == 4
    assert r.completed == 2
    assert r.percent_complete == 0.5
    # Only the past-date incomplete one is slipped.
    slipped_names = [m.name for m in r.slipped]
    assert slipped_names == ["owners_assigned"]


def test_same_day_target_not_slipped() -> None:
    # A target on today's date is not yet slipped.
    ms = [Milestone(name="today", target_date="2026-04-17", completed=False)]
    r = report(ms, "2026-04-17")
    assert r.slipped == ()


def test_malformed_today_rejected() -> None:
    with pytest.raises(ValueError):
        report([], "2026/04/17")


def test_malformed_target_date_rejected() -> None:
    ms = [Milestone(name="bad", target_date="April 17, 2026", completed=False)]
    with pytest.raises(ValueError):
        report(ms, "2026-04-17")


def test_all_completed_never_slipped() -> None:
    ms = [
        Milestone(name="a", target_date="2020-01-01", completed=True),
        Milestone(name="b", target_date="2021-01-01", completed=True),
    ]
    r = report(ms, "2026-04-17")
    assert r.slipped == ()
    assert r.percent_complete == 1.0
