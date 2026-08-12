# BUILDLOG

`C:\Repos\book-to-skill` — fork of [virgiliojr94/book-to-skill](https://github.com/virgiliojr94/book-to-skill) (upstream), pushed to `albatrossflyon-coder/book-to-skill` (origin, write access). OSS contribution repo, not an Albatross AI product — this log tracks our contribution work only, not the upstream project as a whole.

## Tech Stack

- **Languages:** Python (>=3.9)
- **Frameworks/Libraries:** hatchling (build), pytest, ruff, optional parser deps (python-docx, pypdf, pdfminer.six, ebooklib, beautifulsoup4, striprtf, docling)
- **Dev Tools:** GitHub Actions CI, git-cliff (changelog generation)

## 2026-08-12 02:47 CDT — PR #99 shipped: XXE hardening for DOCX extraction

**Status: pushed to origin, remote SHA verified, PR open awaiting maintainer merge.**

Three-round contribution fixing an XXE (XML External Entity) gap in `book_to_skill/parsers/docx.py`:

1. **28bc821a** (2026-08-05) — `extract_docx_with_zipfile()` made self-defending: calls `validate_docx_xml_safety()` unconditionally so a direct call (bypassing `extract_docx()`) still rejects malicious DOCTYPE/ENTITY declarations. Dropped an earlier `defusedxml` dependency swap per maintainer's request (stdlib `ElementTree` on 3.9+ doesn't expand external entities once the pre-scan guard is in place — a new dependency would guard a door already bricked shut).
2. **c55cb5f9 / ceff4a21** (2026-08-10) — Moved validation out of `extract_docx()` (which double-scanned every archive) and into each leaf parser instead, so the guarantee runs exactly once no matter which parser handles the file. Added the same self-defense to `extract_docx_with_python_docx()`, which had none before.
3. **5e4069c** (2026-08-12) — Maintainer's final review caught that the python-docx-path validation call sat *above* the `try` block, so an absent python-docx still paid the full archive scan before ImportError. Moved the call inside `try`, directly after `import docx` — a parser that isn't installed parses nothing, so skipping validation on ImportError gives up no safety. Added `test_extract_docx_validates_once_when_python_docx_unavailable`, pinning `validate_docx_xml_safety` to exactly 1 call through `extract_docx()` in that case.

**Verified before each push:** full test suite (275 passed/0 failed as of 5e4069c), `ruff check .` clean, `vuln-hunter scan_diff` clean (one pre-existing finding on `extract_docx_with_zipfile`'s stdlib `ElementTree` usage — unrelated to this diff, filed separately as [book-to-skill#140](https://github.com/virgiliojr94/book-to-skill/issues/140), previously rejected by the maintainer as unnecessary given the pre-scan guard). A `/code-review high` pass on the final commit found no correctness bugs (8 finder angles, 4 low-priority adjacent notes — one by-design, one pre-existing/out-of-scope, one speculative, one minor test-duplication cleanup — none acted on, all documented in the PR-99 vault entry).

**Open:** awaiting maintainer `virgiliojr94` merge. Separately filed [book-to-skill#140](https://github.com/virgiliojr94/book-to-skill/issues/140) for the pre-existing `defusedxml`-vs-stdlib finding on the zipfile parser, scoped out of PR #99 per maintainer's explicit "one line and a test, then I merge" ask.
