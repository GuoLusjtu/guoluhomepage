# Join Us Callout Implementation Plan

> **For agentic workers:** REQUIRED: Use $subagent-driven-development (if subagents available) or $executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Bio recruitment warning text with the approved accessible Join Us callout and correct the Publications Google Scholar URL without changing unrelated homepage content.

**Architecture:** Keep semantic content in `index.html` and reusable presentation in the existing site stylesheet. Extend the static-content unittest suite first, then make the smallest HTML/CSS changes necessary to satisfy the approved design.

**Tech Stack:** Static HTML5, CSS3, Python standard-library `unittest`, GitHub Pages.

---

## Chunk 1: Test-driven implementation

### Task 1: Define the callout and URL regression contract

**Files:**
- Modify: `tests/test_homepage_content.py`

- [ ] Add a focused test that extracts `#bio` and requires exactly one labelled `aside.join-us-callout`, `h3#join-us-heading`, exact recruitment paragraph, exact decoded Chinese-homepage label plus arrow, and exact existing URL.
- [ ] Require the obsolete red inline recruitment span and old `CV/resume` wording to be absent.
- [ ] Require source `2020&ndash;2022`, correct decoded employment text, strict UTF-8, and no U+FFFD in `index.html` or `css/hugo-academic.css`.
- [ ] Require both homepage Google Scholar anchors to use exactly `https://scholar.google.com/citations?user=R9iwlJcAAAAJ&hl=en`, and reject `hl=en/`.
- [ ] Require `.join-us-callout` to use `background: #f4f8fb`, `border-left: 4px solid #2f6f9f`, `padding: 15px 17px`, and `border-radius: 3px`. Parse only that declaration block when rejecting fixed `width`/`height`.
- [ ] Require an `@media (max-width: 767px)` rule whose `.join-us-callout` declaration specifically reduces padding to `12px 14px`; do not accept an unrelated media rule.
- [ ] Require `.join-us-callout a` and `.join-us-callout a:visited` to use accessible `color: #2f6f9f`, plus `.join-us-callout a:hover` and `.join-us-callout a:focus` to use `color: #254f70` and `text-decoration: underline`.
- [ ] Run the focused tests and confirm RED for the missing callout/CSS, source employment-range entity, and bad Publications URL.
- [ ] Commit tests as `test: define join us callout`.

### Task 2: Implement the approved A callout

**Files:**
- Modify: `index.html`
- Modify: `css/hugo-academic.css`

- [ ] Close the Bio paragraph after the honors text and replace the old recruitment span plus separate Chinese link with the approved sibling `aside` structure.
- [ ] Use the exact recruitment copy and ASCII-safe source entities `&#20013;&#25991;&#20027;&#39029; &rarr;` for the Chinese link label.
- [ ] Preserve `2020&ndash;2022` and fix only the Publications Google Scholar URL by removing its trailing slash.
- [ ] Add the exact callout declarations `background: #f4f8fb`, `border-left: 4px solid #2f6f9f`, `padding: 15px 17px`, and `border-radius: 3px` to `css/hugo-academic.css`, without fixed dimensions; add `.join-us-callout { padding: 12px 14px; }` inside `@media (max-width: 767px)`.
- [ ] Style callout links and visited links with `#2f6f9f`; use `#254f70` plus underline for hover and keyboard focus, preserving sufficient contrast and a visible interaction state.
- [ ] Run focused tests, then the entire suite; expect all tests `OK`.
- [ ] Commit as `feat: add join us callout`.

## Chunk 2: Review, verification, and deployment

### Task 3: Verify and deploy

**Files:**
- Verification and Git operations only

- [ ] Run the full bundled-Python suite and `git diff --check`.
- [ ] Decode changed HTML/CSS as strict UTF-8 and verify no replacement character.
- [ ] Run a local HTTP smoke test; verify the Bio callout structure/text/link, corrected Scholar URL, one Cloudflare beacon, and responsive CSS source.
- [ ] Review the base-to-HEAD diff to confirm only the spec, plan, tests, `index.html`, and `css/hugo-academic.css` changed.
- [ ] Obtain final specification and code-quality approval.
- [ ] Push `master` to `origin/master`, confirm matching remote SHA, and verify the deployed homepage contains the Join Us card and corrected Scholar URL.
