# Publication Spacing and Homepage Label Implementation Plan

> **For agentic workers:** REQUIRED: Use $subagent-driven-development (if subagents available) or $executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tighten standalone publication spacing and identify the homepage list as selected corresponding-author publications.

**Architecture:** Make one scoped CSS value change and one scoped homepage copy addition. Protect both with exact regression assertions and run the existing suite before pushing.

**Tech Stack:** Static HTML, CSS, Python `unittest`.

---

## Chunk 1: Scoped presentation update

### Task 1: Tighten spacing and add the homepage label

**Files:**
- Modify: `css/hugo-academic.css`
- Modify: `index.html`
- Modify: `tests/test_homepage_content.py`
- Modify: `tests/test_publications_page.py`

- [ ] **Step 1: Write failing tests**

Assert that `.publications-page .publication-entry` uses `margin-bottom: 12px`, and that `Selected corresponding-author publications.` appears once directly after the `Recent Publications` heading and before `More Publications`.

- [ ] **Step 2: Run focused tests and confirm they fail**

Run the two new focused `unittest` cases. Expected: both fail before implementation.

- [ ] **Step 3: Implement the minimal changes**

Change the standalone-page entry margin from `18px` to `12px`. Add a short paragraph containing the approved sentence below the homepage heading.

- [ ] **Step 4: Verify**

Run the focused cases, the full `unittest` suite, and `git diff --check`. Expected: all pass and no whitespace errors.

- [ ] **Step 5: Commit and push**

Commit only the scoped implementation and tests, then push `master`.
