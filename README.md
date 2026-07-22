# Book of PQC: companion code

Runnable implementations, exercise stubs, and tests for [*The Encryptorium Book of Post-Quantum Cryptography*](https://book.encryptorium.com).

Every code block in the book runs and is checked in CI against a `# ==>` expected-output marker. This repository holds the fuller implementations behind those blocks, a stubbed copy of each so you can write them yourself, and the pytest suites that check either one. Those suites include the NIST Automated Cryptographic Validation Protocol (ACVP) vector comparisons for ML-KEM (FIPS 203) and SLH-DSA (FIPS 205).

## Layout

- `solutions/chNN-<slug>/`: the reference implementation for one chapter, as a standalone Python package
- `exercises/chNN-<slug>/`: the same package with the functions that chapter teaches replaced by stubs
- `tests/chNN/`: the pytest suite, which runs against either tree

The chapters draw pedagogical slices from `solutions/`. Code in the book is a readable excerpt; code here is the fuller version it was cut from.

## Setup

CPython 3.10 or newer. The lattice chapters (7 through 11) also need NumPy 1.26 or newer; every other chapter runs against the standard library alone.

```
git clone https://github.com/Encryptorium/book-of-pqc-code.git
cd book-of-pqc-code
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-ci.txt
pip install pytest
```

On Windows PowerShell the activation line is `.venv\Scripts\Activate.ps1`.

Pytest is not declared as a dependency of any chapter package, because the chapters' runtime code never imports it. Install it once into the venv, as above.

There is no per-chapter install step. Each `tests/chNN/conftest.py` puts the selected tree's `src/` directory at the front of `sys.path`, so the suite imports the package straight out of the clone.

## Running the tests

```
pytest tests/ch13
```

The suite defaults to the reference implementation, so a fresh clone is green.

## Implementing a chapter yourself

```
PQC_IMPL=exercises pytest tests/ch13
```

Every stubbed function raises `NotImplementedError` until you write it, so the first run is red by design. Open `exercises/ch13-lamport/`, implement one function, run again. Each stub keeps the reference implementation's signature and docstring, and adds a contract block naming what it owes its caller, where the book covers it, and which test proves it.

`PQC_IMPL` accepts only `solutions` or `exercises`. A chapter with no stub package under `exercises/` stops at collection with a `ModuleNotFoundError`, because there is nothing to import.

Nothing is hidden: `solutions/` is in this clone. Reading it costs you the exercise, which is a trade only you can price.

## Troubleshooting

**"No module named 'numpy'" in a Part II chapter.** The venv is active but numpy was not installed. Run `pip install "numpy>=1.26"` inside the venv.

**Pytest reports "no tests ran".** Check you are in the repository root; the chapter test directories are resolved relative to it.

**`python3 --version` reports 3.8 or 3.9.** Several chapters use `match` statements, which raise `SyntaxError` below 3.10. The official installer at python.org bypasses a system package manager's pin.

**The venv activates but `which python` still points at the system CPython.** The shell cached the pre-venv path. Open a new shell, `cd` in, activate again.

Appendix C of the book covers the environment contract in full.

## Release model

The book publishes one chapter at a time, and a chapter's code publishes with it. This repository tracks the published book rather than the working draft, so anything present here belongs to a chapter that has cleared review. Expect it to grow as the book does.

**Chapters released so far: none.** The book is in editorial review. This repository currently carries the environment scaffolding only, so the `tests/ch13` commands above are what to run once Chapter 13 lands.

## What this repository is not

It does not contain the book's prose or figures. Those live at [book.encryptorium.com](https://book.encryptorium.com), where the worked solutions to the numbered exercises are published as Appendix D alongside each released chapter.

## License

MIT, see `LICENSE`. The book's prose is licensed separately under CC BY-SA 4.0.

## Reporting a problem

The book makes two claims a reader can check: every algorithm runs, and every claim is sourced. A violation of either is a bug. Open an issue here, or write to <contact@encryptorium.com>.
