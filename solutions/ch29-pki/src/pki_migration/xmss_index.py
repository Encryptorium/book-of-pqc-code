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
    tmp = path.with_suffix(path.suffix + ".tmp")
    raw = json.dumps(
        {"next_leaf": state["next_leaf"], "max_leaf": state["max_leaf"]}
    ).encode("utf-8")
    with tmp.open("wb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    dir_fd = os.open(str(path.parent), os.O_DIRECTORY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)


def initialize_counter(path: Path, max_leaf: int) -> None:
    """Create a fresh counter file at ``path`` with ``next_leaf = 0``.

    Raises ``RuntimeError`` if a file already exists (refusing to
    overwrite protects against accidental reset).
    """
    if path.exists():
        raise RuntimeError(f"counter file already exists at {path}; refusing to overwrite")
    _write_counter_atomic(path, {"next_leaf": 0, "max_leaf": max_leaf})


def _reserve_next_leaf(counter_path: Path) -> dict:
    """Atomically reserve the next leaf under a sibling-file ``LOCK_EX``.

    Returns the pre-increment counter state ``{"next_leaf", "max_leaf"}``.
    The on-disk counter is advanced to ``next_leaf + 1`` before this
    function returns. Raises ``RuntimeError`` if the counter is
    missing, corrupt, or already exhausted.
    """
    lock_path = _lock_path_for(counter_path)
    with lock_path.open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        persisted = _read_counter_unlocked(counter_path)
        if persisted["next_leaf"] >= persisted["max_leaf"]:
            raise RuntimeError(
                f"leaf exhaustion: all {persisted['max_leaf']} leaves consumed "
                f"per {counter_path}"
            )
        _write_counter_atomic(
            counter_path,
            {
                "next_leaf": persisted["next_leaf"] + 1,
                "max_leaf": persisted["max_leaf"],
            },
        )
        return persisted


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
    persisted = _reserve_next_leaf(counter_path)
    ephemeral = {
        "next_leaf": persisted["next_leaf"],
        "max_leaf": persisted["max_leaf"],
    }
    return xmss_sign(all_sk, all_pk, tree, ephemeral, message, seed, w=w)
