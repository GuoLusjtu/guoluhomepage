# Homepage SEO Title and LinkedIn Implementation Plan

> **For agentic workers:** REQUIRED: Use $subagent-driven-development (if subagents available) or $executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the existing homepage title and add one accessible LinkedIn icon after GitHub, with no other production changes.

**Architecture:** Treat `index.html` as the sole production artifact. Add a narrow static regression contract first, then perform exactly two localized edits and verify the remainder of the file through title/LinkedIn-aware byte canonicalization.

**Tech Stack:** Static HTML5, bundled Font Awesome 4.6.1, Python standard-library `unittest`.

---

## Chunk 1: Test-driven implementation

### Task 1: Define the SEO and LinkedIn contract

**Files:**
- Modify: `tests/test_homepage_content.py`

- [ ] Add a test requiring exactly one `<title>` whose source is `<title>Guo Lu (鲁国) | SJTU | Video Coding &amp; Generative AI</title>` and whose decoded text is `Guo Lu (鲁国) | SJTU | Video Coding & Generative AI`.
- [ ] Assert `og:title` and `twitter:title` remain absent, while the existing meta description and canonical URL retain their exact current values.
- [ ] Add a test requiring exactly one LinkedIn `<li>` immediately after the existing GitHub item inside `ul.social-icon`, with exact URL, `aria-label="LinkedIn"`, no `target`/`rel`, and exact `<i class="fa fa-linkedin big-icon" aria-hidden="true"></i>`.
- [ ] Assert the profile social order is Contact, Google Scholar, GitHub, LinkedIn and that no LinkedIn URL appears in Contact or elsewhere.
- [ ] Add a fixed byte-level preservation guard that canonicalizes only the old/new title element and absent/present exact LinkedIn `<li>` before hashing the rest of `index.html`.
- [ ] Run focused and full tests; expect failures only for the old title and absent LinkedIn entry.
- [ ] Commit as `test: define SEO title and LinkedIn entry`.

### Task 2: Apply the two homepage edits

**Files:**
- Modify: `index.html`

- [ ] Replace only the existing title element with `<title>Guo Lu (鲁国) | SJTU | Video Coding &amp; Generative AI</title>`.
- [ ] Insert the exact LinkedIn list item immediately after GitHub, following existing indentation and whitespace style.
- [ ] Run focused tests and the complete suite; expect all tests `OK`.
- [ ] Decode `index.html` as strict UTF-8 and run `git diff --check`.
- [ ] Commit as `feat: update SEO title and add LinkedIn`.

## Chunk 2: Review and handoff

### Task 3: Verify scope and report

**Files:**
- Verification only

- [ ] Obtain specification and code-quality approval.
- [ ] Run a fresh complete test suite, strict UTF-8 check, and base-to-HEAD `git diff --check`.
- [ ] Confirm the production diff contains only the title replacement and LinkedIn `<li>` insertion in `index.html`; confirm no CSS, JavaScript, body text, metadata additions, or other production files changed.
- [ ] Keep the commits local; do not push.
- [ ] Report changed files and fields, and provide the exact before/after production diff requested by the user.
