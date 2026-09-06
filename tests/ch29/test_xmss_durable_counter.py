"""Tests for ``pki_migration.xmss_index``.

The durable-counter wrapper persists ``next_leaf`` to disk before
calling Ch 15's ``xmss_sign``. These tests exercise: a missing
counter file, a corrupt counter file, roundtrip sign/verify,
restart semantics (a fresh process with the same counter file
refuses to reuse leaves), and leaf exhaustion.
"""

import json

import pytest

from pki_migration.xmss_index import (
    durable_xmss_sign,
    initialize_counter,
    read_counter,
)
from wots_xmss import xmss_keygen, xmss_verify


_SEED = b"ch29-xmss-test-seed"


@pytest.fixture
def xmss_keys():
    """Generate a small XMSS tree (4 leaves) for fast tests."""
    all_sk, all_pk, tree, root_hash, _state = xmss_keygen(
        d=2, sk_seed=_SEED, pk_seed=_SEED
    )
    return all_sk, all_pk, tree, root_hash


def test_initialize_counter_creates_file(tmp_path) -> None:
    counter = tmp_path / "counter.json"
    initialize_counter(counter, max_leaf=4)
    assert counter.exists()
    data = read_counter(counter)
    assert data == {"next_leaf": 0, "max_leaf": 4}


def test_initialize_refuses_to_overwrite(tmp_path) -> None:
    counter = tmp_path / "counter.json"
    initialize_counter(counter, max_leaf=4)
    with pytest.raises(RuntimeError, match="already exists"):
        initialize_counter(counter, max_leaf=4)


def test_read_counter_missing_raises(tmp_path) -> None:
    counter = tmp_path / "nope.json"
    with pytest.raises(RuntimeError, match="missing"):
        read_counter(counter)


def test_read_counter_corrupt_raises(tmp_path) -> None:
    counter = tmp_path / "corrupt.json"
    counter.write_bytes(b"not-json-at-all")
    with pytest.raises(RuntimeError, match="corrupt"):
        read_counter(counter)


def test_read_counter_malformed_missing_key_raises(tmp_path) -> None:
    counter = tmp_path / "malformed.json"
    counter.write_text(json.dumps({"next_leaf": 0}))
    with pytest.raises(RuntimeError, match="max_leaf"):
        read_counter(counter)


def test_read_counter_wrong_type_raises(tmp_path) -> None:
    counter = tmp_path / "wrong.json"
    counter.write_text(json.dumps({"next_leaf": "0", "max_leaf": 4}))
    with pytest.raises(RuntimeError, match="next_leaf"):
        read_counter(counter)


def test_sign_without_counter_raises(tmp_path, xmss_keys) -> None:
    all_sk, all_pk, tree, _root = xmss_keys
    counter = tmp_path / "absent.json"
    with pytest.raises(RuntimeError, match="missing"):
        durable_xmss_sign(counter, all_sk, all_pk, tree, b"msg", _SEED)


def test_sign_roundtrip_and_persists_counter(tmp_path, xmss_keys) -> None:
    all_sk, all_pk, tree, root_hash = xmss_keys
    counter = tmp_path / "counter.json"
    initialize_counter(counter, max_leaf=4)
    wots_sig, wots_pk, path, leaf_index = durable_xmss_sign(
        counter, all_sk, all_pk, tree, b"hello", _SEED
    )
    assert leaf_index == 0
    assert xmss_verify(root_hash, b"hello", wots_sig, wots_pk, path, leaf_index, _SEED)
    assert read_counter(counter) == {"next_leaf": 1, "max_leaf": 4}


def test_restart_does_not_reuse_leaf(tmp_path, xmss_keys) -> None:
    """Second sign against the same counter file uses leaf 1, not leaf 0."""
    all_sk, all_pk, tree, root_hash = xmss_keys
    counter = tmp_path / "counter.json"
    initialize_counter(counter, max_leaf=4)
    _sig1 = durable_xmss_sign(counter, all_sk, all_pk, tree, b"m1", _SEED)
    _sig2 = durable_xmss_sign(counter, all_sk, all_pk, tree, b"m2", _SEED)
    assert _sig1[3] == 0
    assert _sig2[3] == 1
    assert read_counter(counter)["next_leaf"] == 2


def test_counter_exhaustion_raises(tmp_path, xmss_keys) -> None:
    all_sk, all_pk, tree, _root = xmss_keys
    counter = tmp_path / "counter.json"
    initialize_counter(counter, max_leaf=4)
    for i in range(4):
        durable_xmss_sign(counter, all_sk, all_pk, tree, f"m{i}".encode(), _SEED)
    with pytest.raises(RuntimeError, match="exhaustion"):
        durable_xmss_sign(counter, all_sk, all_pk, tree, b"m-extra", _SEED)


def test_max_leaf_zero_exhausts_on_first_sign(tmp_path, xmss_keys) -> None:
    """A counter provisioned with max_leaf=0 refuses every sign."""
    all_sk, all_pk, tree, _root = xmss_keys
    counter = tmp_path / "counter.json"
    initialize_counter(counter, max_leaf=0)
    with pytest.raises(RuntimeError, match="exhaustion"):
        durable_xmss_sign(counter, all_sk, all_pk, tree, b"first", _SEED)


def test_counter_persists_across_reads(tmp_path, xmss_keys) -> None:
    """The first sign advances the on-disk counter; reading it after
    the sign (as a 'restart' would) shows the advanced value."""
    all_sk, all_pk, tree, _root = xmss_keys
    counter = tmp_path / "counter.json"
    initialize_counter(counter, max_leaf=4)
    durable_xmss_sign(counter, all_sk, all_pk, tree, b"first", _SEED)
    # Simulate a fresh process: re-read the counter file without the
    # in-process state from the sign call.
    on_disk = read_counter(counter)
    assert on_disk["next_leaf"] == 1
    # A subsequent sign picks up at leaf 1, not leaf 0.
    _sig, _pk, _path, leaf = durable_xmss_sign(
        counter, all_sk, all_pk, tree, b"second", _SEED
    )
    assert leaf == 1


# Round-10 P1-02: initialization must take the same sibling LOCK_EX the
# signer takes. Both tests below failed on the package as it stood before
# the fix (the first at ``assert not done.wait(0.3)``, the second at
# ``assert "already exists" in ...`` because both initializers wrote).
# Each worker thread records any exception it did not expect, and the
# main thread re-raises the first one, so a crash inside a thread (the
# stub tree's NotImplementedError included) fails the test by its own
# type rather than by a downstream assertion.

import fcntl
import threading
from unittest.mock import patch

from pki_migration import xmss_index as m


def test_initialize_holds_the_reservation_lock(tmp_path) -> None:
    """A holder of the sibling LOCK_EX blocks initialize_counter until release."""
    counter = tmp_path / "counter.json"
    lock_path = m._lock_path_for(counter)
    done = threading.Event()
    errors = []

    def init():
        try:
            m.initialize_counter(counter, max_leaf=4)
            done.set()
        except BaseException as exc:  # noqa: BLE001 (re-raised below)
            errors.append(exc)

    with lock_path.open("a+b") as held:
        fcntl.flock(held.fileno(), fcntl.LOCK_EX)
        t = threading.Thread(target=init)
        t.start()
        assert not done.wait(0.3), "initialize_counter ran while another process held the lock"
        assert not counter.exists()
    t.join(5)
    if errors:
        raise errors[0]
    assert done.is_set()
    assert m.read_counter(counter) == {"next_leaf": 0, "max_leaf": 4}


def test_late_initializer_cannot_rewind_a_reserved_counter(tmp_path) -> None:
    """Round-10 P1-02: init A passes its check, init B creates, a signer reserves 0,
    A resumes. Exactly one initializer writes; the other refuses; no leaf is reused."""
    counter = tmp_path / "counter.json"
    at_write = threading.Event()
    resume = threading.Event()
    original = m._write_counter_atomic
    outcome = {}
    errors = []

    def pausing_write(path, state):
        if threading.current_thread().name == "slow-init":
            at_write.set()
            resume.wait(5)
        return original(path, state)

    def run_init(key):
        try:
            m.initialize_counter(counter, max_leaf=8)
            outcome[key] = "wrote"
        except RuntimeError as exc:
            if "already exists" not in str(exc):
                errors.append(exc)
            outcome[key] = str(exc)
        except BaseException as exc:  # noqa: BLE001 (re-raised below)
            errors.append(exc)

    with patch.object(m, "_write_counter_atomic", pausing_write):
        slow = threading.Thread(name="slow-init", target=run_init, args=("slow",))
        slow.start()
        fast_done = threading.Event()

        def fast_init():
            run_init("fast")
            fast_done.set()

        at_write.wait(2)
        fast = threading.Thread(target=fast_init)
        fast.start()
        fast_ran_concurrently = fast_done.wait(0.3)
        resume.set()
        slow.join(5)
        fast.join(5)

    if errors:
        raise errors[0]
    assert sorted([outcome["slow"], outcome["fast"]])[1] == "wrote"
    assert "already exists" in min(outcome["slow"], outcome["fast"])
    assert not fast_ran_concurrently
    first = m._reserve_next_leaf(counter)["next_leaf"]
    second = m._reserve_next_leaf(counter)["next_leaf"]
    assert (first, second) == (0, 1)


def test_read_counter_needs_no_write_access(tmp_path) -> None:
    """Round-10 P1-02 follow-up (Codex gate): a read-only auditor can still read.
    The shared lock must be taken on a read-only descriptor; opening the sibling
    lock file for append would need write permission and may create a file."""
    import os

    counter = tmp_path / "counter.json"
    m.initialize_counter(counter, max_leaf=4)
    lock_path = m._lock_path_for(counter)
    assert lock_path.exists()
    old_lock, old_dir = lock_path.stat().st_mode, tmp_path.stat().st_mode
    os.chmod(lock_path, 0o444)
    os.chmod(tmp_path, 0o555)
    try:
        assert m.read_counter(counter) == {"next_leaf": 0, "max_leaf": 4}
    finally:
        os.chmod(tmp_path, old_dir)
        os.chmod(lock_path, old_lock)
