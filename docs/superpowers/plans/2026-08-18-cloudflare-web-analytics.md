# Cloudflare Web Analytics Implementation Plan

> **For agentic workers:** REQUIRED: Use $subagent-driven-development (if subagents available) or $executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the obsolete Google Analytics integration with the user's private Cloudflare Web Analytics beacon on every full content page while preserving redirect stubs and all visible site content.

**Architecture:** Extend the existing source-level HTML regression suite first, then apply one exact mechanical migration to the 19 body-bearing pages. Treat the 12 Hugo redirect stubs as immutable inputs, and use local plus production smoke tests to separate HTML integration correctness from Cloudflare's live data processing.

**Tech Stack:** Static HTML, Python 3 standard library (`unittest`, `pathlib`, `hashlib`, `re`), Git, Python HTTP server, Cloudflare Web Analytics.

---

## Chunk 1: Analytics migration and deployment

### Task 1: Add analytics regression coverage and establish RED

**Files:**
- Modify: `tests/test_homepage_content.py`
- Test: all 31 tracked HTML files, excluding `.worktrees`

- [ ] **Step 1: Add constants and helpers**

Add these constants below the existing path constants:

```python
CLOUDFLARE_BEACON = (
    "<!-- Cloudflare Web Analytics -->"
    "<script type='module' "
    "src='https://static.cloudflareinsights.com/beacon.min.js' "
    'data-cf-beacon=\'{"token": "7f0b11c30fc344bfb55c572509aea6d0"}\'>'
    "</script>"
    "<!-- End Cloudflare Web Analytics -->"
)
REDIRECT_STUBS_SHA256 = (
    "fb95fbe62cb3204583afd7b2cba254184babdff19b2e8add1208b973a894e162"
)
PUBLIC_COUNTER_MARKERS = (
    "visitor-counter",
    "visitor-count",
    "pageview-counter",
    "busuanzi",
)
```

Add this helper after `read_text`:

```python
def combined_raw_hash(paths):
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
```

- [ ] **Step 2: Partition the audited pages in `setUpClass`**

After building `cls.html_files`, add:

```python
        cls.content_pages = tuple(
            path for path in cls.html_files if "</body>" in read_text(path)
        )
        cls.redirect_stubs = tuple(
            path for path in cls.html_files if path not in cls.content_pages
        )
```

- [ ] **Step 3: Add five focused tests**

Add these methods to `HomepageContentTests`:

```python
    def test_html_pages_partition_into_content_and_redirect_stubs(self):
        self.assertEqual(31, len(self.html_files))
        self.assertEqual(19, len(self.content_pages))
        self.assertEqual(12, len(self.redirect_stubs))
        self.assertTrue(all("</body>" in read_text(path) for path in self.content_pages))
        self.assertTrue(all("</body>" not in read_text(path) for path in self.redirect_stubs))

    def test_cloudflare_beacon_is_installed_once_before_body_end(self):
        for path in self.content_pages:
            with self.subTest(path=path):
                page = read_text(path)
                self.assertEqual(1, page.count(CLOUDFLARE_BEACON))
                self.assertLess(page.index(CLOUDFLARE_BEACON), page.rindex("</body>"))
                self.assertEqual(
                    1,
                    page.count("7f0b11c30fc344bfb55c572509aea6d0"),
                )

    def test_redirect_stubs_remain_uninstrumented_and_byte_preserved(self):
        self.assertEqual(REDIRECT_STUBS_SHA256, combined_raw_hash(self.redirect_stubs))
        for path in self.redirect_stubs:
            with self.subTest(path=path):
                self.assertNotIn("static.cloudflareinsights.com", read_text(path))

    def test_legacy_google_analytics_is_removed(self):
        forbidden = (
            "www.google-analytics.com/analytics.js",
            "UA-88925956-1",
            "GoogleAnalyticsObject",
        )
        for path in self.html_files:
            with self.subTest(path=path):
                page = read_text(path)
                for marker in forbidden:
                    self.assertNotIn(marker, page)
                self.assertNotRegex(page, r"\bga\s*\(")

    def test_no_public_visitor_counter_is_added(self):
        for path in self.html_files:
            with self.subTest(path=path):
                page = read_text(path).lower()
                for marker in PUBLIC_COUNTER_MARKERS:
                    self.assertNotIn(marker, page)
```

- [ ] **Step 4: Run the suite and verify RED**

Run:

```powershell
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B tests\test_homepage_content.py -v
```

Expected: 18 tests run. The Cloudflare installation test fails because no beacon is installed, and the legacy-GA-removal test fails because all 19 content pages still contain the old integration. The other 16 tests pass, including the redirect-stub byte hash and all existing preservation tests.

- [ ] **Step 5: Commit the RED regression tests**

Run:

```powershell
git add -- tests/test_homepage_content.py
git commit -m "test: define analytics migration requirements"
```

Expected: one commit modifying only the test file, with the intended 2-failure RED state documented.

### Task 2: Replace legacy Google Analytics with Cloudflare

**Files:**
- Modify: `404.html`
- Modify: `index.html`
- Modify: `news/index.html`
- Modify: `project/index.html`
- Modify: `publication/index.html`
- Modify: `tags/community/index.html`
- Modify: `tags/data-offload/index.html`
- Modify: `tags/deep-learning/index.html`
- Modify: `tags/edge-computing/index.html`
- Modify: `tags/human-contact-networks/index.html`
- Modify: `tags/infectious-diseases/index.html`
- Modify: `tags/information-diffusion/index.html`
- Modify: `tags/multiagent-learning/index.html`
- Modify: `tags/opportunistic-networking/index.html`
- Modify: `tags/reinforcement-learning/index.html`
- Modify: `tags/respiratory-symptoms/index.html`
- Modify: `tags/smartphones/index.html`
- Modify: `tags/social-networks/index.html`
- Modify: `tags/video/index.html`
- Preserve byte-for-byte: the 12 `tags/*/page/1/index.html` redirect stubs

- [ ] **Step 1: Remove each complete legacy GA block**

In each of the 19 listed content pages, remove the entire `<script>...</script>` block that contains `GoogleAnalyticsObject`, including its `analytics.js` loader, `UA-88925956-1` pageview calls, and the outbound-link handler that calls `ga('send', 'event', ...)`.

Do not remove unrelated JavaScript imports or inline scripts such as Highlight.js initialization.

- [ ] **Step 2: Insert the exact Cloudflare snippet**

Insert this exact single line once, immediately before the final `</body>` in each of the 19 listed content pages:

```html
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "7f0b11c30fc344bfb55c572509aea6d0"}'></script><!-- End Cloudflare Web Analytics -->
```

Do not add visible text, counters, widgets, banners, cookies, or dashboard links.

- [ ] **Step 3: Run the complete suite for GREEN**

Run:

```powershell
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B tests\test_homepage_content.py -v
```

Expected: `Ran 18 tests` followed by `OK`.

- [ ] **Step 4: Verify exact file scope and preservation**

Run: `git diff --check`

Expected: exit code 0.

Run: `git diff --stat`

Expected: exactly the 19 listed content pages modified; no redirect stub, CSS, JavaScript asset, image, PDF, slide, XML, or visible-content file outside those HTML pages changed.

Run: `rg -n "UA-88925956-1|GoogleAnalyticsObject|www.google-analytics.com/analytics.js|\bga\s*\(" -g '*.html' .`

Expected: no matches outside ignored `.worktrees`; the regression suite provides the authoritative filtered check.

- [ ] **Step 5: Commit the migration**

Run:

```powershell
git add -- 404.html index.html news/index.html project/index.html publication/index.html tags
git commit -m "feat: add private Cloudflare web analytics"
```

Expected: one commit changing only the 19 content pages.

### Task 3: Local smoke test and whole-branch verification

**Files:**
- Test: `index.html`
- Test: `news/index.html`
- Test: `tags/community/index.html`

- [ ] **Step 1: Start the local server with a deterministic Windows process handle**

Use the exact bundled Python executable with `Start-Process -WindowStyle Hidden -PassThru` and arguments `-m http.server --bind 127.0.0.1 8000`. Retain the returned PID for cleanup.

- [ ] **Step 2: Smoke-test three representative pages**

Request:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/news/`
- `http://127.0.0.1:8000/tags/community/`

Expected: all return HTTP 200, retain their expected page markers, contain the exact Cloudflare beacon once, and contain no legacy Google Analytics markers.

- [ ] **Step 3: Stop the exact server PID and verify cleanup**

Stop only the PID returned in Step 1, wait for exit, and verify port 8000 is no longer listening and subsequent requests are refused.

- [ ] **Step 4: Run fresh final verification**

Run:

```powershell
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B tests\test_homepage_content.py -v
git diff --check HEAD~2..HEAD
git status --short --branch
```

Expected: 18/18 tests pass, diff check is clean, and the isolated worktree has no tracked or untracked changes.

Review the full two-commit implementation range. Confirm only the test file and 19 content pages changed; all 12 redirect stubs are identical to the base commit.

### Task 4: Integrate, deploy, and verify production

**Files:**
- Integrate: the reviewed feature branch into `master`
- Verify: `https://guolusjtu.github.io/guoluhomepage/`

- [ ] **Step 1: Merge the reviewed branch into `master`**

Use a fast-forward merge after fresh tests pass on the feature branch.

- [ ] **Step 2: Re-run tests on merged `master`**

Run the bundled Python suite with `-B` from the main working tree. The `.worktrees` exclusion regression must keep the count at 18 tests even while the isolated worktree exists.

Expected: 18/18 tests pass.

- [ ] **Step 3: Push `master` and verify the remote SHA**

Run `git push origin master`, then compare `git ls-remote origin refs/heads/master` with local `git rev-parse HEAD`.

Expected: identical commit IDs.

- [ ] **Step 4: Verify the live deployment**

Request the live homepage with a cache-busting query. Confirm HTTP 200, exactly one expected Cloudflare beacon/token, and no legacy GA markers. Repeat for `/news/` and one canonical tag page if deployment propagation is incomplete on the first request.

- [ ] **Step 5: Confirm the first event in Cloudflare**

Open Cloudflare Dashboard → Analytics & Logs → Web Analytics → `guolusjtu.github.io`, allow the normal processing delay, and confirm a visit/page view appears. This is a user-visible external dashboard confirmation; do not claim collection success based only on local HTML or the public page source.

- [ ] **Step 6: Clean up the integrated worktree and branch**

After remote and live-source verification, confirm the feature worktree is clean, remove the exact worktree path, and delete the fully merged local feature branch.
