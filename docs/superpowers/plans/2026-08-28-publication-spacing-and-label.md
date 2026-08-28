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

Add `test_publication_entries_use_compact_spacing` to assert that `.publications-page .publication-entry` uses `margin-bottom: 12px`. Add `test_recent_publications_has_corresponding_author_label` to assert that `Selected corresponding-author publications.` appears once directly after the `Recent Publications` heading and before `More Publications`.

- [ ] **Step 2: Run focused tests and confirm they fail**

Run:

```powershell
python -m unittest tests.test_publications_page.PublicationsPageTests.test_publication_entries_use_compact_spacing -v
python -m unittest tests.test_homepage_content.HomepageContentTests.test_recent_publications_has_corresponding_author_label -v
```

Expected: both fail before implementation.

- [ ] **Step 3: Implement the minimal changes**

Change the standalone-page entry margin from `18px` to `12px`. Add a short paragraph containing the approved sentence below the homepage heading. Update the existing homepage preservation normalization and publications-section canonical hash only for this approved insertion so the preservation tests continue to reject unrelated changes.

- [ ] **Step 4: Verify**

Run:

```powershell
python -m unittest tests.test_publications_page.PublicationsPageTests.test_publication_entries_use_compact_spacing -v
python -m unittest tests.test_homepage_content.HomepageContentTests.test_recent_publications_has_corresponding_author_label -v
python -m unittest discover -s tests -v
git diff --check
```

Expected: both focused cases pass, all 68 existing tests plus the 2 new tests pass, and `git diff --check` prints no errors.

- [ ] **Step 5: Commit and push**

Run `git branch --show-current` and require `master`. Inspect `git diff -- css/hugo-academic.css index.html tests/test_homepage_content.py tests/test_publications_page.py`, stage only those four files, commit them, verify the workspace is clean, then run `git push origin master`.
