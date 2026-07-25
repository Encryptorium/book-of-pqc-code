"""Chapter 1: the classical factoring baseline behind the quantum threat.

One module, ``factoring``, with the two trial-division functions the chapter
and its exercise 2 build:

- ``factor_trial_division``: return the factor pair of a composite, or None.
- ``factor_trial_division_counted``: the same, plus the number of candidate
  divisions the search performed.

The package is stdlib-only. No cryptographic code lives here; Chapter 1
implements no scheme. It implements the attack whose cost the rest of the book
is a response to.
"""

from .factoring import factor_trial_division, factor_trial_division_counted

__all__ = [
    "factor_trial_division",
    "factor_trial_division_counted",
]
