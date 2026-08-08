# BUILDLOG — our local experiment work on book-to-skill

**This is our own tracking file for local experimentation, not part of the upstream project's documentation.** The real project uses `CHANGELOG.md` (generated from Conventional Commits via git-cliff) — this file exists only so Chris and Claude have a dated record of what was tried, found, and where things stopped, matching the same discipline used across all of Chris's own repos.

Branch: `experiment/kaizen-learnings`. Nothing in this branch has been pushed or proposed upstream.

---

## 2026-08-08, 12:48 PM CDT — Kaizen layer added + real gap found in HTML extraction, session paused here

### What happened, in order

1. **Added the Kaizen self-evolving layer** to book-to-skill's own converter workflow (`SKILL.md` Step 1 and Step 10, plus `LEARNINGS.md`) — see the `feat: add Kaizen self-evolving layer` commit. Purely local, held back from proposing upstream per book-to-skill's own `CONTRIBUTING.md`, which asks for evidence of benefit before a PR that adds weight to the always-loaded `SKILL.md`.

2. **Ran a real proof-of-concept**: fetched 61 real pages (Chapters 1 "Value Creation" and 2 "Marketing") from personalmba.com — Josh Kaufman's own official free-excerpt site for *The Personal MBA*, a legitimate free source (not a pirated copy; declined to look for those). Ran book-to-skill's actual `scripts/extract.py` against the real fetched files.

3. **Found a real, confirmed gap**, not assumed: the combined extracted text had a repeated footer block (book ad + author bio + copyright notice) appearing **179 times**. Suspected `beautifulsoup4` was missing; installed it (`pip install beautifulsoup4`, confirmed v4.15.0); re-ran extraction. **Count stayed at 179, unchanged.**

4. **Root-caused by reading the actual source**, not guessing: `book_to_skill/parsers/html.py`'s `extract_html_content()` strips only `<script>`, `<style>`, `<head>` on both the bs4 path and the stdlib-fallback path. Neither path has any main-content/boilerplate-detection logic — bs4 here only provides more-robust HTML *parsing*, not article-boundary *detection*. Confirmed this is not a Kaizen-related issue (Chris asked directly whether the Kaizen addition could be the cause; it is not — verified by reading the extraction code, which Kaizen never touches).

5. **Logged the finding in `LEARNINGS.md`** under a new "extraction" topic, plus a Usage Log entry — this is the first real Kaizen entry from actual use, not a hypothetical.

### Real fix, not yet built

A proper fix needs genuine main-content detection — a library purpose-built for "find the article, discard the chrome" (e.g. `readability-lxml`, `trafilatura`). Neither is in this codebase. Not attempted yet — the honest next step per Kaizen's own phase-gate rule (see `~/.claude/skills/_shared/kaizen/README.md`) is to build and verify a real before/after fix, then that becomes the evidence for a real upstream issue — not the finding alone.

### Where this picks up next session

- Build the actual `readability-lxml`/`trafilatura`-based fix for `extract_html_content()`, verify it against these same 61 real pages (should drop the 179-count toward ~2, one legitimate mention per unique page if any real body content happens to reference "the book").
- Once fixed and verified, this becomes real evidence for two things: (1) a genuine upstream issue/PR to book-to-skill, and (2) portfolio evidence — a real, checkable example of finding and fixing a bug in someone else's open-source project, not a resume claim.
- Continue the personalmba.com crawl (9 more chapters) once extraction quality is fixed, so the eventual generated skill isn't built on diluted text.
- Also still pending from earlier: Chris Lonsdale's books (legitimate access not yet sourced — no personalmba.com-style free official excerpt site found for him yet).
