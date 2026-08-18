# Cloudflare Web Analytics Implementation Plan

> **For agentic workers:** REQUIRED: Use $subagent-driven-development (if subagents available) or $executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the obsolete Google Analytics integration with the user's private Cloudflare Web Analytics beacon on every full content page while preserving redirect stubs and all visible site content.

**Architecture:** Extend the existing source-level HTML regression suite first, then apply one exact mechanical migration to the 19 body-bearing pages. Treat the 12 Hugo redirect stubs as immutable inputs, and use local plus production smoke tests to separate HTML integration correctness from Cloudflare's live data processing.

**Tech Stack:** Static HTML, Python 3 standard library (`unittest`, `pathlib`, `hashlib`, `re`), Git, Python HTTP server, Cloudflare Web Analytics.

---

## Chunk 1: Analytics migration and deployment

### Task 0: Create the isolated implementation worktree

**Files:**
- Use: `.gitignore`
- Create worktree: `.worktrees/cloudflare-web-analytics`
- Create branch: `codex/cloudflare-web-analytics`

- [ ] **Step 1: Verify the main worktree and ignore rule**

Run from the repository root:

```powershell
git status --short --branch
git check-ignore -v --no-index .worktrees/test
$BASE_SHA = git rev-parse HEAD
Write-Output $BASE_SHA
```

Expected: `master` is clean, `.worktrees/` is ignored by the committed `.gitignore`, and `BASE_SHA` records the exact documentation-only starting commit. Record and verify the actual ahead count at execution time rather than relying on a hard-coded value.

- [ ] **Step 2: Create the feature branch and worktree**

Run:

```powershell
git worktree add ".worktrees/cloudflare-web-analytics" -b "codex/cloudflare-web-analytics" $BASE_SHA
```

Expected: the worktree is created from `BASE_SHA` at `C:\Users\user\Documents\ChatGPT\个人主页\.worktrees\cloudflare-web-analytics`.

- [ ] **Step 3: Verify the isolated baseline**

Run from the new worktree:

```powershell
git status --short --branch
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B tests\test_homepage_content.py -v
```

Expected: clean `codex/cloudflare-web-analytics` branch and the existing 13/13 tests pass.

### Task 1: Add analytics regression coverage and establish RED

**Files:**
- Modify: `tests/test_homepage_content.py`
- Test: all 31 repository-filesystem HTML files outside `.worktrees`

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
                body_end = page.rindex("</body>")
                self.assertTrue(
                    page[:body_end].rstrip().endswith(CLOUDFLARE_BEACON)
                )
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

Expected: 18 test methods run. The Cloudflare installation method produces 19 failing subtests because no content page has a beacon, and the legacy-GA-removal method produces 19 failing subtests because all 19 content pages retain GA. Unittest reports `FAILED (failures=38)` across those two methods. The other 16 methods pass, including the redirect-stub byte hash and all existing preservation tests.

- [ ] **Step 5: Commit the RED regression tests**

Run:

```powershell
git add -- tests/test_homepage_content.py
git commit -m "test: define analytics migration requirements"
```

Expected: one commit modifying only the test file, with the intended 38 failing subtests across two test methods documented.

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

### Task 3: Local smoke test and whole-branch verification

**Files:**
- Test: `index.html`
- Test: `news/index.html`
- Test: `tags/community/index.html`

- [ ] **Step 1: Run the deterministic local smoke script before committing**

Run this complete PowerShell script from the isolated worktree:

```powershell
$pythonExe = 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$beacon = '<!-- Cloudflare Web Analytics --><script type=''module'' src=''https://static.cloudflareinsights.com/beacon.min.js'' data-cf-beacon=''{"token": "7f0b11c30fc344bfb55c572509aea6d0"}''></script><!-- End Cloudflare Web Analytics -->'
$targets = @(
    @{ Url = 'http://127.0.0.1:8000/'; Marker = '<title>GUO LU&#39;s Homepage</title>' },
    @{ Url = 'http://127.0.0.1:8000/news/'; Marker = '<h1>News</h1>' },
    @{ Url = 'http://127.0.0.1:8000/tags/community/'; Marker = 'Community' }
)
$server = Start-Process -FilePath $pythonExe -ArgumentList '-m','http.server','--bind','127.0.0.1','8000' -WorkingDirectory (Get-Location).Path -WindowStyle Hidden -PassThru
try {
    $ready = $false
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        try {
            $null = Invoke-WebRequest -UseBasicParsing $targets[0].Url -TimeoutSec 2
            $ready = $true
            break
        } catch {
            Start-Sleep -Milliseconds 250
        }
    }
    if (-not $ready) { throw 'Local server did not become ready' }

    foreach ($target in $targets) {
        $response = Invoke-WebRequest -UseBasicParsing $target.Url -TimeoutSec 5
        if ([int]$response.StatusCode -ne 200) { throw "Unexpected status for $($target.Url)" }
        if (-not $response.Content.Contains($target.Marker)) { throw "Missing marker for $($target.Url)" }
        if (([regex]::Matches($response.Content, [regex]::Escape($beacon))).Count -ne 1) { throw "Beacon count mismatch for $($target.Url)" }
        foreach ($forbidden in @('UA-88925956-1','GoogleAnalyticsObject','www.google-analytics.com/analytics.js')) {
            if ($response.Content.Contains($forbidden)) { throw "Legacy GA remains in $($target.Url)" }
        }
    }
} finally {
    if (-not $server.HasExited) {
        Stop-Process -Id $server.Id -Force
        $server.WaitForExit()
    }
}
if (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Port 8000 is still listening'
}
try {
    $null = Invoke-WebRequest -UseBasicParsing $targets[0].Url -TimeoutSec 2
    throw 'Server still responds after cleanup'
} catch [System.Net.WebException] {
    Write-Output 'Server cleanup verified'
}
```

Expected: all three URLs return HTTP 200, markers and exactly one beacon are present, legacy GA is absent, the exact server PID exits, port 8000 closes, and a follow-up request is refused.

- [ ] **Step 2: Run fresh final verification**

Run:

```powershell
$BASE_SHA = git merge-base HEAD master
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B tests\test_homepage_content.py -v
git diff --check $BASE_SHA..HEAD
git diff --check
git diff --stat
git status --short --branch
```

Expected before the migration commit: 18/18 tests pass; both diff checks report no whitespace errors; and status/diff stat show only the 19 planned content-page edits. Use the recorded `BASE_SHA` for all whole-range comparisons; do not use `HEAD~2`.

- [ ] **Step 3: Commit the migration**

Run:

```powershell
git add -- 404.html index.html news/index.html project/index.html publication/index.html tags
git commit -m "feat: add private Cloudflare web analytics"
```

Expected: one commit changing only the 19 content pages.

- [ ] **Step 4: Verify the complete two-commit range and clean state**

Run the 18-test suite again with `-B`, then run:

```powershell
$BASE_SHA = git merge-base HEAD master
git diff --check $BASE_SHA..HEAD
git diff --stat $BASE_SHA..HEAD
git status --short --branch
```

Expected: clean feature worktree. The range contains only `tests/test_homepage_content.py` plus the 19 content pages; all 12 redirect stubs are identical to `BASE_SHA`.

### Task 4: Integrate, deploy, and verify production

**Files:**
- Integrate: the reviewed feature branch into `master`
- Verify: `https://guolusjtu.github.io/guoluhomepage/`

- [ ] **Step 1: Merge the reviewed branch into `master`**

Use a fast-forward merge after fresh tests pass on the feature branch.

- [ ] **Step 2: Re-run tests on merged `master`**

Run the bundled Python suite with `-B` from the main working tree. The `.worktrees` exclusion regression must keep the count at 18 tests even while the isolated worktree exists.

Expected: 18/18 tests pass. Before push, dynamically verify that `master` is ahead of `origin/master` by the existing documentation commits plus the two reviewed implementation commits.

- [ ] **Step 3: Push `master` and verify the remote SHA**

Run `git push origin master`, then compare `git ls-remote origin refs/heads/master` with local `git rev-parse HEAD`.

Expected: identical commit IDs.

- [ ] **Step 4: Verify all three live URLs and execute the beacon**

Request all three live URLs with cache-busting queries: the homepage, `/news/`, and `/tags/community/`. For every URL, confirm HTTP 200, exactly one expected Cloudflare beacon/token, and no legacy GA markers. Then open the deployed homepage in a JavaScript-capable browser and refresh once so the beacon actually executes; a PowerShell source request alone does not create an analytics event.

- [ ] **Step 5: Confirm the first event in Cloudflare**

Open Cloudflare Dashboard → Analytics & Logs → Web Analytics → `guolusjtu.github.io`, allow the normal processing delay, and confirm a visit/page view appears. This is a user-visible external dashboard confirmation; do not claim collection success based only on local HTML or the public page source.

- [ ] **Step 6: Clean up the integrated worktree and branch**

After remote and live-source verification, confirm the feature worktree is clean, remove the exact worktree path, and delete the fully merged local feature branch.
