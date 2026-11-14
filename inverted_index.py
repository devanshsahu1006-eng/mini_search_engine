
class InvertedIndex:
    """Build and query a term-to-document inverted index."""

    def __init__(self):
        self.index = {}
        self.document_lengths = {}

    @staticmethod
    def _validate_document(doc_id, tokens):
        """Check that a document has a valid ID and token list."""
        if not isinstance(doc_id, str) or not doc_id:
            raise ValueError("Document ID must be a non-empty string.")

        if not isinstance(tokens, (list, tuple)):
            raise TypeError("Document tokens must be a list or tuple.")

        for token in tokens:
            if not isinstance(token, str) or not token:
                raise ValueError("Every token must be a non-empty string.")

    @staticmethod
    def _add_to_index(index, doc_id, tokens):
        """Add the tokens of one document to an index."""
        for token in tokens:
            if token not in index:
                index[token] = {}

            postings = index[token]
            postings[doc_id] = postings.get(doc_id, 0) + 1

    def build(self, documents):
        """Build the index from {document_id: list_of_tokens}."""

        if not isinstance(documents, dict):
            raise TypeError("Documents must be a dictionary.")

        # Validate everything before changing the existing index.
        for doc_id, tokens in documents.items():
            self._validate_document(doc_id, tokens)

        new_index = {}
        new_lengths = {}

        for doc_id, tokens in documents.items():
            new_lengths[doc_id] = len(tokens)
            self._add_to_index(new_index, doc_id, tokens)

        self.index = new_index
        self.document_lengths = new_lengths

        return self.index

    def lookup(self, term):
        """Return document IDs and term frequencies for a term."""
        return self.index.get(term, {}).copy()

    def get_document_frequency(self, term):
        """Return the number of documents containing a term."""
        return len(self.index.get(term, {}))

    def get_document_length(self, doc_id):
        """Return the number of tokens in a document."""
        return self.document_lengths.get(doc_id, 0)

    def add_document(self, doc_id, tokens):
        """Add a document or replace an existing document."""

        self._validate_document(doc_id, tokens)

        # Remove the old version if the ID already exists.
        self.remove_document(doc_id)

        self._add_to_index(self.index, doc_id, tokens)
        self.document_lengths[doc_id] = len(tokens)

    def remove_document(self, doc_id):
        """Remove a document and its postings from the index."""

        if doc_id not in self.document_lengths:
            return False

        for term in list(self.index):
            postings = self.index[term]
            postings.pop(doc_id, None)

            # Remove terms that no longer occur in any document.
            if not postings:
                del self.index[term]

        del self.document_lengths[doc_id]
        return True

    def get_statistics(self):
        """Return basic corpus statistics."""

        document_count = len(self.document_lengths)
        total_tokens = sum(self.document_lengths.values())

        average_length = (
            total_tokens / document_count
            if document_count > 0 else 0
        )

        return {
            "document_count": document_count,
            "vocabulary_size": len(self.index),
            "total_tokens": total_tokens,
            "average_document_length": average_length
        }
 