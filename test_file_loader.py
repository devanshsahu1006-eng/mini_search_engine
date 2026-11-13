import os
from file_loader import FileLoader


def test_loads_only_txt_files_recursively(tmp_path):
    (tmp_path / "a.txt").write_text("hello")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("world")
    (tmp_path / "ignore.pdf").write_text("not loaded")
    docs = FileLoader().load_files(str(tmp_path))
    assert sorted(docs.values()) == ["hello", "world"]


def test_latin1_fallback(tmp_path):
    (tmp_path / "x.txt").write_bytes("caf\xe9".encode("latin-1"))
    docs = FileLoader().load_files(str(tmp_path))
    assert list(docs.values()) == ["caf\xe9"]


def test_sample_docs_has_15_files():
    docs = FileLoader().load_files("sample_docs")
    assert len(docs) == 15
