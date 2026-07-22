# Book of PQC: companion code

Runnable implementations, exercise stubs, and tests for [*The Encryptorium Book of Post-Quantum Cryptography*](https://book.encryptorium.com). Post-quantum cryptography (PQC) is the set of algorithms built to stay secure against an adversary holding a large quantum computer.

The book's continuous integration (CI) runs the fenced Python blocks in the prose and compares each one's output against a `# ==>` expected-output marker. The exception is a block tagged `no-verify`, which CI skips; the book has two, both sketches not meant to run standalone. This repository holds the fuller implementations behind those blocks, a stubbed copy of each so you can write them yourself, and the pytest suites that check either one. Those suites include the Automated Cryptographic Validation Protocol (ACVP) vector comparisons published by the US National Institute of Standards and Technology (NIST) for ML-KEM and SLH-DSA, standardized as Federal Information Processing Standards (FIPS) 203 and 205.

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

No chapter has been released yet, so a fresh clone carries the environment scaffolding only. There is no `tests/`, `solutions/`, or `exercises/` directory, and every command in this section and the next reports `no tests ran` until the first chapter lands. See Release model below.

Once a chapter is published, run its suite from the repository root:

```
pytest tests/ch13
```

The suite defaults to the reference implementation, so a clone that has a chapter in it is green on the first run.

## Implementing a chapter yourself

```
PQC_IMPL=exercises pytest tests/ch13
```

Every stubbed function raises `NotImplementedError` until you write it, so the first run is red by design. Open `exercises/ch13-lamport/`, implement one function, run again. Each stub keeps the reference implementation's signature and docstring, and adds a contract block naming what it owes its caller, where the book covers it, and which test proves it.

`PQC_IMPL` accepts only `solutions` or `exercises`. A chapter with no stub package under `exercises/` stops at collection with a `ModuleNotFoundError`, because there is nothing to import.

Nothing is hidden: `solutions/` is in this clone. Reading it costs you the exercise, which is a trade only you can price.

## Troubleshooting

**"No module named 'numpy'" in a Part II chapter.** The venv is active but numpy was not installed. Run `pip install "numpy>=1.26"` inside the venv.

**Pytest reports "no tests ran".** Two causes. Either no chapter has been released yet, so there is no `tests/` directory to collect from (see Release model), or pytest was called from outside the repository root, since the chapter test directories are resolved relative to it.

**`python3 --version` reports 3.8 or 3.9.** Six of the reference packages annotate an optional argument with a PEP 604 union such as `bytes | None` and do not import `annotations` from `__future__`. On both versions the annotation is evaluated when the function is defined, so importing one of those modules raises `TypeError: unsupported operand type(s) for |` rather than a `SyntaxError`. The official installer at python.org bypasses a system package manager's pin.

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
