import os
import unittest

from tokenizer import Tokenizer


class TestTokenizer(unittest.TestCase):

    def setUp(self):
        self.tokenizer = Tokenizer()

    def test_lowercase_and_punctuation(self):
        self.assertEqual(
            self.tokenizer.tokenize("Solar POWER, wind-turbines!"),
            ["solar", "power", "wind", "turbines"]
        )

    def test_stop_words_removed(self):
        self.assertEqual(
            self.tokenizer.tokenize("The rocket is on the launch pad"),
            ["rocket", "launch", "pad"]
        )

    def test_stop_words_kept_when_disabled(self):
        tokenizer = Tokenizer(remove_stop_words=False)
        self.assertEqual(
            tokenizer.tokenize("The rocket is ready"),
            ["the", "rocket", "is", "ready"]
        )

    def test_numbers_are_kept(self):
        self.assertEqual(
            self.tokenizer.tokenize("Mars 2020 rover"),
            ["mars", "2020", "rover"]
        )

    def test_apostrophes_joined(self):
        self.assertEqual(
            self.tokenizer.tokenize("Earth's orbit, don't stop"),
            ["earths", "orbit", "dont", "stop"]
        )

    def test_non_english_letters(self):
        # P1 decodes some files as latin-1, so words like "café" must survive.
        self.assertEqual(self.tokenizer.tokenize("Café menu"), ["café", "menu"])

    def test_underscores_split_words(self):
        self.assertEqual(self.tokenizer.tokenize("snake_case"), ["snake", "case"])

    def test_min_length(self):
        tokenizer = Tokenizer(min_length=3)
        self.assertEqual(tokenizer.tokenize("ox runs far away"), ["runs", "far", "away"])

    def test_empty_and_punctuation_only(self):
        self.assertEqual(self.tokenizer.tokenize(""), [])
        self.assertEqual(self.tokenizer.tokenize("  ...!!! ,,, "), [])

    def test_non_string_raises(self):
        with self.assertRaises(TypeError):
            self.tokenizer.tokenize(None)
        with self.assertRaises(TypeError):
            self.tokenizer.tokenize(["solar"])

    def test_tokens_are_valid_for_inverted_index(self):
        # InvertedIndex rejects empty or non-string tokens.
        tokens = self.tokenizer.tokenize("  Hello -- world ' _ 42 ... ")
        self.assertTrue(all(isinstance(t, str) and t for t in tokens))

    def test_query_matches_document(self):
        doc = self.tokenizer.tokenize("Solar panels capture sunlight.")
        query = self.tokenizer.tokenize("SOLAR")
        self.assertIn(query[0], doc)

    def test_tokenize_all_keeps_ids(self):
        docs = {"a.txt": "Wind power", "b.txt": "The battery"}
        self.assertEqual(
            self.tokenizer.tokenize_all(docs),
            {"a.txt": ["wind", "power"], "b.txt": ["battery"]}
        )


@unittest.skipUnless(
    os.path.exists("file_loader.py") and os.path.isdir("sample_docs"),
    "needs P1's file_loader.py and sample_docs (after merge into main)"
)
class TestTokenizerWithSampleDocs(unittest.TestCase):

    def test_every_sample_file_gives_tokens(self):
        from file_loader import FileLoader
        docs = FileLoader().load_files("sample_docs")
        tokens = Tokenizer().tokenize_all(docs)
        self.assertEqual(set(tokens), set(docs))
        for path, words in tokens.items():
            self.assertTrue(words, f"{path} produced no tokens")


if __name__ == "__main__":
    unittest.main()
