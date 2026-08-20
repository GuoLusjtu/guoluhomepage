# About Me Heading Implementation Plan

> **For agentic workers:** REQUIRED: Use $subagent-driven-development (if subagents available) or $executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the approved semantic About Me heading and spacing above the homepage Bio paragraph.

**Architecture:** Add one heading to the existing Bio description column and one narrowly scoped CSS rule. Protect placement, text, styling, and all existing Bio/Join Us content with static regression tests.

**Tech Stack:** Static HTML5, CSS3, Python standard-library `unittest`, GitHub Pages.

---

## Chunk 1: Test-driven change

### Task 1: Add a failing About Me contract

**Files:**
- Modify: `tests/test_homepage_content.py`

- [ ] Add a test requiring exactly `<h3 id="about-me-heading" class="about-me-heading">About Me</h3>` as the first visible child of the Bio description column and immediately before its existing introductory paragraph.
- [ ] Parse only the `.about-me-heading` declaration block and require its declaration map to equal exactly `{margin: 0 0 16px, font-weight: 600}`; also reject an inline style attribute on the heading.
- [ ] Preserve the exact normalized Bio paragraph, Join Us callout, links, and unrelated homepage tests.
- [ ] Run the focused and full suite; expect one new RED failure caused by the missing heading and CSS.
- [ ] Commit as `test: define about me heading`.

### Task 2: Implement the heading and spacing

**Files:**
- Modify: `index.html`
- Modify: `css/hugo-academic.css`

- [ ] Insert the exact semantic heading immediately before the existing Bio paragraph.
- [ ] Add the exact scoped CSS rule without changing global heading or paragraph styles.
- [ ] Run focused tests and the complete suite; expect all tests `OK`.
- [ ] Decode changed files as strict UTF-8 and run `git diff --check`.
- [ ] Commit as `feat: add about me heading`.

## Chunk 2: Review and deployment

### Task 3: Verify and push

**Files:**
- Verification and Git operations only

- [ ] Obtain specification and code-quality approval for the complete implementation.
- [ ] Run a fresh full test suite, strict UTF-8 check, base-to-HEAD `git diff --check`, and local HTTP smoke test for heading order, content preservation, Join Us, and Cloudflare.
- [ ] Push `master` to `origin/master` and confirm the remote SHA.
- [ ] Wait for the matching GitHub Pages workflow to succeed, then verify the deployed homepage contains the exact heading and CSS.
