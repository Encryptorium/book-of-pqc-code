"""Milestone tracker.

Reads a list of dated milestones and a current date; reports
percentage complete and a list of slipped milestones. A slipped
milestone is one whose target date has passed and that has not been
marked complete.

Dates are ISO ``YYYY-MM-DD`` strings, parsed by
``datetime.date.fromisoformat``. A malformed date raises ``ValueError``
from the standard library. An empty milestone list reports zero total
and a ``0.0`` completion fraction; the slipped list is empty.

The tracker does not decide which milestones belong to which program
phase. That coupling is a policy choice; the tracker is deliberately
phase-agnostic so a program lead can combine it with the
``phase_gate`` module or drive it from an external schedule.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Milestone:
    """A single program milestone."""

    name: str
    target_date: str
    completed: bool


@dataclass(frozen=True)
class MilestoneReport:
    """Program-wide milestone report."""

    total: int
    completed: int
    percent_complete: float
    slipped: tuple[Milestone, ...]


def report(milestones: Sequence[Milestone], today: str) -> MilestoneReport:
    """Compute a percentage-complete summary and slipped list.

    ``today`` is an ISO ``YYYY-MM-DD`` string. Each milestone's
    ``target_date`` is validated with ``date.fromisoformat`` before
    comparison; a malformed date surfaces the standard-library
    ``ValueError``.
    """
    # EXERCISE: implement this function.
    #
    # Parse today and every milestone's target_date with date.fromisoformat,
    # so a malformed date surfaces the standard library's ValueError instead
    # of being compared as a string. Percent complete is the completed count
    # over the total, with an empty list reporting 0.0 rather than dividing
    # by zero. A milestone is slipped when it is not complete and its target
    # date is strictly earlier than today, so a target falling on today's
    # date is not yet slipped. Keep the input order in the slipped tuple;
    # the tracker reports, it does not prioritise.
    #
    # Reference: Chapter 30, 'End-of-migration and classical deprecation (2035+)'
    #
    # Proved by:
    #   tests/ch30/test_milestone_tracker.py
    raise NotImplementedError("exercise: report")
