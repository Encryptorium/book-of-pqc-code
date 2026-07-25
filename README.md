# Book of PQC: companion code

Every line of code in [*The Encryptorium Book of Post-Quantum Cryptography*](https://book.encryptorium.com), in a form you can run. Post-quantum cryptography (PQC) is the set of algorithms built to stay secure against an adversary holding a large quantum computer.

The book's continuous integration (CI) runs the fenced Python blocks in the prose and compares each one's output against a `# ==>` expected-output marker. The exception is a block tagged `no-verify`, which CI skips; the book has two, both sketches not meant to run standalone. This repository holds those blocks as files, the fuller implementations behind them, a stubbed copy of each so you can write them yourself, and the pytest suites that check either one. Those suites include the Automated Cryptographic Validation Protocol (ACVP) vector comparisons published by the US National Institute of Standards and Technology (NIST) for ML-KEM and SLH-DSA, standardized as Federal Information Processing Standards (FIPS) 203 and 205.

## Layout

Four trees, each with one job.

- `chapter-code/chNN/`: every Python block that chapter prints, one file each. Generated from the chapter text, so what you run is what the page shows.
- `solutions/chNN-<slug>/`: the reference implementation for one chapter, as a standalone Python package
- `exercises/chNN-<slug>/`: the same package with the functions that chapter teaches replaced by stubs
- `tests/chNN/`: the pytest suite, which runs against either package tree

The chapters draw pedagogical slices from `solutions/`. Code in the book is a readable excerpt; code here is the fuller version it was cut from. `chapter-code/` is the excerpt itself, byte for byte.

## What to run

| You want to | Go to |
|---|---|
| run a listing exactly as the page prints it | `python3 chapter-code/ch01/01-factor-trial-division.py` |
| read the fuller version it was cut from | `solutions/ch01-quantum-threat/` |
| write the chapter's functions yourself | `exercises/ch01-quantum-threat/`, then `PQC_IMPL=exercises pytest tests/ch01` |
| check either package tree | `pytest tests/ch01` |

Every path above is a real one in this clone. Substitute another released chapter's number to move around.

The worked answers to a chapter's numbered exercises are not a separate tree: they are functions in that chapter's `solutions/` package, stubbed in `exercises/` and pinned by `tests/`. Chapter 1's `factor_trial_division_counted` is its exercise 2. The prose form of those answers is Appendix D, on the website.

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

A clone carries the chapters released so far, and nothing for the ones still in editorial review. Run a chapter's suite from the repository root:

```
pytest tests/ch01
```

The suite defaults to the reference implementation, so a clone is green on the first run.

## Implementing a chapter yourself

```
PQC_IMPL=exercises pytest tests/ch01
```

Every stubbed function raises `NotImplementedError` until you write it, so the first run is red by design. Open `exercises/ch01-quantum-threat/`, implement one function, run again. Each stub keeps the reference implementation's signature and adds a contract block naming what it owes its caller, where the book covers it, and which test proves it. Most stubs keep the reference docstring too, so the contract you implement against is the one the book describes rather than a paraphrase. The rest are functions the reference itself wrote without one, mostly one-line address accessors and field-arithmetic helpers, and there the contract block is the whole contract.

`PQC_IMPL` accepts only `solutions` or `exercises`. Every chapter with a package under `solutions/` has one under `exercises/` as well, so `PQC_IMPL=exercises` resolves for every test directory in the clone. Chapter 3 is the one chapter of the book with no package under either tree and no suite to run, because it prints no code.

Nothing is hidden: `solutions/` is in this clone. Reading it costs you the exercise, which is a trade only you can price.

## Troubleshooting

**"No module named 'numpy'" in a Part II chapter.** The venv is active but numpy was not installed. Run `pip install "numpy>=1.26"` inside the venv.

**Pytest reports "no tests ran".** Two causes. Either the chapter named on the command line has not been released yet, so there is no `tests/chNN` directory to collect from (see Release model), or pytest was called from outside the repository root, since the chapter test directories are resolved relative to it.

**`python3 --version` reports 3.8 or 3.9.** Six of the reference packages annotate an optional argument with a PEP 604 union such as `bytes | None` and do not import `annotations` from `__future__`. On both versions the annotation is evaluated when the function is defined, so importing one of those modules raises `TypeError: unsupported operand type(s) for |` rather than a `SyntaxError`. The official installer at python.org bypasses a system package manager's pin.

**The venv activates but `which python` still points at the system CPython.** The shell cached the pre-venv path. Open a new shell, `cd` in, activate again.

Appendix C of the book covers the environment contract in full.

## Release model

The book publishes one chapter at a time, and a chapter's code publishes with it. This repository tracks the published book rather than the working draft, so anything present here belongs to a chapter that has cleared review. Expect it to grow as the book does.

**Chapters released so far: Chapter 1.** The rest of the book is in editorial review, and each chapter's four trees land here on the day its prose publishes.

## What this repository is not

It does not contain the book's prose or figures. Those live at [book.encryptorium.com](https://book.encryptorium.com), where the worked solutions to the numbered exercises are published as Appendix D alongside each released chapter.

## License

MIT, see `LICENSE`. The book's prose is licensed separately under CC BY-SA 4.0.

## Reporting a problem

The book makes two claims a reader can check: every algorithm runs, and every claim is sourced. A violation of either is a bug. Open an issue here, or write to <contact@encryptorium.com>.
