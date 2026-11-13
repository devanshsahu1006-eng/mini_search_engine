"""P1: File handling. Walk a folder and read every .txt file.

Output: {file_path: text}
"""
import os


class FileLoader:
    def __init__(self, extension=".txt"):
        self.extension = extension

    def read_file(self, path):
        """Return the text of one file, or None if it cannot be read."""
        try:
            with open(path, "rb") as f:
                raw = f.read()
        except OSError as error:                 # permission denied, broken link...
            print(f"Skipping {path}: {error}")
            return None
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("latin-1")         # latin-1 accepts any byte

    def load_files(self, folder):
        docs = {}
        for root, dirs, names in os.walk(folder):    # visits every subfolder
            dirs.sort()                              # same order every run
            for name in sorted(names):
                if name.endswith(self.extension):
                    path = os.path.join(root, name)
                    text = self.read_file(path)
                    if text is not None:
                        docs[path] = text
        return docs


if __name__ == "__main__":
    import sys
    docs = FileLoader().load_files(sys.argv[1] if len(sys.argv) > 1 else "sample_docs")
    print(f"Loaded {len(docs)} files")
    for path, text in list(docs.items())[:2]:
        print(path, "->", text[:50])
