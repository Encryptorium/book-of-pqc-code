# Book of PQC: companion code

Runnable implementations and tests for [*The Encryptorium Book of Post-Quantum Cryptography*](https://book.encryptorium.com).

Every code block in the book runs and is checked in CI against a `# ==>` expected-output marker. This repository holds the fuller implementations behind those blocks: a standalone Python package per chapter, plus the pytest suites that check them, including the NIST ACVP vector comparisons for ML-KEM (FIPS 203) and SLH-DSA (FIPS 205).

## Release model

The book publishes one chapter at a time. A chapter's code lands here when that chapter is released, not before. The contents of this repository therefore track the published book rather than the working draft, and a reader can assume that anything present here belongs to a chapter that has cleared review.

**Chapters released so far: none.** The book is in editorial review. This repository currently carries the environment scaffolding only.

## Layout

Once chapters begin landing:

- `code/chNN-<slug>/`: a standalone Python package for that chapter
- `tests/chNN/`: the pytest suite for that chapter, including vector comparisons where the chapter has them

The chapters draw pedagogical slices from these packages. Code in the book is a readable excerpt; code here is the fuller version it was cut from.

## Running the code

CPython 3.10 or newer. The lattice chapters (7 through 12) also need NumPy 1.26 or newer; every other chapter runs against the standard library alone.

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-ci.txt
pytest tests/
```

Appendix C of the book documents the environment contract in full, including the per-chapter package installs.

## What this repository is not

It does not contain the book's prose, figures, or exercise solutions. Those live at [book.encryptorium.com](https://book.encryptorium.com), where the solutions are published as Appendix D alongside each released chapter.

## License

MIT, see `LICENSE`. The book's prose is licensed separately under CC BY-SA 4.0.

## Reporting a problem

The book makes two claims a reader can check: every algorithm runs, and every claim is sourced. A violation of either is a bug. Open an issue here, or write to <contact@encryptorium.com>.
