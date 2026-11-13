"""P2: Tokenization. Turn raw text into a list of search terms.

Input:  text (str)            or  {file_path: text}
Output: ["word", "word", ...]  or  {file_path: ["word", ...]}

The same Tokenizer must be used for documents AND queries, so that
"Solar" in a query matches "solar," in a file.
"""
import re


class Tokenizer:
    # Very common words that appear everywhere and carry no meaning for search.
    STOP_WORDS = frozenset("""
        a an and are as at be been but by can did do does for from had has
        have he her his i if in into is it its me my no not of on or our she
        so than that the their them then there these they this to too us was
        we were what when where which who will with you your
    """.split())

    # A word is a run of letters or digits (any language, so "café" stays whole).
    WORD_PATTERN = re.compile(r"[^\W_]+")

    # An apostrophe inside a word: don't -> dont, earth's -> earths
    APOSTROPHE_PATTERN = re.compile(r"(?<=\w)['’](?=\w)")

    def __init__(self, remove_stop_words=True, min_length=1):
        self.remove_stop_words = remove_stop_words
        self.min_length = min_length

    def tokenize(self, text):
        """Return the list of tokens in one piece of text, in order."""
        if not isinstance(text, str):
            raise TypeError("Text must be a string.")

        text = text.lower()
        text = self.APOSTROPHE_PATTERN.sub("", text)
        words = self.WORD_PATTERN.findall(text)       # punctuation is dropped here

        tokens = []
        for word in words:
            if len(word) < self.min_length:
                continue
            if self.remove_stop_words and word in self.STOP_WORDS:
                continue
            tokens.append(word)
        return tokens

    def tokenize_all(self, docs):
        """Tokenize every document: {file_path: text} -> {file_path: [tokens]}."""
        return {doc_id: self.tokenize(text) for doc_id, text in docs.items()}


if __name__ == "__main__":
    import sys
    text = " ".join(sys.argv[1:]) or "The Solar panels, and the Earth's wind-turbines!"
    print("Input: ", text)
    print("Tokens:", Tokenizer().tokenize(text))