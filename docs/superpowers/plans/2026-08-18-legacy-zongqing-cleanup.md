# Legacy Zongqing Content Cleanup Implementation Plan

> **For agentic workers:** REQUIRED: Use $subagent-driven-development (if subagents available) or $executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove copied Zongqing Lu publication/tag/archive material, retain a useful publication redirect, and identify every retained page/feed as Guo Lu without changing the current homepage publications.

**Architecture:** Treat the generated static site as the production artifact. Replace the legacy publication collection with a canonical meta-refresh page, delete publication-derived tag/feed artifacts, simplify the 404 page, and mechanically update owner identity only in retained legacy shells. Regression tests audit the exact retained filesystem rather than preserving obsolete generated-page counts.

**Tech Stack:** Static HTML/XML, Python 3.12 standard-library `unittest`, GitHub Pages.

---

## Chunk 1: Regression contract and content cleanup

### Task 1: Replace obsolete preservation assertions with cleanup requirements

**Files:**
- Modify: `tests/test_homepage_content.py`

- [ ] Assert the raw `<section id="publications">...</section>` bytes have fixed SHA-256 `8d558fcde05bd6159224aee46442921278d3f1994919fcb02b8e1df2de403f3a`, so the test independently proves the cleanup does not change it.
- [ ] Replace `test_legacy_zongqing_lu_footers_are_preserved` and obsolete exact 31/19/12 generated-page assumptions with assertions over the new retained filesystem. Explicitly migrate the redirect-stub byte snapshot, body-page News/Cloudflare discovery, and exact `#projects` anchor-count tests; classify the new publication redirect by its path/markup rather than absence of `</body>`.
- [ ] Add a test requiring `publication/index.html` to be a redirect stub whose canonical URL and refresh target are exactly `https://guolusjtu.github.io/guoluhomepage/#publications`.
- [ ] Add tests requiring `publication/index.xml`, every file below `tags/`, copied root/generated feeds (`index.xml`, `home/index.xml`, `project/index.xml`, `categories/index.xml`), and copied citation `files/citations/infocom18.bib` to be absent. Preserve project images and other project assets because the approved design retains `/project/` content.
- [ ] Add tests requiring retained HTML/XML site-owner metadata/chrome to contain no `Zongqing` (case-insensitive), while the homepage Publications section matches the recorded pre-cleanup bytes.
- [ ] Add tests requiring `404.html` to contain no copied publication titles or `/publication/<slug>/` links and to keep a homepage recovery link.
- [ ] Add tests parsing `sitemap.xml`: allow only retained real routes, and reject publication-detail, tag, legacy News-detail, Home subsection, and Project-detail URLs.
- [ ] Add a retained-link audit that rejects any HTML `href` targeting a removed local route.
- [ ] Run `python.exe -B -m unittest discover -s tests -v`; expect failures only from the new cleanup contract and any old tests whose assumptions still need deliberate migration.
- [ ] Commit the verified RED tests as `test: define legacy content cleanup`.

### Task 2: Remove copied archives and normalize retained identity

**Files:**
- Replace: `publication/index.html`
- Delete: `publication/index.xml`
- Delete: `tags/**`
- Delete: `index.xml`
- Delete: `home/index.xml`
- Delete: `project/index.xml`
- Delete: `categories/index.xml`
- Delete: `files/citations/infocom18.bib`
- Modify: `404.html`
- Modify: `project/index.html`
- Modify: `sitemap.xml`
- Modify: any other retained HTML found by the identity audit, excluding homepage publication content

- [ ] Replace `publication/index.html` with a UTF-8 HTML redirect page containing canonical and meta-refresh targets for `https://guolusjtu.github.io/guoluhomepage/#publications`, a visible fallback link, and exactly one existing Cloudflare beacon immediately before `</body>`.
- [ ] Delete the copied publication RSS and the complete publication-derived `tags/` tree.
- [ ] Delete obsolete generated feeds that expose copied homepage/project/category content.
- [ ] Delete the copied `files/citations/infocom18.bib`; preserve project images and assets.
- [ ] Simplify `404.html` to retain the common navigation/analytics shell and a concise “Page not found” recovery link, removing all old recent-publication/post lists.
- [ ] Update retained legacy HTML identity fields: author `Guo Lu`, brand/title `Guo Lu&#39;s Homepage`, and footer `&copy; 2020&ndash;2026 Guo Lu`.
- [ ] Convert the 14 `/tags/...` anchors in retained `project/index.html` to plain text while preserving their labels and surrounding project content.
- [ ] Reduce `sitemap.xml` to retained, indexable real pages (`/guoluhomepage/`, `/guoluhomepage/news/`, and `/guoluhomepage/project/`); do not advertise the publication redirect.
- [ ] Do not touch the current homepage Publications section, News content/feed, Cloudflare beacon token, or active News navigation.
- [ ] Run the focused cleanup tests and confirm GREEN.
- [ ] Run the entire test suite and fix only cleanup-related stale assumptions until all tests pass.
- [ ] Commit production cleanup as `chore: remove legacy Zongqing content`.

## Chunk 2: Verification and deployment

### Task 3: Audit static output locally

**Files:**
- Verification only

- [ ] Run the full suite with bundled Python: `C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m unittest discover -s tests -v`; expect all tests `OK`.
- [ ] Run `rg -n -i "zongqing" . --glob '!docs/superpowers/**' --glob '!tests/**' --glob '!**/.worktrees/**'`; expect no production matches.
- [ ] Run `git diff --check <cleanup-base>..HEAD`; expect no whitespace errors.
- [ ] Start a local static HTTP server and verify `/` and `/news/` return 200. Fetch `/publication/` without following its external redirect and parse its exact canonical, refresh, fallback target, and one Cloudflare beacon. Verify `/404.html` contains no copied publication list.
- [ ] Parse every retained local HTML link and assert it does not point to a deleted publication-detail, tag, feed, or other removed route.
- [ ] Stop the exact server PID and verify the local port is no longer listening.
- [ ] Review the complete diff against the design boundary, especially the unchanged homepage Publications section.

### Task 4: Integrate and deploy

**Files:**
- Git operations only

- [ ] Confirm the worktree is clean and all intended commits are on `master`.
- [ ] Push `master` to `origin/master`.
- [ ] Verify the GitHub Pages deployment completes successfully.
- [ ] Verify production `/`, `/publication/`, `/news/`, and an unknown URL; confirm the homepage remains current, the publication redirect lands at `#publications`, News remains available, and copied Zongqing content is not exposed.
