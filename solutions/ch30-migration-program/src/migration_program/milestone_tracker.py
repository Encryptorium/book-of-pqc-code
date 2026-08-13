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
    today_d = date.fromisoformat(today)
    parsed: list[tuple[Milestone, date]] = []
    for m in milestones:
        m_date = date.fromisoformat(m.target_date)
        parsed.append((m, m_date))

    total = len(parsed)
    completed = sum(1 for m, _ in parsed if m.completed)
    percent = (completed / total) if total > 0 else 0.0
    slipped = tuple(m for m, m_date in parsed if (not m.completed) and (m_date < today_d))
    return MilestoneReport(
        total=total,
        completed=completed,
        percent_complete=percent,
        slipped=slipped,
    )
