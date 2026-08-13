# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 29: PKI and code signing
# Section: "Code-signing pipeline"
# https://book.encryptorium.com/part-5-migration-deployment/ch29-pki-code-signing/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch29/03-read-counter.py

# Block 3: pedagogical slice of pki_migration.xmss_index.durable_xmss_sign (stdlib only).
import fcntl
import json
import os
from pathlib import Path

def _read_counter(counter_path):
    raw = counter_path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data.get("next_leaf"), int):
        raise RuntimeError(f"counter missing 'next_leaf' int at {counter_path}")
    if not isinstance(data.get("max_leaf"), int):
        raise RuntimeError(f"counter missing 'max_leaf' int at {counter_path}")
    return data

def _atomic_write(counter_path, state):
    tmp = counter_path.with_suffix(counter_path.suffix + ".tmp")
    raw = json.dumps({"next_leaf": state["next_leaf"],
                      "max_leaf": state["max_leaf"]}).encode("utf-8")
    with tmp.open("wb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, counter_path)
    dir_fd = os.open(str(counter_path.parent), os.O_DIRECTORY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)

def burn_next_leaf(counter_path, lock_path):
    # One LOCK_EX covers read, check, increment, write, fsync.
    with lock_path.open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        data = _read_counter(counter_path)
        if data["next_leaf"] >= data["max_leaf"]:
            raise RuntimeError(f"leaf exhaustion: all {data['max_leaf']} consumed")
        used = data["next_leaf"]
        _atomic_write(counter_path, {"next_leaf": used + 1, "max_leaf": data["max_leaf"]})
        return used

counter = Path("/tmp/ch29-xmss-counter.json")
lock = Path("/tmp/ch29-xmss-counter.lock")
counter.write_text(json.dumps({"next_leaf": 0, "max_leaf": 4}))

used = burn_next_leaf(counter, lock)
print("burned leaf:", used)
print("persisted:", json.loads(counter.read_text()))
counter.unlink()
lock.unlink()
# ==> burned leaf: 0
# ==> persisted: {'next_leaf': 1, 'max_leaf': 4}
