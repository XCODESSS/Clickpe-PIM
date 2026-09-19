import pytest

from clickpe_pim.storage.captures import save_bytes


def test_raw_capture_is_immutable(tmp_path):
    path, digest = save_bytes(tmp_path, "r1", "s1", b"first", ".html")
    assert len(digest) == 64
    assert (tmp_path / path).read_bytes() == b"first"
    assert save_bytes(tmp_path, "r1", "s1", b"first", ".html") == (path, digest)
    with pytest.raises(FileExistsError):
        save_bytes(tmp_path, "r1", "s1", b"changed", ".html")


def test_capture_path_rejects_traversal(tmp_path):
    with pytest.raises(ValueError):
        save_bytes(tmp_path, "../r", "s", b"x", ".html")

