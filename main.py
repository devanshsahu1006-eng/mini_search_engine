"""P4: End-to-end search engine pipeline and CLI entry point.

Connects P1 (FileLoader), P2 (Tokenizer), P3 (InvertedIndex), and P4 (Ranker).
Compatible with P2's ./search.sh -d <folder> "<query>" wrapper.
"""
import argparse
import os
import sys

from file_loader import FileLoader
from inverted_index import InvertedIndex
from ranker import Ranker
from tokenizer import Tokenizer


class SearchEngine:
    """Coordinate file loading, tokenization, indexing, and relevance ranking."""

    def __init__(self, loader=None, tokenizer=None, index=None, ranker=None):
        self.loader = loader if loader is not None else FileLoader()
        self.tokenizer = tokenizer if tokenizer is not None else Tokenizer()
        self.index = index if index is not None else InvertedIndex()
        self.ranker = (
            ranker
            if ranker is not None
            else Ranker(self.index, tokenizer=self.tokenizer)
        )

    def build_index(self, folder):
        """Load and index all matching documents under folder."""
        if not os.path.isdir(folder):
            raise FileNotFoundError(f"Folder not found: {folder}")
        docs = self.loader.load_files(folder)
        tokenized_docs = self.tokenizer.tokenize_all(docs)
        self.index.build(tokenized_docs)
        return self.index.get_statistics()

    def search(self, query, method="bm25", top_k=None):
        """Query the built index and return [(doc_id, score), ...]."""
        return self.ranker.search(query, method=method, top_k=top_k)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Search a directory of .txt files using TF-IDF or BM25."
    )
    parser.add_argument("folder", help="Directory containing .txt documents to index")
    parser.add_argument("query", help="Search query string")
    parser.add_argument(
        "-m",
        "--method",
        choices=["bm25", "tfidf"],
        default="bm25",
        help="Scoring algorithm to use (default: bm25)",
    )
    parser.add_argument(
        "-k",
        "--top-k",
        type=int,
        default=10,
        help="Maximum number of results to display (default: 10)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if not os.path.isdir(args.folder):
        print(f"Error: folder '{args.folder}' does not exist.", file=sys.stderr)
        return 1

    engine = SearchEngine()
    stats = engine.build_index(args.folder)
    results = engine.search(args.query, method=args.method, top_k=args.top_k)

    print(
        f"Indexed {stats['document_count']} documents "
        f"({stats['vocabulary_size']} unique terms) | Method: {args.method.upper()}"
    )
    if not results:
        print("No matching documents found.")
        return 0

    for rank_num, (doc_path, score) in enumerate(results, start=1):
        print(f"{rank_num}. [{score:.4f}] {doc_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())