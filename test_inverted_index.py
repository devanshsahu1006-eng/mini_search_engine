import unittest

from inverted_index import InvertedIndex


class TestInvertedIndex(unittest.TestCase):

    def setUp(self):
        self.index = InvertedIndex()
        self.documents = {
            "doc1": ["python", "java", "python", "c"],
            "doc2": ["python", "javascript", "java"],
            "doc3": ["c", "python", "python"]
        }
        self.index.build(self.documents)

    def test_build_index(self):
        self.assertEqual(
            self.index.index,
            {
                "python": {"doc1": 2, "doc2": 1, "doc3": 2},
                "java": {"doc1": 1, "doc2": 1},
                "c": {"doc1": 1, "doc3": 1},
                "javascript": {"doc2": 1}
            }
        )

    def test_lookup_existing_term(self):
        self.assertEqual(
            self.index.lookup("python"),
            {"doc1": 2, "doc2": 1, "doc3": 2}
        )

    def test_lookup_missing_term(self):
        self.assertEqual(self.index.lookup("ruby"), {})

    def test_term_frequency(self):
        self.assertEqual(self.index.lookup("python")["doc1"], 2)
        self.assertEqual(self.index.lookup("python")["doc2"], 1)

    def test_document_frequency(self):
        self.assertEqual(self.index.get_document_frequency("python"), 3)
        self.assertEqual(self.index.get_document_frequency("java"), 2)
        self.assertEqual(self.index.get_document_frequency("ruby"), 0)

    def test_document_length(self):
        self.assertEqual(self.index.get_document_length("doc1"), 4)
        self.assertEqual(self.index.get_document_length("doc2"), 3)
        self.assertEqual(self.index.get_document_length("unknown"), 0)

    def test_add_document(self):
        self.index.add_document("doc4", ["python", "ruby", "ruby"])

        self.assertEqual(
            self.index.lookup("ruby"),
            {"doc4": 2}
        )
        self.assertEqual(self.index.get_document_length("doc4"), 3)

    def test_replace_existing_document(self):
        self.index.add_document("doc1", ["ruby", "ruby", "java"])

        self.assertEqual(
            self.index.lookup("python"),
            {"doc2": 1, "doc3": 2}
        )
        self.assertEqual(
            self.index.lookup("ruby"),
            {"doc1": 2}
        )
        self.assertEqual(self.index.get_document_length("doc1"), 3)

    def test_remove_document(self):
        result = self.index.remove_document("doc1")

        self.assertTrue(result)
        self.assertEqual(self.index.get_document_length("doc1"), 0)
        self.assertNotIn("doc1", self.index.lookup("python"))

    def test_remove_nonexistent_document(self):
        result = self.index.remove_document("unknown")
        self.assertFalse(result)

    def test_remove_unused_terms(self):
        self.index.remove_document("doc2")

        self.assertNotIn("javascript", self.index.index)
        self.assertNotIn("doc2", self.index.lookup("java"))

    def test_statistics(self):
        stats = self.index.get_statistics()

        self.assertEqual(stats["document_count"], 3)
        self.assertEqual(stats["vocabulary_size"], 4)
        self.assertEqual(stats["total_tokens"], 10)
        self.assertAlmostEqual(stats["average_document_length"], 10 / 3)

    def test_empty_documents(self):
        empty_index = InvertedIndex()
        empty_index.build({})

        self.assertEqual(empty_index.index, {})
        self.assertEqual(empty_index.document_lengths, {})
        self.assertEqual(
            empty_index.get_statistics(),
            {
                "document_count": 0,
                "vocabulary_size": 0,
                "total_tokens": 0,
                "average_document_length": 0
            }
        )

    def test_document_with_empty_tokens(self):
        empty_index = InvertedIndex()
        empty_index.build({"doc1": []})

        self.assertEqual(empty_index.lookup("python"), {})
        self.assertEqual(empty_index.get_document_length("doc1"), 0)

    def test_invalid_document_id(self):
        with self.assertRaises(ValueError):
            self.index.build({"": ["python"]})

        with self.assertRaises(ValueError):
            self.index.build({123: ["python"]})

    def test_invalid_tokens_type(self):
        with self.assertRaises(TypeError):
            self.index.build({"doc1": "python java"})

        with self.assertRaises(TypeError):
            self.index.build({"doc1": None})

    def test_invalid_token_values(self):
        with self.assertRaises(ValueError):
            self.index.build({"doc1": ["python", ""]})

        with self.assertRaises(ValueError):
            self.index.build({"doc1": ["python", 123]})

    def test_invalid_documents_type(self):
        with self.assertRaises(TypeError):
            self.index.build(["python", "java"])

    def test_add_document_validation(self):
        with self.assertRaises(ValueError):
            self.index.add_document("", ["python"])

        with self.assertRaises(TypeError):
            self.index.add_document("doc4", "python")

    def test_failed_build_preserves_existing_index(self):
        original_index = {
            term: postings.copy()
            for term, postings in self.index.index.items()
        }
        original_lengths = self.index.document_lengths.copy()

        with self.assertRaises(ValueError):
            self.index.build({
                "doc4": ["ruby", "python"],
                "": ["java"]
            })

        self.assertEqual(self.index.index, original_index)
        self.assertEqual(self.index.document_lengths, original_lengths)

    def test_lookup_returns_copy(self):
        result = self.index.lookup("python")
        result["doc1"] = 100

        self.assertEqual(self.index.lookup("python")["doc1"], 2)


if __name__ == "__main__":
    unittest.main()