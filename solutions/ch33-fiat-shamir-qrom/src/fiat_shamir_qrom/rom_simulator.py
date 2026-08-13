"""Classical random oracle simulator for Chapter 33.

A RandomOracle instance models an idealized hash function H with output
range ``[0, output_modulus)``. Queries are lazy-sampled: on first
classical query at input x, the oracle returns ``sha256(seed || x) mod
output_modulus`` and caches the result; on subsequent queries at the
same x the cached value is returned. A reprogram(x, value) method lets
a simulator preprogram the oracle at a selected point, provided x has
not yet been queried.

The reprogram-before-query invariant is the classical shadow of the
QROM restriction that the measure-and-reprogram reduction exploits.
In the quantum setting, if the adversary has already measured the
oracle response at x, reprogramming retroactively rewrites the
adversary's view and the reduction no longer simulates a valid ideal
oracle. Here, the ValueError is raised eagerly to make that boundary
observable in tests.

Parameters use the Chapter 32 toy-group modulus ``DEFAULT_OUTPUT = 1013``
by default, which lines up with the Schnorr challenge space in
``fiat_shamir``.
"""

from __future__ import annotations

import hashlib
from typing import Iterable


DEFAULT_OUTPUT = 1013


class RandomOracle:
    """Lazy-sampling classical random oracle with reprogramming.

    The oracle maintains a cache of queried inputs and a separate map
    of preprogrammed inputs. A query first consults the cache; then the
    programmed map (and caches the value); then lazy-samples via SHA-256
    and caches. The cache is write-once: once an input is cached, it
    cannot be reprogrammed.

    The query log records every query input in order, which the
    measure-and-reprogram scaffolding uses to pick a random query index
    after the adversary has run.
    """

    def __init__(self, output_modulus: int = DEFAULT_OUTPUT, seed: bytes = b"") -> None:
        if output_modulus <= 0:
            raise ValueError("output_modulus must be positive")
        self.output_modulus = output_modulus
        self.seed = seed
        self._cache: dict[bytes, int] = {}
        self._programmed: dict[bytes, int] = {}
        self._query_log: list[bytes] = []

    def query(self, x: bytes) -> int:
        """Query the oracle at classical input ``x``.

        Returns the cached value if ``x`` has been queried before; else
        the programmed value if ``x`` was preprogrammed; else a lazy-
        sampled uniform value derived from ``sha256(seed || x)``.
        """
        if not isinstance(x, (bytes, bytearray)):
            raise ValueError("query input must be bytes")
        self._query_log.append(bytes(x))
        if x in self._cache:
            return self._cache[x]
        if x in self._programmed:
            value = self._programmed[x]
        else:
            digest = hashlib.sha256(self.seed + bytes(x)).digest()
            value = int.from_bytes(digest, "big") % self.output_modulus
        self._cache[bytes(x)] = value
        return value

    def reprogram(self, x: bytes, value: int) -> None:
        """Program the oracle at ``x`` to respond with ``value``.

        Raises ValueError if ``x`` has already been queried (the oracle
        response at ``x`` has been observed, so reprogramming would
        retroactively rewrite it) or if ``value`` lies outside
        ``[0, output_modulus)``.
        """
        if not isinstance(x, (bytes, bytearray)):
            raise ValueError("reprogram input must be bytes")
        if x in self._cache:
            raise ValueError("cannot reprogram a queried point")
        if value < 0 or value >= self.output_modulus:
            raise ValueError("value outside oracle range")
        self._programmed[bytes(x)] = value

    def is_queried(self, x: bytes) -> bool:
        """Return True if ``x`` has been queried at least once."""
        return x in self._cache

    def is_programmed(self, x: bytes) -> bool:
        """Return True if ``x`` has been preprogrammed."""
        return x in self._programmed

    def cached_response(self, x: bytes) -> int:
        """Return the cached response at ``x`` without logging a query.

        Raises ValueError if ``x`` has not yet been queried.
        """
        if x not in self._cache:
            raise ValueError("input has not been queried")
        return self._cache[x]

    @property
    def queries(self) -> tuple[bytes, ...]:
        """Tuple of every query input, in the order it was made."""
        return tuple(self._query_log)

    def query_count(self) -> int:
        """Number of queries made, counting repeats."""
        return len(self._query_log)


def bulk_sample(
    oracle: RandomOracle, inputs: Iterable[bytes]
) -> list[int]:
    """Query the oracle at each input in ``inputs`` and return the list.

    A convenience wrapper used in tests. Each call appends to the query
    log; repeated inputs return the cached value.
    """
    return [oracle.query(x) for x in inputs]
