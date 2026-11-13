"""Profile the Mini Search Engine's InvertedIndex.

Run with:  python profile_run.py
"""

import cProfile
import pstats
import random
import time

from inverted_index import InvertedIndex

DOCUMENT_COUNTS = [10, 100, 1000]  # collection sizes to test
WORDS_PER_DOCUMENT = 200
LOOKUP_REPETITIONS = 10000         # one lookup is too fast to measure
TOP_FUNCTIONS = 5                  # rows shown per profile
MISSING_TERM = "zzz_missing_term"  # never appears in the sample text

VOCABULARY = [
    "Solar", "wind", "Energy", "power", "climate", "battery", "electric",
    "Water", "research", "technology", "grid", "storage", "carbon", "fuel",
]


def make_sample_texts(document_count):
    """Create {doc_id: text} with mixed-case words (repeatable)."""
    random.seed(42)
    texts = {}
    for number in range(document_count):
        words = random.choices(VOCABULARY, k=WORDS_PER_DOCUMENT)
        texts[f"doc{number}"] = " ".join(words)
    return texts


def tokenize(text):
    """Turn text into a list of lowercase words."""
    return text.lower().split()


def tokenize_all(texts):
    """Tokenize every document: {doc_id: [tokens]}."""
    return {doc_id: tokenize(text) for doc_id, text in texts.items()}


def search(index, existing_term, repetitions):
    """Look up one existing and one missing term many times."""
    for _ in range(repetitions):
        index.lookup(existing_term)
        index.lookup(MISSING_TERM)


def run_profile(title, function, *args):
    """Profile function(*args), then print time and the slowest functions."""
    profiler = cProfile.Profile()
    start = time.perf_counter()
    profiler.runcall(function, *args)
    elapsed = time.perf_counter() - start

    stats = pstats.Stats(profiler)
    print(f"\n--- {title} ---")
    print(f"Execution time (with profiler overhead): {elapsed:.6f} seconds")
    print(f"Total function calls: {stats.total_calls}")
    stats.strip_dirs().sort_stats("tottime").print_stats(TOP_FUNCTIONS)


def main():
    for document_count in DOCUMENT_COUNTS:
        print("=" * 60)
        print(f"{document_count} documents x {WORDS_PER_DOCUMENT} words")
        print("=" * 60)

        documents = tokenize_all(make_sample_texts(document_count))
        index = InvertedIndex()

        run_profile("build()", index.build, documents)

        existing_term = next(iter(index.index))
        print(f"Unique terms indexed: {len(index.index)}")
        print(f"Searching for {existing_term!r} (exists) and "
              f"{MISSING_TERM!r} (missing)")

        run_profile(
            f"lookup() x {LOOKUP_REPETITIONS} (existing + missing)",
            search, index, existing_term, LOOKUP_REPETITIONS,
        )


if __name__ == "__main__":
    main()