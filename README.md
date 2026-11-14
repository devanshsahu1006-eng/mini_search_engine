# Mini Search Engine for Local Documents

A small keyword search engine for a folder of `.txt` files. It reads the files,
splits them into words, builds an inverted index and returns the best-matching
documents, ranked by BM25 (default) or TF-IDF. Built in Python for a 6-person
course project (SSL).

## How it works

    files -> FileLoader -> Tokenizer -> InvertedIndex -> Ranker -> results

| Step | File | What it does |
|------|------|--------------|
| 1 | `file_loader.py` | Reads every `.txt` in a folder and its subfolders. Skips files it cannot open; falls back to Latin-1 if a file is not UTF-8. Returns `{file_path: text}`. |
| 2 | `tokenizer.py` | Lowercases, removes punctuation and common stop words (keeps "no" and "not"), joins apostrophes (don't -> dont), keeps numbers and accented words. |
| 3 | `inverted_index.py` | Maps each word to the documents that contain it. |
| 4 | `ranker.py` | Scores matching documents with BM25 or TF-IDF, highest score first. |
| 5 | `main.py` | Connects all steps. `SearchEngine` class plus a command-line interface. |

## Requirements

- Python 3
- Bash (only for `search.sh`)
- `pytest` for the tests (`pip install pytest`)

If your system only has `python3` (no `python`), use a virtual environment. It
gives you `python` and `pip`, and `search.sh` needs `python` too:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install pytest

## How to run

    # search the demo documents (15 files, 5 topics: energy, cooking, sports, space, health)
    python main.py sample_docs "solar energy"
    python main.py sample_docs "solar energy" --method tfidf --top-k 3
    ./search.sh -d sample_docs "solar power"
    ./search.sh -h

    # make the 10 / 100 / 1000 document test folders
    python generate_docs.py

    # run all unit tests
    pytest

    # timing + correctness check
    python evaluate.py

    # profile indexing and search
    python profile_run.py

## Results

Output of `python evaluate.py`. "Full build" is the whole
`SearchEngine().build_index(folder)` step (load + tokenize + index). Search
times are per query.

| Docs | Load (ms) | Tokenize (ms) | Full build (ms) | BM25 search (ms) | TF-IDF search (ms) | Correct |
|------|-----------|---------------|-----------------|------------------|--------------------|---------|
| 10   | 0.2  | 0.2  | 0.4  | 0.003 | 0.003 | PASS |
| 100  | 1.8  | 2.0  | 3.9  | 0.008 | 0.006 | PASS |
| 1000 | 16.8 | 19.2 | 38.5 | 0.070 | 0.056 | PASS |

What the results show:

- **Building scales roughly linearly.** 10 times more documents takes about 10
  times longer to load, tokenize and build.
- **Loading and tokenizing dominate the build.** At 1000 documents they take
  about 36 ms of the 38.5 ms total, so building the index itself is only a few
  milliseconds.
- **Search is very fast and grows slowly.** A query stays under 0.1 ms even at
  1000 documents. It grows far less than the corpus does, because a query only
  touches the documents that contain its words.
- **TF-IDF is slightly faster than BM25** (0.056 vs 0.070 ms at 1000 documents).
  The difference is tiny in practice.

How correctness is checked: for a common, a medium and a rare word, the engine's
result set is compared with a slow brute-force scan of every document. We also
check that scores are sorted best-first, that `top_k` is respected, and that a
stop-word-only query and an unknown word return no results.

## Profiling

`profile_run.py` runs Python's `cProfile` on the inverted index (`build()` and
`lookup()`), using generated documents of 200 words each, at several corpus
sizes. It shows which functions take the most time.

Selected results (profiler overhead included, so times are higher than in the
table above):

| Documents | `build()` time | Function calls | Where the time goes |
|-----------|----------------|----------------|---------------------|
| 10  | 0.001 s | 4,055 | `_add_to_index`, `_validate_document` |
| 100 | 0.008 s | 40,505 | `_add_to_index` (about 60%), `_validate_document` (about a third) |

- Build time grows with the number of words, and the calls scale the same way:
  10 times more documents gives about 10 times more function calls.
- Most of the build is spent in `_add_to_index`, with the per-document check in
  `_validate_document` taking a large share too.
- 10,000 lookups (existing and missing words) take about 0.013 s in total, so a
  single `lookup()` is very cheap. Each call also makes a small copy of the stored data.

Run `python profile_run.py` to see the full output, including the larger sizes.

## Project files

| File | Owner | Purpose |
|------|-------|---------|
| `file_loader.py`, `generate_docs.py`, `sample_docs/`, `test_file_loader.py` | P1 | Reading files, test data |
| `tokenizer.py`, `search.sh`, `test_tokenizer.py` | P2 | Tokenization, Bash wrapper |
| `inverted_index.py`, `profile_run.py`, `test_inverted_index.py` | P3 | Index, profiling |
| `ranker.py`, `main.py`, `test_ranker.py` | P4 | BM25 / TF-IDF ranking, main program |
| `README.md`, `.gitignore`, `.gitattributes`, `evaluate.py` | P5 | Docs, repo setup, evaluation |

## Team

| Role | Member | GitHub | Institute ID |
|------|--------|--------|--------------|
| P1 - file loading, test data | Devansh | devanshsahu1006-eng | CS25BT023 |
| P2 - tokenizer, Bash wrapper | Suzane | suzane-jazinth | CS25BT035 |
| P3 - inverted index, profiling | Sarthak | Sarthak-2408 | MC25BT026 |
| P4 - ranking, main program | Rhithick | BlazingFlames64 | MC25BT016 |
| P5 - README, evaluation | Divyansh | divyanshsahu77805-star | MC25BT017 |
| Presentation (LaTeX / Beamer) | Haseeb | dominator5127-beep | MC25BT009 |

Everyone worked on a feature branch (`feature/loader`, `feature/tokenizer`,
`feature/index`, `feature/ranker`) and merged it into `main`.
