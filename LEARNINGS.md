# Learnings

How this converter gets better with use instead of running the same way every time regardless of history (the Kaizen pattern). Not a chat log — only non-obvious things worth remembering: an extraction quirk for a specific format/genre, a default that turned out wrong for a class of book, a failure mode nobody expected.

**Format:** one entry per topic (extraction, depth/budget calibration, format-specific quirks, or "general"). Keep each entry to a few lines — a fact plus why it matters, not a transcript. Prune entries that stop being true (a since-fixed extractor bug, a changed default) rather than let them accumulate as noise.

```
## <topic>

- <date> — <what was learned, and why it matters next time>
```

---

## extraction

- 2026-08-08, 12:48 PM CDT — **HTML extraction includes repeated page chrome (nav/footer/ads), not just article content.** Found running the converter against 61 real pages scraped from personalmba.com (Josh Kaufman's official free excerpt site) across two chapters. `extract_html_content()` in `book_to_skill/parsers/html.py` strips only `<script>`, `<style>`, `<head>` — both the bs4 path and the stdlib fallback path convert everything else to text indiscriminately. A repeated footer block (book ad + author bio + copyright notice) appeared **179 times** in the combined extracted text across 61 source pages. Installing `beautifulsoup4` did NOT fix this — confirmed by re-running extraction before/after install, count stayed at 179 both times, because bs4 is only used for more-robust parsing here, not main-content detection. **Root cause confirmed by reading the actual source**, not assumed. A real fix would need genuine content-boundary detection (e.g. `readability-lxml` or `trafilatura`, purpose-built for "find the article, discard the chrome") — this codebase has neither. Worth proposing upstream once we have a concrete before/after fix to show, not just the finding alone.

## general

*(no entries yet — this fills in as the converter runs into real, non-obvious things worth remembering)*

---

## Usage Log

The actual evidence trail. One line every time Step 1 checks this file:

```
- <date> — checked | hit: <which entry, what it saved> | miss: nothing relevant | empty: no entries yet
```

- 2026-08-08, 12:48 PM CDT — checked | empty: no entries yet (first real run) | outcome: added the "extraction" entry above after finding a genuine gap in `extract_html_content()`. Note: this run was done by manually invoking `scripts/extract.py` directly, not through the formal SKILL.md workflow — worth a real Step-1-through-Step-8 run next session to test the full loop, not just the extraction step in isolation.
- 2026-08-12 — checked | hit: the "extraction" entry above — confirmed it was still the exact, current root cause (re-read `extract_html_content()` before touching it) rather than re-diagnosing from scratch. This run went through the real start-to-finish Step 1-8 loop the prior entry asked for.
