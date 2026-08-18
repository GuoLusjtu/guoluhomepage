# Homepage Publications, Services, and News Implementation Plan

> **For agentic workers:** REQUIRED: Use $subagent-driven-development (if subagents available) or $executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the confirmed 2026 publications and service roles, restore a six-item homepage News section, rebuild the News archive/feed from 2026 onward, reactivate News navigation, and deploy the verified static site.

**Architecture:** Continue editing the generated static HTML directly. `index.html` owns the homepage publications, services, and six-item News summary; `news/index.html` owns the full from-2026 archive; `news/index.xml` mirrors the archive items; the 19 body-bearing HTML pages share the active News navigation item. Regression tests define exact content/order while retaining the existing analytics and redirect-stub invariants.

**Tech Stack:** Static HTML, RSS 2.0 XML, Python standard-library `unittest`, PowerShell, Git/GitHub Pages.

**Design spec:** `docs/superpowers/specs/2026-08-18-homepage-publications-services-news-design.md`

**Required Python:** `C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` (Python 3.12.13 at planning time). Invoke it with `-B` for tests and the temporary server so no `__pycache__` is created.

---

## File map

- Modify `tests/test_homepage_content.py`: replace obsolete News-preservation/commented-navigation assertions and add exact regression coverage for publications, services, homepage News, archive, feed, and active navigation.
- Modify `index.html`: add two publications, update Services, add the six-item News section, and activate its News navigation item.
- Modify `news/index.html`: activate navigation and replace the pre-2026 list/pager with the six-item 2026 archive.
- Modify `news/index.xml`: replace the old feed items and legacy identity metadata with the six 2026 announcements without individual detail URLs.
- Modify the other 17 body-bearing HTML pages listed in Task 4: only uncomment the existing News navigation `<li>`.
- Do not modify the 12 body-less redirect stubs.

### Task 0: Record the baseline and create the implementation worktree

**Files:**
- Verify: repository state only

- [ ] **Step 1: Commit this reviewed plan on `master` before implementation**

The design commits already exist on `master`. After this plan passes document review, commit only this file:

```powershell
git add docs/superpowers/plans/2026-08-18-homepage-publications-services-news.md
git commit -m "docs: plan 2026 homepage and news refresh"
```

- [ ] **Step 2: Fetch and record a stable comparison base**

Run:

```powershell
git fetch origin
if ($LASTEXITCODE -ne 0) { throw 'git fetch origin failed' }
git merge-base --is-ancestor origin/master HEAD
if ($LASTEXITCODE -ne 0) { throw 'origin/master is not an ancestor of HEAD' }
$homepageBaseSha = (git rev-parse origin/master).Trim()
if ($LASTEXITCODE -ne 0 -or $homepageBaseSha -notmatch '^[0-9a-f]{40}$') { throw 'Could not resolve BASE_SHA' }
$homepageStartSha = (git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $homepageStartSha -notmatch '^[0-9a-f]{40}$') { throw 'Could not resolve START_SHA' }
Write-Output "BASE_SHA=$homepageBaseSha"
Write-Output "START_SHA=$homepageStartSha"
git status --short --branch
$dirty = @(git status --porcelain)
if ($LASTEXITCODE -ne 0 -or $dirty.Count -ne 0) { throw 'Main worktree is not clean' }
```

Expected: ancestor check exits 0; record both 40-character SHAs in the execution log; the main worktree is clean. `BASE_SHA` intentionally covers the already-approved design/plan commits in the final deployment range.

- [ ] **Step 3: Create an isolated worktree from the recorded start commit**

Use `$using-git-worktrees`. Create `.worktrees/homepage-2026-refresh` on branch `codex/homepage-2026-refresh` explicitly from `$homepageStartSha`. Confirm `.worktrees/` is ignored, both worktrees are clean, and the feature worktree starts at the recorded SHA. Reassign `$homepageBaseSha` to the recorded literal SHA in any later PowerShell session before range commands.

## Chunk 1: Regression contract

### Task 1: Add failing content and News regression tests

**Files:**
- Modify: `tests/test_homepage_content.py`
- Test: `tests/test_homepage_content.py`

- [ ] **Step 1: Add shared News/feed constants and extraction helpers**

Add `html` and `xml.etree.ElementTree`, then define the exact six strings and RSS mapping once:

```python
import html
import xml.etree.ElementTree as ET

NEWS_FEED = ROOT / "news" / "index.xml"
NEWS_ITEMS = (
    "August 2026 — Invited to serve as an Area Chair for ICLR 2027 and as a Senior PC member for AAAI 2027.",
    "August 2026 — Two papers were accepted by ACM TOMM and IEEE T-CSVT.",
    "July 2026 — Two papers were accepted by ACM MM 2026, and one paper was accepted by ECCV 2026.",
    "June 2026 — Organizing the Challenge on Ultra-Low Bitrate Image Compression at ECCV 2026.",
    "March 2026 — Serving as a Guest Editor for an IEEE JETCAS Special Issue.",
    "February 2026 — Two papers were accepted by CVPR 2026.",
)
LEGACY_NEWS_MARKERS = (
    "One paper accepted at ICLR&#39;20",
    "One paper accepted at TON",
    "One paper accepted at AAAI&#39;20",
    "/news/iclr20/",
    "/news/mm17/",
    "/news/infocom16-talk/",
    "/news/page/2/",
)
NEWS_FEED_ITEMS = (
    ("2026-08-service", "ICLR 2027 and AAAI 2027 service roles", NEWS_ITEMS[0]),
    ("2026-08-publications", "Two journal papers accepted", NEWS_ITEMS[1]),
    ("2026-07-publications", "ACM MM 2026 and ECCV 2026 papers accepted", NEWS_ITEMS[2]),
    ("2026-06-challenge", "ECCV 2026 compression challenge", NEWS_ITEMS[3]),
    ("2026-03-jetcas", "IEEE JETCAS Special Issue Guest Editor", NEWS_ITEMS[4]),
    ("2026-02-cvpr", "Two CVPR 2026 papers accepted", NEWS_ITEMS[5]),
)

def section(html, section_id):
    start = html.index(f'<section id="{section_id}"')
    end = html.index("</section>", start) + len("</section>")
    return html[start:end]
```

- [ ] **Step 2: Add exact publication tests**

Create tests that extract each new `pub-list-item` and assert:

```python
def test_new_2026_journal_publications_have_exact_content(self):
    expected = (
        (
            "Diff-VF: Training-free High-quality Long Video Generation via Diffusion Model",
            "[TOMM'26] Diff-VF: Training-free High-quality Long Video Generation via Diffusion Model",
            "https://scholar.google.com.au/citations?view_op=view_citation&hl=zh-CN&user=R9iwlJcAAAAJ&sortby=pubdate&citation_for_view=R9iwlJcAAAAJ:4fKUyHm3Qg0C",
            "Haoning Yang, Xinyuan Chen, Yaohui Wang, <u>Guo Lu</u>",
            "ACM Transactions on Multimedia Computing, Communications, and Applications (TOMM), 2026.",
        ),
        (
            "Large Language Model for Lossless Image Compression with Visual Prompts",
            "[T-CSVT'26] Large Language Model for Lossless Image Compression with Visual Prompts",
            "https://scholar.google.com.au/citations?view_op=view_citation&hl=zh-CN&user=R9iwlJcAAAAJ&cstart=20&pagesize=80&sortby=pubdate&citation_for_view=R9iwlJcAAAAJ:ZHo1McVdvXMC",
            "Junhao Du, Chuqin Zhou, Yunuo Chen, <u>Guo Lu</u>",
            "IEEE Transactions on Circuits and Systems for Video Technology, 2026.",
        ),
    )
    for lookup_title, expected_title, url, authors, venue in expected:
        with self.subTest(title=expected_title):
            entry = publication_entry(self.homepage, lookup_title)
            decoded_entry = html.unescape(entry)
            self.assertIn(expected_title, decoded_entry)
            self.assertIn(f'href="{url}"', decoded_entry)
            self.assertIn(authors, decoded_entry)
            self.assertIn(f"<em>{venue}</em>", decoded_entry)
            self.assertEqual(1, entry.count("<u>Guo Lu</u>"))
```

Add a second test that takes the Publications section, finds the positions of the eight confirmed 2026 labels/titles, and asserts their index list is sorted. It must specifically assert TOMM is third and T-CSVT is fourth, and that no second ACMMM entry was added.

- [ ] **Step 3: Add exact Professional Services tests**

Extract and `html.unescape(section(self.homepage, "services"))`. Assert each confirmed rendered sentence occurs exactly once, the Associate Editor line precedes all new/updated roles, stale ICLR/NeurIPS/AAAI variants are absent, `submission deadline` and `June 1, 2026` are absent, and unaffected legacy service lines remain present. Production HTML must escape URL query separators as `&amp;`; rendered-text assertions accept raw Unicode punctuation or equivalent valid entities.

- [ ] **Step 4: Replace the obsolete commented-navigation test**

Replace `test_all_news_navigation_items_are_commented_and_none_are_active` with an assertion that all 19 body-bearing pages contain exactly one active canonical News `<li>`, no complete commented News `<li>` remains, and all 12 redirect stubs contain neither form.

Use comment stripping before counting active markup:

```python
page_without_comments = re.sub(r"<!--.*?-->", "", page, flags=re.DOTALL)
self.assertEqual(1, len(active_item.findall(page_without_comments)))
self.assertEqual(0, len(commented_item.findall(page)))
```

- [ ] **Step 5: Replace the obsolete legacy-archive hash test**

Remove `test_news_archive_body_and_known_titles_are_preserved`. Add separate tests that assert:

1. `index.html` has exactly one `id="news"` section between `id="bio"` and `id="publications"`. Apply `html.unescape()` to the extracted section before asserting it contains the six `NEWS_ITEMS` once each in exact order. Assert one `More News` link whose decoded href is `https://guolusjtu.github.io/guoluhomepage/news/` or `/guoluhomepage/news/`.
2. `news/index.html` has exactly six structural blocks with ids matching the six `NEWS_FEED_ITEMS` fragments. Apply `html.unescape()` to each block and the whole archive before comparing rendered text. Each block renders one complete `NEWS_ITEMS` sentence exactly once (do not render a separate duplicate date), in exact order, and none of `LEGACY_NEWS_MARKERS` occurs anywhere in the page.
3. Parsing `news/index.xml` yields the exact channel metadata and exact six-item mapping below. Assert `Zongqing`, every legacy marker, and any `news/<old-slug>/` link is absent.
4. No new directory or HTML file exists under `news/`; its repository files remain exactly `news/index.html` and `news/index.xml`.

The RSS contract is exact:

```text
channel/title: News | Guo Lu's Homepage
channel/link: https://guolusjtu.github.io/guoluhomepage/news/
channel/description: News from Guo Lu's Homepage
channel/language: en-us
channel/copyright: © 2020–2026 Guo Lu
channel/lastBuildDate: Tue, 18 Aug 2026 00:00:00 +0800
```

For each `NEWS_FEED_ITEMS` tuple `(fragment, title, description)`, require one `<item>` with exactly that `title` and `description`; both `<link>` and `<guid>` equal `https://guolusjtu.github.io/guoluhomepage/news/#{fragment}`; `guid` has `isPermaLink="true"`; and item-level `pubDate` is omitted rather than inventing a specific acceptance day.

Keep the existing 31/19/12 HTML classification, Cloudflare beacon, legacy-GA absence, public-counter absence, footer, Awards, contact, Oral-label, and `#projects` preservation tests unchanged.

- [ ] **Step 6: Run the full suite to verify the new contract is red**

Run:

```powershell
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m unittest discover -s tests -v
```

Expected: nonzero exit; the new publication, Services, homepage/archive/feed News, and active-navigation tests fail for missing/stale production content, while all unrelated preservation and analytics tests pass.

- [ ] **Step 7: Inspect and commit only the red tests**

Run:

```powershell
git diff --check
git diff -- tests/test_homepage_content.py
git status --short
```

Expected: only `tests/test_homepage_content.py` is modified and no production HTML/XML is changed.

Commit:

```powershell
git add tests/test_homepage_content.py
git commit -m "test: define 2026 homepage and news refresh"
```

## Chunk 2: Homepage content

### Task 2: Add publications, Services, and homepage News

**Files:**
- Modify: `index.html`
- Test: `tests/test_homepage_content.py`

- [ ] **Step 1: Add the compact News section between About and Publications**

Immediately after the closing `</section>` for `id="bio"` and before `id="publications"`, add a `home-section` with `id="news"`. Follow the existing two-column structure: left heading `News`, right compact `<ul>` with six `<li><p>...</p></li>` entries in `NEWS_ITEMS` order, followed by a `More News` link to `https://guolusjtu.github.io/guoluhomepage/news/`. Use HTML-safe punctuation consistently, but ensure rendered text matches the six approved sentences exactly.

- [ ] **Step 2: Insert TOMM'26 and T-CSVT'26 as publication positions 3 and 4**

Place two existing-style `pub-list-item` blocks immediately after ACMMM'26 and before Engineering'26. Wrap each complete title/label in the approved Scholar `<a>` URL; encode every query-string `&` as `&amp;` in HTML; use the exact four-author string with only `<u>Guo Lu</u>`; use the exact full venue sentence in `<em>`.

- [ ] **Step 3: Update Professional Services without reordering unrelated entries**

Keep Associate Editor first. Insert JETCAS Guest Editor and ECCV Challenge Organizer directly after it, then preserve the remaining current order while replacing the ICLR, NeurIPS, and AAAI lines with:

```html
<p>Area Chair, International Conference on Learning Representations (ICLR), 2025, 2026, 2027.</p>
<p>Area Chair, Annual Conference on Neural Information Processing Systems (NeurIPS), 2025, 2026.</p>
<p>Senior PC, AAAI, 2021, 2026, 2027.</p>
```

Use the two exact new service sentences from the design spec. Do not include the JETCAS deadline or a month.

- [ ] **Step 4: Run focused homepage tests**

Run:

```powershell
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m unittest tests.test_homepage_content.HomepageContentTests.test_new_2026_journal_publications_have_exact_content -v
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m unittest tests.test_homepage_content.HomepageContentTests.test_2026_publications_have_confirmed_order -v
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m unittest tests.test_homepage_content.HomepageContentTests.test_professional_services_have_confirmed_2026_roles -v
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m unittest tests.test_homepage_content.HomepageContentTests.test_homepage_news_has_latest_six_and_archive_link -v
```

Expected: PASS for all four. The full suite may still fail only for active navigation and the not-yet-rebuilt archive/feed.

- [ ] **Step 5: Check and commit homepage content**

Run `git diff --check`, inspect `git diff -- index.html`, and confirm the Cloudflare snippet still occurs once immediately before `</body>`.

Commit:

```powershell
git add index.html
git commit -m "feat: refresh 2026 homepage content"
```

## Chunk 3: News navigation, archive, and feed

### Task 3: Rebuild the News archive and RSS feed from 2026

**Files:**
- Modify: `news/index.html`
- Modify: `news/index.xml`
- Test: `tests/test_homepage_content.py`

- [ ] **Step 1: Replace the legacy HTML archive list**

Preserve the News page header, navbar, page title/container, footer, scripts, and exact Cloudflare beacon. Replace only the current 10 legacy item blocks and pager with six compact item blocks in the approved order. Each block has the corresponding stable `NEWS_FEED_ITEMS` fragment as its `id` and displays the one complete approved `NEWS_ITEMS` sentence as plain archive content—do not add a separate date line because the sentence already begins with month/year. Do not add an `<a>` to an individual detail page.

- [ ] **Step 2: Rebuild the XML item list**

Use the exact channel metadata and `NEWS_FEED_ITEMS` mapping defined in Task 1. Replace all 15 old `<item>` elements. Links/guids use the six stable archive fragments, and item-level `pubDate` is omitted. Preserve the existing RSS 2.0/Atom namespace and exact self link.

- [ ] **Step 3: Run archive/feed tests**

Run:

```powershell
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m unittest tests.test_homepage_content.HomepageContentTests.test_news_archive_has_exact_2026_items -v
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m unittest tests.test_homepage_content.HomepageContentTests.test_news_feed_has_exact_2026_items -v
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m unittest tests.test_homepage_content.HomepageContentTests.test_news_directory_has_no_detail_pages -v
```

Expected: PASS; exactly six items in both representations, no pre-2026 title/URL, no dead pager, and no extra file under `news/`.

- [ ] **Step 4: Verify analytics and commit archive/feed**

Run:

```powershell
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m unittest tests.test_homepage_content.HomepageContentTests.test_content_pages_have_one_cloudflare_beacon_before_body_end -v
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m unittest tests.test_homepage_content.HomepageContentTests.test_all_html_files_exclude_legacy_google_analytics -v
git diff --check
```

Expected: PASS and no whitespace errors.

Commit:

```powershell
git add news/index.html news/index.xml
git commit -m "feat: restart news archive from 2026"
```

### Task 4: Reactivate News navigation on all body-bearing pages

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
- Test: `tests/test_homepage_content.py`

- [ ] **Step 1: Uncomment only the complete News navigation item**

In each listed HTML file, change:

```html
<!-- <li class="nav-item"><a href="https://guolusjtu.github.io/guoluhomepage/#news">News</a></li> -->
```

to:

```html
<li class="nav-item"><a href="https://guolusjtu.github.io/guoluhomepage/#news">News</a></li>
```

Do not touch `#projects` links, redirect stubs, or other navigation items.

- [ ] **Step 2: Run active-navigation and redirect tests**

Run:

```powershell
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m unittest tests.test_homepage_content.HomepageContentTests.test_all_body_pages_have_active_news_navigation -v
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m unittest tests.test_homepage_content.HomepageContentTests.test_redirect_stubs_are_unmodified_and_have_no_cloudflare_beacon -v
```

Expected: PASS; 19 active News items, zero commented items, and unchanged redirect hash.

- [ ] **Step 3: Inspect the mechanical diff and commit**

Run `git diff --check` and `git diff --stat`. Confirm every navigation-only file other than `index.html` and `news/index.html` has exactly one insertion and one deletion.

Commit:

```powershell
git add 404.html index.html news/index.html project/index.html publication/index.html tags/community/index.html tags/data-offload/index.html tags/deep-learning/index.html tags/edge-computing/index.html tags/human-contact-networks/index.html tags/infectious-diseases/index.html tags/information-diffusion/index.html tags/multiagent-learning/index.html tags/opportunistic-networking/index.html tags/reinforcement-learning/index.html tags/respiratory-symptoms/index.html tags/smartphones/index.html tags/social-networks/index.html tags/video/index.html
git commit -m "feat: restore news navigation"
```

## Chunk 4: Verification, integration, and deployment

### Task 5: Run complete automated and local HTTP verification

**Files:**
- Verify only; no planned content edits.

- [ ] **Step 1: Run the full fresh regression suite**

Run:

```powershell
& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m unittest discover -s tests -v
```

Expected: all tests pass, including exact content/order, 19 active navigation items, six HTML/XML News items, analytics invariants, 31/19/12 classification, redirect hash, and unrelated preservation checks.

- [ ] **Step 2: Check repository hygiene and complete diff**

Run:

```powershell
$homepageBaseSha = 'e39e0ee017e32a845ee6cbf56647d856895acc66'
git diff --check "$homepageBaseSha..HEAD"
git status --short
git diff --stat "$homepageBaseSha..HEAD"
git diff "$homepageBaseSha..HEAD" -- index.html news/index.html news/index.xml tests/test_homepage_content.py
```

Expected: clean working tree, no cache artifacts, and only the planned test/HTML/XML files plus design/plan documentation in the complete range.

- [ ] **Step 3: Smoke-test with a temporary local server**

Run this concrete PowerShell smoke script. It refuses to reuse an occupied port, retains the exact child PID, retries readiness for at most five seconds, and always stops/waits for that child:

```powershell
$pythonExe = 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$port = 8000
if (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) {
    throw "Port $port is already listening"
}
$server = $null
try {
    $server = Start-Process -FilePath $pythonExe -ArgumentList @('-B', '-m', 'http.server', "$port", '--bind', '127.0.0.1') -WorkingDirectory (Get-Location).Path -WindowStyle Hidden -PassThru
    $homeResponse = $null
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        try {
            $homeResponse = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/' -TimeoutSec 2
            break
        } catch {
            Start-Sleep -Milliseconds 250
        }
    }
    if ($null -eq $homeResponse -or $homeResponse.StatusCode -ne 200) { throw 'Local server did not become ready' }
    $newsResponse = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/news/' -TimeoutSec 5
    $tagResponse = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/tags/video/' -TimeoutSec 5
    foreach ($response in @($homeResponse, $newsResponse, $tagResponse)) {
        if ($response.StatusCode -ne 200) { throw "Unexpected HTTP $($response.StatusCode)" }
        if ($response.Content -notmatch '<li class="nav-item"><a href="https://guolusjtu\.github\.io/guoluhomepage/#news">News</a></li>') { throw 'Active News navigation missing' }
        if (([regex]::Matches($response.Content, [regex]::Escape('7f0b11c30fc344bfb55c572509aea6d0'))).Count -ne 1) { throw 'Cloudflare token count mismatch' }
        if ($response.Content -match 'UA-88925956-1') { throw 'Legacy GA marker found' }
    }
    if ($homeResponse.Content -notmatch '<section id="news" class="home-section">' -or $homeResponse.Content -notmatch 'Two papers were accepted by ACM TOMM and IEEE T-CSVT') { throw 'Homepage News content missing' }
    if ($newsResponse.Content -notmatch 'id="2026-08-service"' -or $newsResponse.Content -match 'One paper accepted at ICLR&#39;20|/news/page/2/') { throw 'News archive content mismatch' }
    if ($tagResponse.Content -notmatch '<title>Video') { throw 'Representative tag marker missing' }
} finally {
    if ($null -ne $server -and -not $server.HasExited) {
        Stop-Process -Id $server.Id
        Wait-Process -Id $server.Id -ErrorAction SilentlyContinue
    }
}
if (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) { throw "Port $port still listening" }
try {
    Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/' -TimeoutSec 2 | Out-Null
    throw 'Request unexpectedly succeeded after shutdown'
} catch {
    if ($_.Exception.Message -eq 'Request unexpectedly succeeded after shutdown') { throw }
}
Write-Output 'Smoke test passed'
```

The script requests:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/news/`
- `http://127.0.0.1:8000/tags/video/`

Assert HTTP 200, exact representative markers, one Cloudflare beacon per HTML response, active News navigation on all three, six homepage/archive News items, no old News marker, and no old GA marker. After cleanup, verify the PID and listener are gone and a new request is refused.

- [ ] **Step 4: Obtain two-stage implementation review**

Dispatch a spec-compliance reviewer, then a code-quality reviewer, over the recorded `$homepageBaseSha..HEAD` range. Resolve any verified blocking issue, rerun the affected tests and full suite, and repeat review until both approve.

### Task 6: Fast-forward, push, and verify production

**Files:**
- Git integration/deployment only.

- [ ] **Step 1: Integrate the reviewed implementation**

If implementation ran in a feature worktree, verify both worktrees are clean and fast-forward `master` to `codex/homepage-2026-refresh` with `git merge --ff-only`. Do not rewrite or discard the already-approved design and plan commits.

- [ ] **Step 2: Re-run tests on final `master` and push**

Run the full unittest suite and range `git diff --check` once more. Immediately before pushing, fetch again and refuse to push if the remote gained commits:

```powershell
$pythonExe = 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonExe -B -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Final tests failed' }
$homepageBaseSha = 'e39e0ee017e32a845ee6cbf56647d856895acc66'
git diff --check "$homepageBaseSha..HEAD"
if ($LASTEXITCODE -ne 0) { throw 'Final diff check failed' }
git fetch origin
git merge-base --is-ancestor origin/master master
if ($LASTEXITCODE -ne 0) { throw 'Remote history is not an ancestor of local master' }
$counts = (git rev-list --left-right --count master...origin/master).Trim() -split '\s+'
$localAhead = [int]$counts[0]
$remoteAhead = [int]$counts[1]
if ($remoteAhead -ne 0) { throw "origin/master gained $remoteAhead commit(s); stop and integrate safely" }
if ($localAhead -eq 0) { throw 'No local commits to push' }
git push origin master
if ($LASTEXITCODE -ne 0) { throw 'Push failed' }
git status --short --branch
```

Expected: push succeeds and `master...origin/master` reports no ahead/behind commits.

- [ ] **Step 3: Verify the deployed GitHub Pages site**

After GitHub Pages propagation, request all three production URLs corresponding to the local smoke test and assert HTTP 200 plus the same representative content/navigation/analytics markers. Open the homepage in a JS-capable browser, confirm the News section and More News flow render correctly, and check that Cloudflare can receive the visit after normal processing delay.

- [ ] **Step 4: Report the deployed result**

Report the pushed commit, tests/smoke results, production URL checks, and the Cloudflare dashboard path. Mention that News retention now begins in 2026 and the old XML/archive entries were intentionally removed.
