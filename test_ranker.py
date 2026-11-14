import math
import unittest

from inverted_index import InvertedIndex
from main import SearchEngine, main
from ranker import Ranker
from tokenizer import Tokenizer


class TestRanker(unittest.TestCase):

    def setUp(self):
        self.tokenizer = Tokenizer()
        self.index = InvertedIndex()
        self.docs = {
            "d1.txt": self.tokenizer.tokenize("solar solar power energy"),
            "d2.txt": self.tokenizer.tokenize("solar wind turbine electricity"),
            "d3.txt": self.tokenizer.tokenize("bread flour oven baking recipe"),
        }
        self.index.build(self.docs)
        self.ranker = Ranker(self.index, tokenizer=self.tokenizer)

    def test_tfidf_exact_calculation(self):
        results = dict(self.ranker.rank_tfidf("solar"))
        expected_idf = math.log(4.0 / 3.0) + 1.0
        self.assertAlmostEqual(results["d1.txt"], (2 / 4) * expected_idf)
        self.assertAlmostEqual(results["d2.txt"], (1 / 4) * expected_idf)
        self.assertNotIn("d3.txt", results)

    def test_bm25_exact_calculation(self):
        results = dict(self.ranker.rank_bm25("solar"))
        avgdl = 13.0 / 3.0
        k1, b = 1.5, 0.75
        expected_idf = math.log(((3 - 2 + 0.5) / (2 + 0.5)) + 1.0)
        norm = 1.0 - b + b * (4.0 / avgdl)
        expected_d1 = expected_idf * ((2 * (k1 + 1.0)) / (2 + k1 * norm))
        expected_d2 = expected_idf * ((1 * (k1 + 1.0)) / (1 + k1 * norm))
        self.assertAlmostEqual(results["d1.txt"], expected_d1)
        self.assertAlmostEqual(results["d2.txt"], expected_d2)
        self.assertNotIn("d3.txt", results)

    def test_ranking_order_and_rarity_boost(self):
        bm25_results = self.ranker.search("solar energy", method="bm25")
        tfidf_results = self.ranker.search("solar energy", method="tfidf")
        self.assertEqual([doc for doc, _ in bm25_results], ["d1.txt", "d2.txt"])
        self.assertEqual([doc for doc, _ in tfidf_results], ["d1.txt", "d2.txt"])

    def test_deterministic_tie_breaking(self):
        index = InvertedIndex()
        index.build({
            "b.txt": ["rocket", "orbit"],
            "a.txt": ["rocket", "orbit"],
        })
        ranker = Ranker(index)
        results = ranker.search("rocket", method="bm25")
        self.assertEqual([doc for doc, _ in results], ["a.txt", "b.txt"])

    def test_top_k_limits_results(self):
        results = self.ranker.search("solar", method="bm25", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "d1.txt")

    def test_case_insensitive_and_stop_words_ignored(self):
        results = self.ranker.search("THE Solar ENERGY!", method="bm25")
        self.assertEqual([doc for doc, _ in results], ["d1.txt", "d2.txt"])

    def test_pretokenized_query_accepted(self):
        from_str = self.ranker.search("solar energy", method="bm25")
        from_tokens = self.ranker.search(["solar", "energy"], method="bm25")
        self.assertEqual(from_str, from_tokens)

    def test_empty_or_missing_query_returns_empty(self):
        self.assertEqual(self.ranker.search(""), [])
        self.assertEqual(self.ranker.search("the and of"), [])
        self.assertEqual(self.ranker.search("quantum"), [])

    def test_empty_index_returns_empty(self):
        empty_ranker = Ranker(InvertedIndex())
        self.assertEqual(empty_ranker.search("solar", method="bm25"), [])
        self.assertEqual(empty_ranker.search("solar", method="tfidf"), [])

    def test_invalid_inputs_raise(self):
        with self.assertRaises(TypeError):
            Ranker("not_an_index")
        with self.assertRaises(ValueError):
            self.ranker.search("solar", method="unknown")
        with self.assertRaises(ValueError):
            self.ranker.search("solar", top_k=0)


class TestEndToEndPipeline(unittest.TestCase):

    def test_sample_docs_search_pipeline(self):
        engine = SearchEngine()
        stats = engine.build_index("sample_docs")
        self.assertEqual(stats["document_count"], 15)

        for method in ("bm25", "tfidf"):
            results = engine.search("solar energy panels", method=method, top_k=3)
            self.assertTrue(results)
            top_doc, top_score = results[0]
            self.assertIn("solar_power.txt", top_doc)
            self.assertGreater(top_score, 0.0)

    def test_cli_main_runs_cleanly(self):
        exit_code = main(
            ["sample_docs", "rocket satellite orbit", "--method", "bm25", "--top-k", "3"]
        )
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()