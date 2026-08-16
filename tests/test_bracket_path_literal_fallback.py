"""Regression tests: a literal path containing "[" or "]" resolves correctly.

`resolve_input_files` routes any path containing a glob metacharacter
("*", "?", "[") to `glob.glob()`. Before this fix, that happened
unconditionally, even when the path was a real file that exists on disk --
`glob.glob()` treats "[...]" as a character class, so a filename like
Zotero's default "Author - Title [year].pdf" matched nothing and was
silently dropped, surfacing only as a misleading "No supported files found"
error with no indication the file was ever seen.

This fix checks literal existence first and only falls back to glob
expansion when there's no literal match -- it does not change what happens
for a bracket path that matches nothing either way (still an empty result,
covered below for contrast with the fixed case).
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from book_to_skill.utils import resolve_input_files  # noqa: E402


def test_literal_file_with_brackets_in_name_resolves(tmp_path):
    """The exact Zotero-style filename from the issue report."""
    target = tmp_path / "Landon - Building Great Sentences [2013].pdf"
    target.write_bytes(b"%PDF-1.4 fake pdf content")

    result = resolve_input_files([str(target)])

    assert result == [target.resolve()]


def test_literal_directory_with_brackets_in_name_is_walked(tmp_path):
    """A directory name containing brackets still gets walked, not glob-matched."""
    docs = tmp_path / "notes [drafts]"
    docs.mkdir()
    (docs / "a.md").write_text("# A", encoding="utf-8")
    (docs / "ignored.bin").write_text("binary", encoding="utf-8")

    result = resolve_input_files([str(docs)])

    assert [p.name for p in result] == ["a.md"]


def test_real_glob_pattern_with_brackets_still_expands(tmp_path):
    """A genuine character-class glob (no literal file of that exact name) still works."""
    (tmp_path / "ch1.md").write_text("# Ch1", encoding="utf-8")
    (tmp_path / "ch2.md").write_text("# Ch2", encoding="utf-8")
    (tmp_path / "chA.md").write_text("# ChA", encoding="utf-8")

    pattern = str(tmp_path / "ch[0-9].md")
    result = resolve_input_files([pattern])

    assert [p.name for p in result] == ["ch1.md", "ch2.md"]


def test_nonexistent_bracket_path_still_returns_empty_unchanged(tmp_path):
    """A bracket path matching nothing literally or via glob still returns []
    -- unchanged pre-existing behavior for any non-matching glob pattern,
    not something this fix touches (it only changes the literal-exists case)."""
    missing = tmp_path / "Author - Title [2020].pdf"

    result = resolve_input_files([str(missing)])

    assert result == []
