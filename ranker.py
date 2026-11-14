"""P4: Keyword search and relevance ranking using TF-IDF and BM25.

Consumes P3's InvertedIndex and P2's Tokenizer to score and rank matching
documents from most to least relevant.
"""
import math

from inverted_index import InvertedIndex
from tokenizer import Tokenizer


class Ranker:
    """Rank indexed documents for a keyword query using TF-IDF or BM25."""

    def __init__(self, index, tokenizer=None, k1=1.5, b=0.75):
        if not isinstance(index, InvertedIndex):
            raise TypeError("index must be an InvertedIndex instance.")
        if k1 < 0:
            raise ValueError("k1 must be non-negative.")
        if not (0.0 <= b <= 1.0):
            raise ValueError("b must be between 0.0 and 1.0.")

        self.index = index
        self.tokenizer = tokenizer if tokenizer is not None else Tokenizer()
        self.k1 = k1
        self.b = b

    def _prepare_query(self, query):
        """Convert a raw query string or token sequence into a list of tokens."""
        if isinstance(query, str):
            return self.tokenizer.tokenize(query)
        if isinstance(query, (list, tuple)):
            tokens = []
            for token in query:
                if not isinstance(token, str) or not token:
                    raise ValueError("Every query token must be a non-empty string.")
                tokens.append(token)
            return tokens
        raise TypeError("Query must be a string or a sequence of tokens.")

    @staticmethod
    def _validate_top_k(top_k):
        if top_k is not None and (
            isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1
        ):
            raise ValueError("top_k must be a positive integer or None.")

    def _collect_postings(self, query_tokens):
        """Fetch postings once per unique query term to avoid redundant copies."""
        postings_by_term = {}
        for term in query_tokens:
            if term not in postings_by_term:
                postings_by_term[term] = self.index.lookup(term)
        return postings_by_term

    def rank_tfidf(self, query, top_k=None):
        """Return [(doc_id, score), ...] ranked by length-normalized TF-IDF."""
        self._validate_top_k(top_k)
        stats = self.index.get_statistics()
        num_docs = stats["document_count"]
        if num_docs == 0:
            return []

        query_tokens = self._prepare_query(query)
        if not query_tokens:
            return []

        postings_by_term = self._collect_postings(query_tokens)
        idf_by_term = {
            term: math.log((num_docs + 1.0) / (len(postings) + 1.0)) + 1.0
            for term, postings in postings_by_term.items()
            if postings
        }

        scores = {}
        for term in query_tokens:
            postings = postings_by_term.get(term)
            if not postings:
                continue
            idf = idf_by_term[term]
            for doc_id, tf in postings.items():
                doc_len = self.index.get_document_length(doc_id)
                if doc_len <= 0:
                    continue
                tf_norm = tf / doc_len
                scores[doc_id] = scores.get(doc_id, 0.0) + tf_norm * idf

        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        return ranked[:top_k] if top_k is not None else ranked

    def rank_bm25(self, query, top_k=None):
        """Return [(doc_id, score), ...] ranked by Okapi BM25."""
        self._validate_top_k(top_k)
        stats = self.index.get_statistics()
        num_docs = stats["document_count"]
        avgdl = stats["average_document_length"]
        if num_docs == 0 or avgdl <= 0:
            return []

        query_tokens = self._prepare_query(query)
        if not query_tokens:
            return []

        postings_by_term = self._collect_postings(query_tokens)
        idf_by_term = {}
        for term, postings in postings_by_term.items():
            if postings:
                df = len(postings)
                idf_by_term[term] = math.log(((num_docs - df + 0.5) / (df + 0.5)) + 1.0)

        scores = {}
        for term in query_tokens:
            postings = postings_by_term.get(term)
            if not postings:
                continue
            idf = idf_by_term[term]
            for doc_id, tf in postings.items():
                doc_len = self.index.get_document_length(doc_id)
                if doc_len <= 0:
                    continue
                norm = 1.0 - self.b + self.b * (doc_len / avgdl)
                denom = tf + self.k1 * norm
                term_score = idf * ((tf * (self.k1 + 1.0)) / denom)
                scores[doc_id] = scores.get(doc_id, 0.0) + term_score

        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        return ranked[:top_k] if top_k is not None else ranked

    def search(self, query, method="bm25", top_k=None):
        """Search and rank documents using 'bm25' (default) or 'tfidf'."""
        if not isinstance(method, str):
            raise TypeError("method must be a string ('bm25' or 'tfidf').")
        normalized = method.strip().lower()
        if normalized == "bm25":
            return self.rank_bm25(query, top_k=top_k)
        if normalized == "tfidf":
            return self.rank_tfidf(query, top_k=top_k)
        raise ValueError(
            f"Unsupported ranking method: {method!r}. Expected 'bm25' or 'tfidf'."
        )

    def rank(self, query, method="bm25", top_k=None):
        """Alias for search()."""
        return self.search(query, method=method, top_k=top_k)