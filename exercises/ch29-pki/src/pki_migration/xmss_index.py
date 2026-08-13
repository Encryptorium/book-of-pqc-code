"""Durable-counter wrapper around Ch 15 XMSS signing.

XMSS is stateful: reusing a leaf index degrades the one-time security
of the underlying WOTS+ key (NIST SP 800-208 section 9.1). The Ch 15
implementation tracks ``next_leaf`` and ``max_leaf`` in an
in-process dict. For deployment, the counter must survive process
restarts, must not be silently resettable, and must serialize
concurrent signers so that two processes cannot reserve the same
leaf.

This module persists the counter to a JSON file. The
``durable_xmss_sign`` entry point holds a single POSIX exclusive
lock on a sibling lock file across the entire
read-check-increment-write sequence, then runs the WOTS+ signing
step. A crash between counter persistence and WOTS+ signing wastes a
leaf but cannot reuse one; a second concurrent signer blocks at
``LOCK_EX`` until the first releases, then reads the
already-incremented counter and reserves the next index.

The POSIX file lock is the pedagogical simplification. SP 800-208
section 8.1 validates key and signature generation only inside a
hardware cryptographic module at FIPS 140 Level 3 physical security
or higher, and section 9.1 recommends a hardware monotonic counter
where one is available. A serializable database transaction is a
weaker engineering alternative that the standard does not sanction.

Public API:

- ``initialize_counter(path, max_leaf)``: create a fresh counter
  file. Raises ``RuntimeError`` if the file already exists.
- ``read_counter(path) -> dict``: parse the counter file under a
  shared lock; raises ``RuntimeError`` if absent or corrupt.
- ``durable_xmss_sign(counter_path, ...) -> xmss signature``:
  reserve, persist, sign under a single exclusive lock. Raises
  ``RuntimeError`` for any precondition failure (missing file,
  corrupt file, exhausted counter).
"""

import fcntl
import json
import os
import sys
from pathlib import Path

_XMSS_SRC = Path(__file__).resolve().parents[3] / "ch15-xmss" / "src"
if str(_XMSS_SRC) not in sys.path:
    sys.path.insert(0, str(_XMSS_SRC))

from wots_xmss import xmss_sign  # noqa: E402


_COUNTER_KEYS = ("next_leaf", "max_leaf")


def _lock_path_for(counter_path: Path) -> Path:
    """Sibling lock file for ``counter_path``; created on first use."""
    return counter_path.with_name(counter_path.name + ".lock")


def _parse_counter_bytes(raw: bytes, path: Path) -> dict:
    """Parse counter JSON bytes; raise ``RuntimeError`` on any malformed input."""
    try:
        data = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise RuntimeError(f"corrupt counter file at {path}: {exc}")
    for key in _COUNTER_KEYS:
        if key not in data or not isinstance(data[key], int):
            raise RuntimeError(
                f"counter file at {path} missing or malformed {key!r}"
            )
    return {"next_leaf": data["next_leaf"], "max_leaf": data["max_leaf"]}


def _read_counter_unlocked(path: Path) -> dict:
    """Read and parse the counter file without taking any lock.

    Intended for callers that already hold the sibling lock file's
    ``LOCK_EX``. External callers should use :func:`read_counter`,
    which takes its own shared lock.
    """
    if not path.exists():
        raise RuntimeError(f"counter file missing at {path}")
    return _parse_counter_bytes(path.read_bytes(), path)


def read_counter(path: Path) -> dict:
    """Read the counter file at ``path`` under a shared lock.

    Raises ``RuntimeError`` if the file is absent, cannot be decoded,
    or lacks the required integer keys.
    """
    if not path.exists():
        raise RuntimeError(f"counter file missing at {path}")
    with path.open("rb") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        raw = f.read()
    return _parse_counter_bytes(raw, path)


def _write_counter_atomic(path: Path, state: dict) -> None:
    """Atomically persist ``state`` to ``path`` via temp-file rename.

    Writes through a temp file in the same directory, fsyncs the temp
    file, ``os.replace``s into the destination, then fsyncs the
    parent directory so the rename itself is durable across crashes.
    Caller is expected to hold an exclusive lock on the sibling lock
    file.
    """
    # EXERCISE: implement this function.
    #
    # A half-written counter is an unreadable counter, and a signer that
    # cannot read its counter is a signer that might restart at zero. Write
    # the JSON to a temp file in the same directory, flush it, fsync its
    # descriptor, then os.replace it over the destination: rename within a
    # directory is atomic, so a concurrent reader sees either the whole old
    # file or the whole new one. Finish by opening the parent directory with
    # O_DIRECTORY and fsyncing that too, because the rename is a directory
    # entry and is not durable across a crash until the directory itself is
    # synced. The caller is expected to already hold the exclusive lock.
    #
    # Reference: Chapter 29, 'Code-signing pipeline' (NIST SP 800-208 sections 8.1 and 9.1)
    #
    # Proved by:
    #   tests/ch29/test_xmss_durable_counter.py
    raise NotImplementedError("exercise: _write_counter_atomic")


def initialize_counter(path: Path, max_leaf: int) -> None:
    """Create a fresh counter file at ``path`` with ``next_leaf = 0``.

    Raises ``RuntimeError`` if a file already exists (refusing to
    overwrite protects against accidental reset).
    """
    # EXERCISE: implement this function.
    #
    # Create the counter file with next_leaf at 0 and the caller's max_leaf,
    # through the atomic write. Refuse with RuntimeError if a file is
    # already there. Overwriting would rewind the counter and reissue leaves
    # that have already signed, which is the precise failure this module
    # exists to prevent, so the guard is the feature rather than defensive
    # habit.
    #
    # Reference: Chapter 29, 'Code-signing pipeline' (NIST SP 800-208 sections 8.1 and 9.1)
    #
    # Proved by:
    #   tests/ch29/test_xmss_durable_counter.py
    raise NotImplementedError("exercise: initialize_counter")


def _reserve_next_leaf(counter_path: Path) -> dict:
    """Atomically reserve the next leaf under a sibling-file ``LOCK_EX``.

    Returns the pre-increment counter state ``{"next_leaf", "max_leaf"}``.
    The on-disk counter is advanced to ``next_leaf + 1`` before this
    function returns. Raises ``RuntimeError`` if the counter is
    missing, corrupt, or already exhausted.
    """
    # EXERCISE: implement this function.
    #
    # One LOCK_EX must cover read, exhaustion check, increment, and write.
    # Open the sibling lock path with 'a+b' so it is created on first use,
    # flock it exclusively, then read the counter through
    # _read_counter_unlocked rather than read_counter, which would try to
    # take its own lock. Raise RuntimeError naming exhaustion once next_leaf
    # has reached max_leaf. Otherwise persist next_leaf + 1 and return the
    # pre-increment state. Persisting before the caller signs is the
    # ordering that matters: a crash at this point wastes a leaf, while
    # persisting after signing would reuse one. A second signer blocks at
    # the flock until the first releases, then reads the already-advanced
    # counter and reserves the next index.
    #
    # Reference: Chapter 29, 'Code-signing pipeline' (NIST SP 800-208 sections 8.1 and 9.1)
    #
    # Proved by:
    #   tests/ch29/test_xmss_durable_counter.py
    raise NotImplementedError("exercise: _reserve_next_leaf")


def durable_xmss_sign(
    counter_path: Path,
    all_sk: list,
    all_pk: list,
    tree: list,
    message: bytes,
    seed: bytes,
    w: int = 16,
):
    """Sign ``message`` with XMSS while enforcing a durable counter.

    1. Acquire an exclusive lock on the sibling lock file.
    2. Read the counter; raise ``RuntimeError`` if exhausted.
    3. Persist the incremented counter (atomic write + parent-dir fsync).
    4. Release the lock; call ``xmss_sign`` with an ephemeral state at
       the pre-increment leaf index.

    A crash between steps 3 and 4 wastes a leaf but never reuses one;
    a second concurrent signer blocks at step 1 until the first
    releases.

    Returns the ``xmss_sign`` tuple: ``(wots_sig, wots_pk, path, leaf_index)``.
    """
    # EXERCISE: implement this function.
    #
    # Reserve and persist first, sign second. Call _reserve_next_leaf for
    # the pre-increment state, build a throwaway state dict carrying that
    # leaf index and max_leaf, and pass it to Ch 15's xmss_sign. The state
    # handed to xmss_sign is ephemeral on purpose: the file is the
    # authoritative counter, and an in-process dict must never be the thing
    # that survives the call. Signing runs outside the lock because it never
    # touches the counter. Return xmss_sign's tuple unchanged.
    #
    # Reference: Chapter 29, 'Code-signing pipeline'
    #
    # Proved by:
    #   tests/ch29/test_xmss_durable_counter.py
    raise NotImplementedError("exercise: durable_xmss_sign")
