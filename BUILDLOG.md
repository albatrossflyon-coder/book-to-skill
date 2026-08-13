# BUILDLOG

`C:\Repos\book-to-skill` — fork of [virgiliojr94/book-to-skill](https://github.com/virgiliojr94/book-to-skill) (upstream), pushed to `albatrossflyon-coder/book-to-skill` (origin, write access). OSS contribution repo, not an Albatross AI product — this log tracks our contribution work only, not the upstream project as a whole.

**Note on clones (added 2026-08-12):** there is a second, independent local clone of this same fork at `C:\Repos\External\book-to-skill`, used for the personalmba.com/Kaufman evaluation, the Kaizen layer experiment, and the trafilatura fix below. Same GitHub remotes, separate working trees — a commit in one doesn't appear in the other until fetched. Worth consolidating into one clone eventually; not done yet.

## Tech Stack

- **Languages:** Python (>=3.9)
- **Frameworks/Libraries:** hatchling (build), pytest, ruff, optional parser deps (python-docx, pypdf, pdfminer.six, ebooklib, beautifulsoup4, striprtf, docling, **trafilatura** — added 2026-08-12, real HTML boilerplate detection, optional via `[html]` extra)
- **Dev Tools:** GitHub Actions CI, git-cliff (changelog generation), uv (package manager in the `External` clone — note: `uv run <tool>` can silently resolve to the wrong Python if the tool isn't a declared project dependency; verify with `.venv/Scripts/python.exe -m <tool>` instead)

## 2026-08-13 — PR #142 review round: two required changes shipped, question answered, rebased onto master

**Status: pushed (SHA `6145982`, remote-verified via `gh api`), reply comment posted (https://github.com/virgiliojr94/book-to-skill/pull/142#issuecomment-5286645736), still open awaiting the maintainer's next look.**

Maintainer reviewed #142 same-day. Praised the measurement (61 real pages, named corpus, honest accounting), flagged two things before he'd take it, and asked one question:

1. **`[html]` extra's weight was undocumented** — `docs/install.md` never mentioned it pulls trafilatura's real 17-package HTML stack (lxml, date parser, timezone DB, URL classifier). Fixed: one line under the pip install example.
2. **The new primary path was invisible** — not registered in `DEPENDENCY_GROUPS` (`--check` still reported HTML as bs4-only), and `extract_html_content()` returned one of two materially different documents with zero indication which ran. Fixed: trafilatura registered as primary module in the HTML group; added "Trying X..." prints mirroring `extract_docx()`'s existing style.
3. **Question:** did the 61-page corpus have any code-shaped content, to know whether `include_formatting=False` was tested against it? Checked the actual corpus (not memory) — personalmba.com prose only, two book chapters, no code anywhere. Answered honestly: untested territory.

**Real gotcha:** rebased onto what I thought was `origin/master` to pick up the maintainer's own #155 fix (his separate regression from #141, POSIX permission asserts failing on Windows) — but `origin` here is our fork, which hadn't synced his merge yet. Rebased onto `upstream/master` instead once caught by actually running the full suite and seeing the same 3 failures persist. 2 of 3 fixed by #155 as expected; the third (`test_prepare_output_dir_rejects_symlink`) needs Windows symlink-creation privileges (Developer Mode/elevation) this session doesn't have — confirmed unrelated to this PR's diff, moot on the maintainer's `ubuntu-latest` CI.

Verified both with and without `trafilatura` installed in `.venv` before pushing (the exact gap that caused the 08-12 CI break) — 474 passed / 0 failed / 7 skipped-without-trafilatura with it installed.

## 2026-08-12 — PR #142 shipped: trafilatura for real HTML boilerplate detection

**Status: pushed to fork, remote SHA verified, PR open (https://github.com/virgiliojr94/book-to-skill/pull/142) awaiting maintainer review.**

**How the bug was found (2026-08-08, TEDx→book-to-skill evaluation):** ran `scripts/extract.py` against 61 real pages scraped from personalmba.com (Josh Kaufman's official free-excerpt site for *The Personal MBA*), across two full chapters (Value Creation, Marketing). A repeated footer block (book ad + author bio + copyright notice) appeared 183 times in the combined extracted text. Root-caused by reading `extract_html_content()` in `book_to_skill/parsers/html.py` directly: it strips only `<script>`/`<style>`/`<head>` on both the bs4 path and the stdlib fallback path — neither does real main-content vs. page-chrome detection.

**The fix:** wired `trafilatura` in as the new primary extraction path, falling through to the existing bs4 path and then the stdlib parser on any failure (missing dependency, low-quality/whitespace result, or a parse exception) — matching the function's existing graceful-degradation design. Kept optional (`pip install book-to-skill[html]`) so the base install stays dependency-free.

**Verified:** re-ran extraction against the same 61 real pages — boilerplate dropped from 183 to 69 hits. The actual footer (ad block, copyright/trademark notice) is fully eliminated; the remaining 69 are one line — the site's own page masthead, appearing once per page, structurally closer to real article lead-in than nav/footer chrome. 5 new deterministic tests added (`tests/test_html_boilerplate_extraction.py`) covering the fallback contract. Full suite: 415 passed, 3 failed — confirmed via `git log` those 3 are pre-existing (added by the maintainer's own latest commit #141, asserting POSIX permission bits that don't hold on Windows), unrelated to this change.

**Real gotchas hit building this:**
1. The working branch also carried an unrelated local-only "Kaizen self-evolving layer" experiment — had to cut a fresh branch off current `origin/master` and manually reapply just the relevant files to keep this a real "one focused change" PR.
2. `uv run pytest`/`uv run ruff` silently resolved to an unrelated Python install from PATH instead of this project's own `.venv` — two verification passes looked green but weren't actually testing against an environment with `trafilatura` installed. Fixed by installing test tools directly into `.venv`.
3. This `BUILDLOG.md` file appeared to have gone missing between 08-11 and 08-12 — turned out to be a false alarm: the `C:\Repos\External\book-to-skill` clone's local `master` branch pointer had drifted to track `origin/master` (upstream) instead of `fork/master` (ours), after running `git fetch origin master`. The real file was safe on `fork/master` the whole time (commit `300506d`). Lesson: after fetching upstream directly by name (`git fetch origin <branch>`), double-check which remote a local branch is actually tracking before assuming a file is gone.

**Open:** watching PR #142 for maintainer review/comments.

## 2026-08-12 19:01 CDT — PR #142 CI was actually red; fixed and reverified

**Status: pushed to fork, PR description edited, CI now green (11/11 checks pass), remote SHA verified.**

**What was found:** the "415 passed, 3 failed (unrelated)" claim above was a real local-only verification run with `trafilatura` installed in `.venv`. GitHub's actual CI matrix (`pip install pytest` only, no extras — deliberately dependency-free base tier) never had `trafilatura` present, so the 4 new tests that `patch("trafilatura.extract", ...)` failed with `ModuleNotFoundError` on every Python version (3.9–3.13). Separately, the PR description's Checklist section had one `[ ]` item ("`validate_skill.py` passes — n/a, not touched") — the repo's PR-description-check script fails on any literal `[ ]` in that section regardless of an "n/a" justification (same failure mode as PR #99, see [[feedback-check-pr-template-before-contributing]]).

**The fix:** guarded the 4 trafilatura-dependent tests with `pytest.importorskip("trafilatura")`, matching the existing bs4 skip idiom already used in `test_html_block_boundaries.py`. Checked the literal box in the PR description. Verified both conditions directly: with trafilatura installed (`.venv`), all 5 tests run and pass; with a bare Python (no trafilatura, mirroring real CI), 4 skip and 1 (the `sys.modules`-mocked "not installed" case) still runs and passes. Pushed commit `b9ad727`; CI went fully green (`test (py3.9)`–`test (py3.13)`, lint, security, CodeQL, dependency review, smoke, PR description check, PR title — 11/11).

**Lesson:** "tests pass locally" isn't "tests pass in CI" when the local run has optional extras installed that CI deliberately doesn't — verify against the same dependency surface CI actually uses, not just a green local run.

## 2026-08-12 02:47 CDT — PR #99 shipped: XXE hardening for DOCX extraction

**Status: MERGED 2026-08-12T13:17:10Z by virgiliojr94. Issue #140 also closed the same day, on solid technical grounds. Fully closed, no open action.**

Three-round contribution fixing an XXE (XML External Entity) gap in `book_to_skill/parsers/docx.py`:

1. **28bc821a** (2026-08-05) — `extract_docx_with_zipfile()` made self-defending: calls `validate_docx_xml_safety()` unconditionally so a direct call (bypassing `extract_docx()`) still rejects malicious DOCTYPE/ENTITY declarations. Dropped an earlier `defusedxml` dependency swap per maintainer's request (stdlib `ElementTree` on 3.9+ doesn't expand external entities once the pre-scan guard is in place — a new dependency would guard a door already bricked shut).
2. **c55cb5f9 / ceff4a21** (2026-08-10) — Moved validation out of `extract_docx()` (which double-scanned every archive) and into each leaf parser instead, so the guarantee runs exactly once no matter which parser handles the file. Added the same self-defense to `extract_docx_with_python_docx()`, which had none before.
3. **5e4069c** (2026-08-12) — Maintainer's final review caught that the python-docx-path validation call sat *above* the `try` block, so an absent python-docx still paid the full archive scan before ImportError. Moved the call inside `try`, directly after `import docx` — a parser that isn't installed parses nothing, so skipping validation on ImportError gives up no safety. Added `test_extract_docx_validates_once_when_python_docx_unavailable`, pinning `validate_docx_xml_safety` to exactly 1 call through `extract_docx()` in that case.

**Verified before each push:** full test suite (275 passed/0 failed as of 5e4069c), `ruff check .` clean, `vuln-hunter scan_diff` clean (one pre-existing finding on `extract_docx_with_zipfile`'s stdlib `ElementTree` usage — unrelated to this diff, filed separately as [book-to-skill#140](https://github.com/virgiliojr94/book-to-skill/issues/140), previously rejected by the maintainer as unnecessary given the pre-scan guard). A `/code-review high` pass on the final commit found no correctness bugs (8 finder angles, 4 low-priority adjacent notes — one by-design, one pre-existing/out-of-scope, one speculative, one minor test-duplication cleanup — none acted on, all documented in the PR-99 vault entry).

**Open:** awaiting maintainer `virgiliojr94` merge. Separately filed [book-to-skill#140](https://github.com/virgiliojr94/book-to-skill/issues/140) for the pre-existing `defusedxml`-vs-stdlib finding on the zipfile parser, scoped out of PR #99 per maintainer's explicit "one line and a test, then I merge" ask.
