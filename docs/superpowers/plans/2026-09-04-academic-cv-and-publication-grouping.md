# Academic CV and Publication Grouping Implementation Plan

> **For agentic workers:** REQUIRED: Use $subagent-driven-development (if subagents available) or $executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a verified 4–6 page English academic CV and reorganize the complete Publications page by year, with journals before conferences.

**Architecture:** Treat `docs/publications-inventory.md` as the source of truth for both publication metadata and journal/conference classification. Generate the editable DOCX and public PDF from a versioned builder script, retain the legacy PDF URL as a byte-identical copy, and integrate one CV link into the existing homepage profile links. Preserve all existing publication records and their relative order within each type.

**Tech Stack:** Static HTML/CSS, Python `unittest`, bundled Python with `python-docx`, LibreOffice-based DOCX renderer, GitHub Pages.

**Bundled toolchain:** Before document work, call the workspace dependency loader. Use only `C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` and `C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe`, or their updated paths returned by that loader. Do not use system Python or Node. The document renderer is `C:\Users\user\.codex\plugins\cache\openai-primary-runtime\documents\26.903.11726\skills\documents\render_docx.py`; render QA output goes to `C:\Users\user\AppData\Local\Temp\guo-lu-cv-render`.

---

## Chunk 1: Publications page grouping

### Task 1: Add classification contract tests

**Files:**
- Modify: `tests/test_publications_page.py`
- Create: `docs/publications-order-baseline.json`
- Read: `docs/publications-inventory.md`

- [ ] Before changing HTML, extract the current year-by-year title order from `publication/index.html` into `docs/publications-order-baseline.json`. Add a test proving this baseline contains the same 72 unique included titles as the inventory.
- [ ] Add helpers that read each included inventory row's `Type` and map `journal` to `Journal Articles` and `conference-main` to `Conference Papers`; use the baseline JSON, not inventory row order, as the relative-order authority.
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
- Read and verify: `https://icisee.sjtu.edu.cn/jiaoshiml/luguo.html`
- Download/read for stable historical facts only: `https://guolusjtu.github.io/guoluhomepage/paper/GuoLu.pdf`

- [ ] Save a compact evidence table in `docs/cv-content.md` that cites the exact source for every appointment, education, award, project, teaching, and service fact. For the official page, copy only explicitly visible content. Use the old CV only for stable education facts that agree with current sources; omit any field that cannot be corroborated. Never infer incomplete dates, roles, grant identifiers, or amounts.
- [ ] Start `docs/cv-content.md` with headings and an empty selected-publications list only.
- [ ] Add failing tests that require the exact 21-paper selection (all 19 homepage Recent Publications plus CVPR 2021 FVC and CVPR 2019 DVC) to resolve exactly once to included inventory rows, require evidence rows for non-publication facts, and reject placeholder text, invented grant identifiers/amounts, and unverified corresponding-author symbols.
- [ ] Run focused tests to confirm RED, then fill the verified facts and exact 21-paper list from the sources and rerun to GREEN.
- [ ] Commit content and tests.

### Task 4: Build the DOCX and PDF

**Files:**
- Create: `scripts/build_academic_cv.py`
- Create: `files/Guo-Lu-CV.docx`
- Create: `files/Guo-Lu-CV.pdf`
- Create: `paper/GuoLu.pdf`
- Test: `tests/test_cv_content.py`

- [ ] Use the document template picker if available; otherwise use the approved restrained single-column layout. Load the bundled workspace dependencies first.
- [ ] Immediately before authoring, run exactly once: `& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' 'C:\Users\user\.codex\plugins\cache\openai-primary-runtime\documents\26.903.11726\skills\documents\container_tools\mark_artifact_operation_started.mjs' --operation-kind create --expected-output-count 1 --output-format docx`.
- [ ] Implement a deterministic builder using bundled `python-docx`, native Title/Heading styles, real hyperlinks, page numbers, and logical reading order. The document Title is black with no border or rule; dark blue is limited to section headings. Do not use callout boxes.
- [ ] Generate DOCX with the bundled Python. Render with `& '<bundled-python>' 'C:\Users\user\.codex\plugins\cache\openai-primary-runtime\documents\26.903.11726\skills\documents\render_docx.py' 'files\Guo-Lu-CV.docx' --output_dir 'C:\Users\user\AppData\Local\Temp\guo-lu-cv-render' --emit_pdf`, then copy the verified rendered PDF to both public PDF paths byte-for-byte.
- [ ] Inspect every rendered page PNG at 100% and iterate until the CV is 4–6 pages with no clipping, overlap, orphaned headings, broken glyphs, or awkward page breaks. Re-render and reinspect all pages after every layout-related change.
- [ ] Add structural tests for 4–6 page count, searchable/selectable PDF text, native DOCX Title/Heading styles, absence of placeholders, and byte identity of the two PDF paths. Inspect PDF URI annotations and require exact clickable links for the homepage, Google Scholar, GitHub, and LinkedIn.
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

- [ ] Run `& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -v`.
- [ ] Run `git diff --check` and confirm a clean worktree.
- [ ] Serve the site locally and confirm `/`, `/publication/`, `/files/Guo-Lu-CV.pdf`, and `/paper/GuoLu.pdf` return HTTP 200. Confirm the homepage contains exactly one CV link with the canonical href, both PDFs are non-empty with `application/pdf` responses, and their SHA-256 hashes match.
- [ ] Re-render the final DOCX and inspect every PNG; verify PDF text and links one last time.
- [ ] Request final specification and code-quality reviews, resolving any important findings.
- [ ] Confirm the feature worktree is clean. Fetch `origin`, verify `master` has no unexpected remote divergence, and merge without force or history rewriting. On `master`, rerun the full suite and `git diff --check`, push `master`, verify the remote SHA, then verify the public homepage, Publications page, and both CV URLs after GitHub Pages deploys.
