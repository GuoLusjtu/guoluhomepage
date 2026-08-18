# Legacy Zongqing Content Cleanup Design

## Goal

Remove the copied Zongqing Lu publication archive and its generated discovery surfaces without altering Guo Lu's current homepage publications. Replace legacy site-owner identity strings with Guo Lu across retained site pages and feeds.

## Content changes

- Replace legacy site chrome and metadata such as `Zongqing's Homepage`, `meta name="author" content="Zongqing Lu"`, XML copyright fields, and legacy footers with Guo Lu identity.
- Use `Guo Lu's Homepage` for retained legacy page/feed titles, `Guo Lu` for author metadata, and `&copy; 2020&ndash;2026 Guo Lu` for HTML footers.
- Replace `/publication/index.html` with a lightweight redirect to `/guoluhomepage/#publications` so old collection links remain useful.
- Remove `/publication/index.xml`, because it contains only the copied publication archive.
- Remove the legacy publication-derived tag HTML/XML pages and their `page/1` redirect stubs. These tags do not describe the current homepage publication list.
- Remove obsolete publication and post lists from `404.html`, leaving a simple 404 page with navigation back to the homepage.
- Remove obsolete root and generated XML entries that advertise the copied publication/tag content; retained feeds must identify Guo Lu.

## Boundaries

- Do not modify the current publication entries in the homepage `index.html`.
- Do not rename text inside external URLs or PDF filenames merely because they contain `zongqing`.
- Do not delete the separate `/project/` AI@edge Lab content in this change; only update its site-owner chrome and metadata. Its content can be reviewed separately.
- Preserve the existing Cloudflare beacon, active News navigation, redirect behavior unrelated to removed legacy content, and current News archive/feed.

## Verification

- Add regression tests before production edits and confirm they fail for the existing copied archive.
- Assert the homepage publication section remains byte-for-byte unchanged across the cleanup.
- Assert `/publication/index.html` redirects to `/#publications` and the copied publication feed/tag artifacts are absent.
- Assert retained HTML/XML files contain no legacy site-owner identity strings.
- Assert the 404 page contains no copied publication titles or old publication links.
- Run the full test suite, HTML/XML audits, `git diff --check`, and a local HTTP smoke test for `/`, `/publication/`, `/news/`, and `/404.html`.
