"""
evaluate.py  (P5)

Performance and correctness check for the mini search engine.

For 3 corpus sizes (10 / 100 / 1000 documents) it measures:
  Load        - FileLoader reading the files
  Tokenize    - Tokenizer.tokenize_all on the loaded text
  Full build  - SearchEngine().build_index(folder): load + tokenize + index
  Search      - average time of ONE query, for BM25 and for TF-IDF
and it checks that the search results are correct.

Run:
    python generate_docs.py     # once - makes the 10 / 100 / 1000 file folders
    python evaluate.py
"""
import contextlib
import io
import os
import sys
import time
from collections import Counter

from file_loader import FileLoader
from tokenizer import Tokenizer
from main import SearchEngine

SIZES = [10, 100, 1000]
METHODS = ["bm25", "tfidf"]
BUILD_REPEATS = 3        # load / tokenize / build are timed 3 times, best one kept
SEARCH_REPEATS = 20      # every query is run this many times, then averaged
TOP_K = 5                # what a normal search asks for


def silent():
    """Hide anything printed inside a 'with' block (the engine prints status
    lines, which would clutter the output and slow down the timing)."""
    return contextlib.redirect_stdout(io.StringIO())


def build_engine(folder):
    """SearchEngine() is created empty; build_index(folder) then loads the
    files, tokenizes them and builds the index."""
    with silent():
        engine = SearchEngine()
        engine.build_index(folder)
    return engine


def count_txt(folder):
    """Number of .txt files in a folder, including its subfolders."""
    total = 0
    for _, _, files in os.walk(folder):
        total += sum(1 for name in files if name.endswith(".txt"))
    return total


def find_folders():
    """Find the folders made by generate_docs.py: the ones that hold exactly
    10, 100 and 1000 .txt files. Returns {10: path, 100: path, 1000: path}."""
    found = {}
    for root, dirs, _ in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        for d in dirs:
            path = os.path.join(root, d)
            n = count_txt(path)
            if n in SIZES and n not in found:
                found[n] = path
    return found


def best_of(func, repeats=BUILD_REPEATS):
    """Run func() several times. Return (its result, fastest time in ms)."""
    best = None
    result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = func()
        elapsed = (time.perf_counter() - start) * 1000
        if best is None or elapsed < best:
            best = elapsed
    return result, best


def pick_queries(doc_words):
    """Pick a common, a medium and a rare word from the corpus itself.
    Words in half the documents or more are skipped: TF-IDF / BM25 give them
    a score of about 0, so they cannot be tested fairly."""
    n = len(doc_words)
    doc_freq = Counter()
    for words in doc_words.values():
        doc_freq.update(words)
    ranked = [w for w, df in doc_freq.most_common() if df * 2 < n]
    if len(ranked) < 3:
        ranked = [w for w, _ in doc_freq.most_common()]
    return [ranked[0], ranked[len(ranked) // 2], ranked[-1]]


def check_correct(engine, doc_words, queries):
    """Compare the engine with a slow brute-force scan of every document."""
    n = len(doc_words)
    ok = True

    def ask(query, **kwargs):
        with silent():
            return engine.search(query, **kwargs)

    for method in METHODS:
        for query in queries:
            expected = {path for path, words in doc_words.items() if query in words}
            results = ask(query, method=method, top_k=n)
            paths = [path for path, _ in results]
            scores = [score for _, score in results]

            if set(paths) != expected or len(paths) != len(set(paths)):
                print(f"  FAIL [{method}] '{query}': expected {len(expected)} docs, got {len(paths)}")
                ok = False
            elif scores != sorted(scores, reverse=True):
                print(f"  FAIL [{method}] '{query}': results are not sorted best-first")
                ok = False
            elif len(ask(query, method=method, top_k=TOP_K)) > TOP_K:
                print(f"  FAIL [{method}] '{query}': top_k was ignored")
                ok = False

    # edge cases: a stop-word-only query and an unknown word give no results
    for query in ("the and is", "zzzqqqxxx"):
        if ask(query):
            print(f"  FAIL: '{query}' should return no results")
            ok = False
    return ok


def evaluate_size(n, folder):
    docs, t_load = best_of(lambda: FileLoader().load_files(folder))
    tokens, t_tokenize = best_of(lambda: Tokenizer().tokenize_all(docs))
    engine, t_build = best_of(lambda: build_engine(folder))

    doc_words = {path: set(words) for path, words in tokens.items()}
    queries = pick_queries(doc_words)

    t_search = {}
    for method in METHODS:
        with silent():
            start = time.perf_counter()
            for _ in range(SEARCH_REPEATS):
                for query in queries:
                    engine.search(query, method=method, top_k=TOP_K)
            total = time.perf_counter() - start
        t_search[method] = total / (SEARCH_REPEATS * len(queries)) * 1000

    print(f"Checking {n} docs in {folder} (queries: {queries})")
    ok = check_correct(engine, doc_words, queries)
    if len(docs) != n:
        print(f"  FAIL: loaded {len(docs)} files, expected {n}")
        ok = False

    return {"n": n, "load": t_load, "tokenize": t_tokenize, "build": t_build,
            "bm25": t_search["bm25"], "tfidf": t_search["tfidf"], "ok": ok}


def main():
    folders = find_folders()
    missing = [n for n in SIZES if n not in folders]
    if missing:
        sys.exit(f"No folder with exactly {missing} .txt files found - "
                 "run python generate_docs.py first.")

    rows = [evaluate_size(n, folders[n]) for n in SIZES]

    print()
    print("| Docs | Load (ms) | Tokenize (ms) | Full build (ms) | BM25 search (ms) | TF-IDF search (ms) | Correct |")
    print("|------|-----------|---------------|-----------------|------------------|--------------------|---------|")
    for r in rows:
        print(f"| {r['n']} | {r['load']:.1f} | {r['tokenize']:.1f} | {r['build']:.1f} | "
              f"{r['bm25']:.3f} | {r['tfidf']:.3f} | {'PASS' if r['ok'] else 'FAIL'} |")

    if not all(r["ok"] for r in rows):
        sys.exit(1)


if __name__ == "__main__":
    main()
