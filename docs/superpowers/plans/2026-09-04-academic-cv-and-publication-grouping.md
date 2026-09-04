# Academic CV and Publication Grouping Implementation Plan

> **For agentic workers:** REQUIRED: Use $subagent-driven-development (if subagents available) or $executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a verified 4–6 page English academic CV and reorganize the complete Publications page by year, with journals before conferences.

**Architecture:** Treat `docs/publications-inventory.md` as the source of truth for both publication metadata and journal/conference classification. Generate the editable DOCX and public PDF from a versioned builder script, retain the legacy PDF URL as a byte-identical copy, and integrate one CV link into the existing homepage profile links. Preserve all existing publication records and their relative order within each type.

**Tech Stack:** Static HTML/CSS, Python `unittest`, bundled Python with `python-docx`, LibreOffice-based DOCX renderer, GitHub Pages.

---

## Chunk 1: Publications page grouping

### Task 1: Add classification contract tests

**Files:**
- Modify: `tests/test_publications_page.py`
- Read: `docs/publications-inventory.md`

- [ ] Add helpers that read each included inventory row's `Type` and map `journal` to `Journal Articles` and `conference-main` to `Conference Papers`.
- [ ] Add failing tests proving all 72 entries appear exactly once, each entry is under the inventory-authorized subgroup, empty groups are omitted, Journal precedes Conference within a year, and each subgroup preserves the former relative order.
- [ ] Run the new focused tests with the bundled Python executable and confirm they fail because subgroup wrappers/headings do not yet exist.
- [ ] Commit the failing contract tests.

### Task 2: Reorganize publication markup and styles

**Files:**
- Modify: `publication/index.html`
- Modify: `css/hugo-academic.css`
- Test: `tests/test_publications_page.py`

- [ ] Within each existing year, wrap journal entries in a labelled `publication-type-group` and conference entries in a second group, omitting empty groups.
- [ ] Keep year headings as `h2`, add subgroup headings as `h3`, and change publication titles from `h3` to `h4`.
- [ ] Add minimal scoped CSS for subgroup spacing and headings while preserving desktop/mobile year layout.
- [ ] Run focused grouping/accessibility tests, then the complete suite; expect all tests to pass and the record count to remain 72.
- [ ] Commit the page and style changes.

## Chunk 2: Academic CV source and artifacts

### Task 3: Define and verify CV content data

**Files:**
- Create: `docs/cv-content.md`
- Create: `tests/test_cv_content.py`
- Read: `index.html`
- Read: `docs/publications-inventory.md`

- [ ] Create a structured content file containing only verified appointment, education, award, project, teaching, and service facts, with the official faculty URL recorded as provenance.
- [ ] Record the exact 21 selected-paper titles: all 19 homepage Recent Publications plus the verified CVPR 2021 FVC and CVPR 2019 DVC entries.
- [ ] Add failing tests that require all 21 titles to resolve exactly once to included inventory rows and reject placeholder text, invented grant identifiers/amounts, and unverified corresponding-author symbols.
- [ ] Run focused tests to confirm RED, fill the verified content, then rerun to GREEN.
- [ ] Commit content and tests.

### Task 4: Build the DOCX and PDF

**Files:**
- Create: `scripts/build_academic_cv.py`
- Create: `files/Guo-Lu-CV.docx`
- Create: `files/Guo-Lu-CV.pdf`
- Create: `paper/GuoLu.pdf`
- Test: `tests/test_cv_content.py`

- [ ] Use the document template picker if available; otherwise use the approved restrained single-column layout.
- [ ] Immediately before authoring, run `mark_artifact_operation_started.mjs` once with operation kind `create`, expected output count `2`, and output format `docx,pdf` as supported by the marker.
- [ ] Implement a deterministic builder using bundled `python-docx`, native Title/Heading styles, real hyperlinks, dark-blue headings, page numbers, and logical reading order.
- [ ] Generate DOCX, render it with the packaged `render_docx.py --emit_pdf`, and copy the verified PDF byte-for-byte to `paper/GuoLu.pdf`.
- [ ] Inspect every rendered page PNG at 100% and iterate until the CV is 4–6 pages with no clipping, overlap, orphaned headings, broken glyphs, or awkward page breaks.
- [ ] Add structural tests for page count, searchable PDF text, DOCX hyperlinks/headings, absence of placeholders, and byte identity of the two PDF paths.
- [ ] Run focused CV tests and commit the builder, content artifacts, compatibility copy, and tests.

## Chunk 3: Homepage integration and final verification

### Task 5: Add the homepage CV link

**Files:**
- Modify: `index.html`
- Modify: `tests/test_homepage_content.py`

- [ ] Add a failing test requiring exactly one visible `CV` link in the existing profile/social-links list with the canonical PDF URL.
- [ ] Run it to confirm RED, add the minimal list item, and update preservation normalization only for this exact approved insertion.
- [ ] Run the focused test and complete suite; expect GREEN without unrelated homepage changes.
- [ ] Commit homepage integration and tests.

### Task 6: Verify the complete feature

**Files:**
- Verify all files changed since the design-spec base commit.

- [ ] Run `python -m unittest discover -s tests -v` with the bundled runtime.
- [ ] Run `git diff --check` and confirm a clean worktree.
- [ ] Serve the site locally and confirm `/`, `/publication/`, `/files/Guo-Lu-CV.pdf`, and `/paper/GuoLu.pdf` return HTTP 200.
- [ ] Re-render the final DOCX and inspect every PNG; verify PDF text and links one last time.
- [ ] Request final specification and code-quality reviews, resolving any important findings.
- [ ] Merge the feature branch into `master`, rerun the full suite, push `master`, and verify the public homepage, Publications page, and both CV URLs after GitHub Pages deploys.
