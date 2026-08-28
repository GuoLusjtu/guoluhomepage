# Curated Publications Page Implementation Plan

> **For agentic workers:** REQUIRED: Use $subagent-driven-development (if subagents available) or $executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the publications redirect with a verified, responsive, year-organized publication archive and point the homepage's More Publications link to it.

**Architecture:** Keep the site fully static. First create and obtain user approval for a committed publication inventory assembled from Google Scholar and authoritative paper sources; then render the approved records directly into `publication/index.html`. Add focused structural tests in a new test module and page-specific CSS in the existing stylesheet without changing unrelated homepage content.

**Tech Stack:** Static HTML5, existing Bootstrap 3 and Hugo Academic CSS, Python `unittest`, standard-library HTML/regex/URL parsing, GitHub Pages.

**Design reference:** `docs/superpowers/specs/2026-08-28-publications-page-design.md`

---

## File Structure

- Create `docs/publications-inventory.md`: review-stage audit table for all discovered records, their authoritative sources, inclusion decisions, and unresolved exceptions.
- Create `tests/test_publications_inventory.py`: parse and validate the review inventory, its coverage, enum values, provenance, author policy, summary, and duplicate decisions.
- Create `tests/test_publications_page.py`: compare the rendered archive with the approved inventory and test page structure, metadata, URLs, ordering, responsive CSS, and homepage integration.
- Modify `publication/index.html`: replace the redirect document with the final static publication archive.
- Modify `index.html`: change only the More Publications destination.
- Modify `css/hugo-academic.css`: add narrowly scoped `.publications-page` layout and mobile rules.
- Modify `sitemap.xml`: add the now-indexable `/publication/` route.
- Modify `tests/test_homepage_content.py`: update preservation constants and route expectations affected by the approved homepage link and new sitemap route.

## Chunk 1: Verified Publication Inventory and Test Contract

### Task 1: Define an executable inventory contract

**Files:**
- Create: `docs/publications-inventory.md`
- Create: `tests/test_publications_inventory.py`
- Reference: `docs/superpowers/specs/2026-08-28-publications-page-design.md`

- [ ] **Step 1: Create an empty inventory with an exact schema**

Create `docs/publications-inventory.md` with this exact preamble and header:

```markdown
# Publications Inventory

Retrieved from Google Scholar: YYYY-MM-DD  
Scholar profile: https://scholar.google.com.au/citations?user=R9iwlJcAAAAJ&hl=zh-CN
Scholar records: 0  
Summary: include=0; exclude=0; needs-review=0

| Scholar title | Canonical title | Display authors | Original author count | Venue | Year | Destination | Authority | Year authority | Provenance | Type | Status | Reason |
| --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- | --- | --- |
```

Allowed values:

```text
Provenance: official-page | publisher | official-pdf | arxiv | user-confirmed
Type: journal | conference-main | excluded
Status: include | exclude | needs-review
```

Use `—` for a nullable destination or authority. `Year authority` is either one HTTPS URL or the literal `user-confirmed`. For `user-confirmed`, put the confirmation context in Reason.
Encode any literal pipe inside a field as `&#124;`; raw or backslash-escaped pipes are not allowed because the standard-library parser deliberately treats every raw pipe as a column delimiter.

- [ ] **Step 2: Write the inventory parser and failing validation tests**

Create `tests/test_publications_inventory.py`:

```python
from pathlib import Path
import re
import unicodedata
import unittest
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "publications-inventory.md"
FIELDS = (
    "Scholar title", "Canonical title", "Display authors",
    "Original author count", "Venue", "Year", "Destination",
    "Authority", "Year authority", "Provenance", "Type", "Status", "Reason",
)
PROVENANCE = {"official-page", "publisher", "official-pdf", "arxiv", "user-confirmed"}
RECORD_TYPES = {"journal", "conference-main", "excluded"}
STATUSES = {"include", "exclude", "needs-review"}
USER_CONFIRMED_RECORDS = {
    "Diff-VF: Training-free High-quality Long Video Generation via Diffusion Model": {
        "Display authors": "Haoning Yang, Xinyuan Chen, Yaohui Wang, Guo Lu",
        "Venue": "ACM TOMM",
        "Year": "2026",
    },
    "Large language model for lossless image compression with visual prompts": {
        "Display authors": "Junhao Du, Chuqin Zhou, Yunuo Chen, Guo Lu",
        "Venue": "IEEE T-CSVT",
        "Year": "2026",
    },
}


def normalized_title(value):
    value = unicodedata.normalize("NFKC", value).lower()
    value = re.sub(r"supplementary materials?", "", value)
    return re.sub(r"[^a-z0-9]+", "", value)


def load_inventory():
    text = INVENTORY.read_text(encoding="utf-8")
    lines = text.splitlines()
    header = "| " + " | ".join(FIELDS) + " |"
    start = lines.index(header) + 2
    rows = []
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        values = [value.strip() for value in line.strip("|").split("|")]
        if len(values) != len(FIELDS):
            raise AssertionError(f"Bad inventory row with {len(values)} fields: {line}")
        rows.append(dict(zip(FIELDS, values)))
    return text, rows


class PublicationsInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text, cls.rows = load_inventory()

    def test_declared_scholar_count_and_summary_match_rows(self):
        declared = int(re.search(r"^Scholar records: (\d+)  $", self.text, re.M).group(1))
        discovered = sum(row["Scholar title"] != "—" for row in self.rows)
        self.assertEqual(declared, discovered)
        counts = {status: sum(row["Status"] == status for row in self.rows) for status in STATUSES}
        expected = "Summary: " + "; ".join(f"{key}={counts[key]}" for key in ("include", "exclude", "needs-review"))
        self.assertIn(expected, self.text)

    def test_rows_use_valid_schema_and_provenance(self):
        self.assertTrue(self.rows)
        for row in self.rows:
            self.assertIn(row["Provenance"], PROVENANCE)
            self.assertIn(row["Type"], RECORD_TYPES)
            self.assertIn(row["Status"], STATUSES)
            self.assertRegex(row["Year"], r"^(?:19|20)\d{2}$")
            self.assertGreater(int(row["Original author count"]), 0)
            if row["Status"] == "include":
                for field in ("Canonical title", "Display authors", "Venue", "Year authority"):
                    self.assertNotEqual("—", row[field])
                self.assertEqual(1, row["Display authors"].count("Guo Lu"))
                if int(row["Original author count"]) > 10:
                    self.assertIn("…", row["Display authors"])
            if row["Status"] != "include":
                self.assertNotEqual("—", row["Reason"])
            if row["Provenance"] == "user-confirmed":
                self.assertNotEqual("—", row["Reason"])
            else:
                self.assertNotEqual("—", row["Authority"])
            for field in ("Destination", "Authority"):
                if row[field] != "—":
                    parsed = urlparse(row[field])
                    self.assertEqual("https", parsed.scheme)
                    self.assertTrue(parsed.netloc)
            if row["Year authority"] != "user-confirmed":
                parsed = urlparse(row["Year authority"])
                self.assertEqual("https", parsed.scheme)
                self.assertTrue(parsed.netloc)

    def test_included_titles_are_unique_after_normalization(self):
        keys = [normalized_title(row["Canonical title"]) for row in self.rows if row["Status"] == "include"]
        self.assertEqual(len(keys), len(set(keys)))

    def test_user_supplied_accepted_papers_are_not_omitted(self):
        for title, expected in USER_CONFIRMED_RECORDS.items():
            matches = [
                row for row in self.rows
                if normalized_title(row["Canonical title"]) == normalized_title(title)
                and row["Status"] == "include"
            ]
            self.assertEqual(1, len(matches))
            row = matches[0]
            for field, value in expected.items():
                self.assertEqual(value, row[field])
```

- [ ] **Step 3: Run the inventory tests to verify the empty artifact fails**

```powershell
python -m unittest tests.test_publications_inventory -v
```

Expected: FAIL at `test_rows_use_valid_schema_and_provenance` because the table has no rows.

### Task 2: Populate, verify, and obtain approval for the inventory

**Files:**
- Modify: `docs/publications-inventory.md`
- Test: `tests/test_publications_inventory.py`

- [ ] **Step 1: Capture the complete Scholar inventory with an exact command**

Run this read-only PowerShell command. It fetches both result pages and prints one tab-separated discovery row per Scholar record:

```powershell
$headers = @{ 'User-Agent' = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/127.0.0.0 Safari/537.36' }
$all = @()
foreach ($start in 0, 100) {
  $url = "https://scholar.google.com.au/citations?user=R9iwlJcAAAAJ&hl=en&pagesize=100&sortby=pubdate&cstart=$start"
  $content = (Invoke-WebRequest -Uri $url -Headers $headers).Content
  foreach ($match in [regex]::Matches($content, '<tr class="gsc_a_tr">(?<row>.*?)</tr>', 'Singleline')) {
    $row = $match.Groups['row'].Value
    $title = [regex]::Match($row, 'class="gsc_a_at"[^>]*>(?<v>.*?)</a>', 'Singleline').Groups['v'].Value
    $title = [System.Net.WebUtility]::HtmlDecode(([regex]::Replace($title, '<.*?>', '')))
    $year = [regex]::Match($row, 'class="gsc_a_h gsc_a_hc gs_ibl">(?<v>.*?)</span>', 'Singleline').Groups['v'].Value
    $all += [pscustomobject]@{ ScholarTitle = $title; ScholarYear = $year }
  }
}
$all | ForEach-Object { "$($_.ScholarYear)`t$($_.ScholarTitle)" }
"TOTAL=$($all.Count)"
```

Expected at plan-writing time: `TOTAL=108`. If Scholar returns a consent/CAPTCHA page or zero rows, retry later with the same command; if blocking persists, use a user-supplied Scholar export and record `Scholar retrieval fallback: user export` in the inventory preamble. Do not claim completeness from a partial page.

- [ ] **Step 2: Add one audit row per discovery**

Transfer every printed Scholar title into the `Scholar title` column using `apply_patch`. User-supplied accepted papers absent from Scholar use `—` in that column. The required user-supplied set initially contains Diff-VF and Large Language Model for Lossless Image Compression with Visual Prompts, using the four-author versions confirmed by Guo Lu. Update `Scholar records` to the exact fetched/exported count. The number of non-`—` Scholar-title rows must equal that count.

- [ ] **Step 3: Normalize duplicates without guessing**

Build a comparison key by Unicode-normalizing and lowercasing the title, removing punctuation, collapsing whitespace, and removing suffixes such as `supplementary material`. Every Scholar discovery remains a separate audit row. When a preprint and formal publication match, mark the formal row `include` and the preprint row `exclude` with `duplicate of: <canonical title>` in Reason; never collapse two discoveries into one row. Keep ambiguous matches as separate `needs-review` rows.

- [ ] **Step 4: Verify each retained record and its year authority**

For each candidate, verify title, author order, venue, year, and URL using this order:

1. CVF Open Access or OpenReview paper page;
2. IEEE Xplore, ACM DL, Springer, AAAI Proceedings, DOI, or other publisher page;
3. official paper PDF;
4. arXiv only for a confirmed accepted paper without a formal page;
5. explicit information supplied by Guo Lu.

Record one decisive metadata source in Authority and the specific source establishing the display year in Year authority. Additional supporting sources go in Reason. A user-confirmed accepted record may use `—` for Authority and `user-confirmed` for Year authority, with the supplied title/venue/year context in Reason. For a main-track conference paper, the authority must be an official proceedings entry/program or official PDF that distinguishes it from workshop/companion material. Do not expand initials unless a source resolves the full name. Normalize a verified owner variant to `Guo Lu`; do not infer that every `G. Lu` is the owner.

- [ ] **Step 5: Apply the inclusion rules**

Set `include` for peer-reviewed journal articles and regular/full papers in conference main tracks, including PCS, VCIP, ICME, ISCAS, ICASSP, and EUSIPCO. Set `exclude` with a reason for workshops, companion/demo/challenge/tutorial/poster-abstract/short-paper tracks, duplicate arXiv records, standalone unaccepted preprints, patents, supplementary material, and malformed duplicates.

- [ ] **Step 6: Verify long author lists**

For more than ten authors, construct the display sequence from the first four authors, Guo Lu in the original position, and the last two authors, inserting `…` for each omitted span. Verify that the displayed order is a subsequence of the official order and that `Guo Lu` occurs once.

- [ ] **Step 7: Recompute the summary and run the audit tests**

Count rows by Status and update the exact `Summary:` line. Then run:

```powershell
python -m unittest tests.test_publications_inventory -v
```

Expected: all inventory tests PASS, proving the declared Scholar count matches discovery rows, summary counts match statuses, required sources and years exist, enums are valid, included owner names follow policy, long lists contain an ellipsis, and normalized included titles are unique.

- [ ] **Step 8: Present the exception list to the user**

Use the already validated `Summary:` counts, then show every row whose Status is `needs-review`, grouped by Year. Stop here and obtain explicit approval of the inventory before writing publication-page markup. Apply corrections with `apply_patch`, update the summary, and rerun the inventory tests. Expected result: the user explicitly approves the inventory and all inventory tests pass.

- [ ] **Step 9: Commit the approved inventory**

```powershell
git add docs/publications-inventory.md tests/test_publications_inventory.py
git commit -m "docs: curate verified publication inventory"
```

Expected: one commit containing the approved inventory and its dedicated validator test.

### Task 3: Add failing publication-page contract tests

**Files:**
- Create: `tests/test_publications_page.py`
- Modify: `tests/test_homepage_content.py`

- [ ] **Step 1: Create the test module and shared constants**

Create `tests/test_publications_page.py` with:

```python
from pathlib import Path
import html
import re
import unittest
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "publication" / "index.html"
HOME = ROOT / "index.html"
CSS = ROOT / "css" / "hugo-academic.css"
PUBLICATIONS_URL = "https://guolusjtu.github.io/guoluhomepage/publication/"
SCHOLAR_URL = "https://scholar.google.com/citations?user=R9iwlJcAAAAJ&hl=en"
SCHOLAR_HREF = "https://scholar.google.com/citations?user=R9iwlJcAAAAJ&amp;hl=en"
EXPECTED_TITLE = "Publications | Guo Lu (鲁国) | SJTU"


class PublicationsPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.home = HOME.read_text(encoding="utf-8")
        cls.css = CSS.read_text(encoding="utf-8")
```

- [ ] **Step 2: Add metadata and redirect-removal tests**

```python
def test_page_has_exact_metadata_and_no_redirect(self):
    self.assertIn(f"<title>{EXPECTED_TITLE}</title>", self.page)
    self.assertIn(f'<link rel="canonical" href="{PUBLICATIONS_URL}">', self.page)
    self.assertNotRegex(self.page, r'<meta\s+http-equiv=["\']refresh["\']')
    self.assertIn('class="publications-page"', self.page)
    self.assertEqual(1, self.page.count(f'href="{SCHOLAR_HREF}"'))
```

- [ ] **Step 3: Add homepage-link and active-navigation tests**

```python
def test_homepage_more_publications_targets_archive(self):
    section = self.home.split('<section id="publications"', 1)[1].split("</section>", 1)[0]
    self.assertEqual(1, section.count(f'href="{PUBLICATIONS_URL}"'))
    self.assertIn("More Publications", section)

def test_publications_navigation_is_active(self):
    active = re.findall(
        rf'<li class="nav-item active">\s*<a href="{re.escape(PUBLICATIONS_URL)}">Publications</a>\s*</li>',
        self.page,
    )
    self.assertEqual(1, len(active))
```

- [ ] **Step 4: Add structural publication tests**

Require markup in this form:

```html
<section class="publication-year" data-year="2026">
  <div class="publication-year-label">2026</div>
  <div class="publication-year-items">
    <article class="publication-entry" data-title="..."></article>
  </div>
</section>
```

Add tests:

```python
def publication_entries(self):
    return re.findall(
        r'<article\s+class="publication-entry"(?=[\s>])(.*?)</article>',
        self.page,
        flags=re.DOTALL,
    )

def test_years_are_unique_and_reverse_chronological(self):
    years = [
        int(value)
        for value in re.findall(
            r'<section class="publication-year" data-year="(\d{4})">', self.page
        )
    ]
    self.assertTrue(years)
    self.assertEqual(sorted(set(years), reverse=True), years)

def test_entries_have_two_semantic_blocks(self):
    entries = self.publication_entries()
    self.assertTrue(entries)
    for entry in entries:
        self.assertEqual(1, entry.count('class="publication-title"'))
        self.assertEqual(1, entry.count('class="publication-meta"'))
        owners = re.findall(r'<span class="publication-owner">(.*?)</span>', entry, re.DOTALL)
        self.assertEqual(["Guo Lu"], [html.unescape(re.sub(r"<[^>]+>", "", value)).strip() for value in owners])
        meta = re.search(r'<div class="publication-meta">(.*?)</div>', entry, re.DOTALL).group(1)
        self.assertRegex(meta, r'<em>[^<]+, (?:19|20)\d{2}</em>')

def test_entry_years_match_their_enclosing_year_group(self):
    groups = re.findall(
        r'<section class="publication-year" data-year="(\d{4})">(.*?)</section>',
        self.page,
        flags=re.DOTALL,
    )
    for year, body in groups:
        labels = re.findall(r'<div class="publication-year-label">(.*?)</div>', body, re.DOTALL)
        self.assertEqual([year], [html.unescape(re.sub(r"<[^>]+>", "", value)).strip() for value in labels])
        self.assertEqual(1, body.count('class="publication-year-items"'))
        metas = re.findall(r'<div class="publication-meta">(.*?)</div>', body, re.DOTALL)
        self.assertTrue(metas)
        for meta in metas:
            self.assertRegex(meta, rf'<em>[^<]+, {year}</em>')
```

- [ ] **Step 5: Add URL and duplicate-title tests**

```python
def test_optional_title_links_use_https(self):
    for href in re.findall(r'<h2 class="publication-title">\s*<a href="([^"]+)"', self.page):
        parsed = urlparse(html.unescape(href))
        self.assertEqual("https", parsed.scheme)
        self.assertTrue(parsed.netloc)

def test_display_titles_are_unique_after_normalization(self):
    titles = re.findall(r'<article class="publication-entry" data-title="([^"]+)"', self.page)
    keys = [re.sub(r"[^a-z0-9]+", "", html.unescape(title).lower()) for title in titles]
    self.assertEqual(len(keys), len(set(keys)))

def test_rendered_titles_exactly_match_approved_inventory(self):
    from tests.test_publications_inventory import load_inventory, normalized_title
    _, rows = load_inventory()
    approved = {
        normalized_title(row["Canonical title"]): {
            "title": row["Canonical title"],
            "authors": row["Display authors"],
            "venue": row["Venue"],
            "year": row["Year"],
            "destination": "" if row["Destination"] == "—" else row["Destination"],
        }
        for row in rows if row["Status"] == "include"
    }
    rendered = {}
    pattern = (
        r'<article class="publication-entry" data-title="([^"]+)" '
        r'data-authors="([^"]+)" data-venue="([^"]+)" '
        r'data-year="(\d{4})" data-destination="([^"]*)">'
    )
    for title, authors, venue, year, destination in re.findall(pattern, self.page):
        decoded_title = html.unescape(title)
        rendered[normalized_title(decoded_title)] = {
            "title": decoded_title,
            "authors": html.unescape(authors),
            "venue": html.unescape(venue),
            "year": year,
            "destination": html.unescape(destination),
        }
    self.assertEqual(approved, rendered)

def test_visible_entry_content_matches_data_attributes(self):
    pattern = (
        r'<article class="publication-entry" data-title="([^"]+)" '
        r'data-authors="([^"]+)" data-venue="([^"]+)" '
        r'data-year="(\d{4})" data-destination="([^"]*)">(.*?)</article>'
    )
    for title, authors, venue, year, destination, body in re.findall(pattern, self.page, re.DOTALL):
        title_text = html.unescape(title)
        visible_title = re.search(r'<h2 class="publication-title">(.*?)</h2>', body, re.DOTALL).group(1)
        visible_title = html.unescape(re.sub(r"<[^>]+>", "", visible_title)).strip()
        self.assertEqual(title_text, visible_title)
        links = re.findall(r'<h2 class="publication-title">\s*<a href="([^"]+)">', body)
        self.assertEqual([] if not destination else [html.unescape(destination)], [html.unescape(value) for value in links])
        meta = re.search(r'<div class="publication-meta">(.*?)</div>', body, re.DOTALL).group(1)
        visible_meta = " ".join(html.unescape(re.sub(r"<[^>]+>", "", meta)).split())
        self.assertEqual(f"{html.unescape(authors)} · {html.unescape(venue)}, {year}", visible_meta)
```

- [ ] **Step 6: Add responsive CSS and analytics tests**

```python
def test_responsive_year_layout_contract(self):
    self.assertIn(".publications-page .publication-year", self.css)
    self.assertRegex(self.css, r'@media\s*\(max-width:\s*767px\)')
    self.assertIn(".publication-year-label", self.css)

def test_cloudflare_analytics_is_retained(self):
    self.assertIn("static.cloudflareinsights.com/beacon.min.js", self.page)
    self.assertIn('7f0b11c30fc344bfb55c572509aea6d0', self.page)
```

- [ ] **Step 7: Update affected legacy expectations**

In `tests/test_homepage_content.py`, add `PUBLICATION_ARCHIVE_URL = SITE_BASE_URL + "publication/"`; add `publication/index.html` to `STANDARD_SHELL_PATHS`; update the sitemap expectation to `(SITE_BASE_URL, SITE_BASE_URL + "news/", SITE_BASE_URL + "project/", PUBLICATION_ARCHIVE_URL)`. Add a test requiring exactly one More Publications href to `PUBLICATION_ARCHIVE_URL`. Do not update the homepage preservation hash until the exact intended homepage diff is available.

- [ ] **Step 8: Run the focused tests to verify failure**

```powershell
python -m unittest tests.test_publications_inventory tests.test_publications_page tests.test_homepage_content -v
```

Expected intentional failures: metadata/title/canonical, redirect-removal, page class, Scholar introduction link, active navigation, year/entry presence, responsive CSS, exact inventory-to-page record equality, homepage More Publications destination, standard-shell navigation, and sitemap route. Inventory tests and existing unrelated tests must remain green.

- [ ] **Step 9: Commit the failing tests**

```powershell
git add tests/test_publications_page.py tests/test_homepage_content.py
git commit -m "test: define curated publications archive"
```

## Chunk 2: Static Archive, Integration, and Verification

### Task 4: Implement the publication-page shell and responsive layout

**Files:**
- Modify: `publication/index.html`
- Modify: `css/hugo-academic.css`

- [ ] **Step 1: Replace the redirect with the standard site shell**

Use the existing page shell from `news/index.html` as the structural reference. Preserve its charset, viewport, stylesheet/script loading order, navigation destinations, footer, and Cloudflare beacon. Set:

```html
<title>Publications | Guo Lu (鲁国) | SJTU</title>
<link rel="canonical" href="https://guolusjtu.github.io/guoluhomepage/publication/">
```

Remove the `http-equiv="refresh"` element. Make Publications the only navigation item with `class="nav-item active"`; its link target is the canonical publication URL.

- [ ] **Step 2: Add the publication-page introduction**

Wrap all archive content in the site's standard content-width container:

```html
<main class="publications-page">
  <div class="container">
    <header class="publications-header">
      <h1>Publications</h1>
      <p>A curated list of peer-reviewed journal and conference publications. Please visit <a href="https://scholar.google.com/citations?user=R9iwlJcAAAAJ&amp;hl=en">Google Scholar</a> for citation statistics.</p>
    </header>
    <!-- All publication-year sections go here. -->
  </div>
</main>
```

- [ ] **Step 3: Add the desktop year-grid CSS**

Append one clearly marked block to `css/hugo-academic.css`:

```css
/* Curated publications archive */
.publications-page { padding: 96px 0 48px; }
.publications-header { margin-bottom: 32px; }
.publications-page .publication-year {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  column-gap: 24px;
  margin-bottom: 28px;
}
.publications-page .publication-year-label {
  color: #607d8b;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.4;
}
.publications-page .publication-entry { margin-bottom: 18px; }
.publications-page .publication-title {
  font-size: 17px;
  font-weight: 600;
  line-height: 1.45;
  margin: 0 0 3px;
}
.publications-page .publication-meta {
  color: #555;
  font-size: 14px;
  line-height: 1.55;
}
.publications-page .publication-owner {
  text-decoration: underline;
  text-underline-offset: 2px;
}
```

- [ ] **Step 4: Add the mobile layout CSS**

```css
@media (max-width: 767px) {
  .publications-page { padding-top: 72px; }
  .publications-page .publication-year {
    display: block;
    margin-bottom: 26px;
  }
  .publications-page .publication-year-label { margin-bottom: 10px; }
  .publications-page .publication-title { font-size: 16px; }
}
```

Do not add cards, tables, badges, fixed heights, or horizontal scrolling.

- [ ] **Step 5: Run the focused tests**

```powershell
python -m unittest tests.test_publications_page -v
```

Expected: metadata, redirect, navigation, CSS, and analytics tests PASS. Entry/year and exact inventory-rendering tests still FAIL until Task 5; the homepage More Publications integration test still FAILS until Task 6.

- [ ] **Step 6: Commit the shell and styles**

```powershell
git add publication/index.html css/hugo-academic.css
git commit -m "feat: add publications archive shell"
```

### Task 5: Render the approved publication inventory

**Files:**
- Modify: `publication/index.html`
- Reference: `docs/publications-inventory.md`

- [ ] **Step 1: Add year containers in reverse order**

For every year with at least one approved `include` record, create exactly one `publication-year` section. Do not render `exclude` or `needs-review` records.

- [ ] **Step 2: Render each approved paper**

Use this exact semantic shape and exact data-attribute order:

```html
<article class="publication-entry" data-title="DVC: An End-to-End Deep Video Compression Framework" data-authors="Guo Lu, Wanli Ouyang, Dong Xu, Xiaoyun Zhang, Chunlei Cai, Zhiyong Gao" data-venue="CVPR" data-year="2019" data-destination="https://verified.example/paper">
  <h2 class="publication-title"><a href="https://verified.example/paper">DVC: An End-to-End Deep Video Compression Framework</a></h2>
  <div class="publication-meta"><span class="publication-owner">Guo Lu</span>, Wanli Ouyang, Dong Xu, Xiaoyun Zhang, Chunlei Cai, Zhiyong Gao &middot; <em>CVPR, 2019</em></div>
</article>
```

Populate all five attributes from the approved inventory. `data-authors` contains the plain approved display sequence without markup. `data-destination` is an empty string when Destination is `—`; in that case omit only the `<a>` wrapper. In the visible meta block, replace the one verified `Guo Lu` token in the approved author sequence with `<span class="publication-owner">Guo Lu</span>` at exactly the same position, including when it occurs after an ellipsis. Do not move or duplicate it. HTML-escape ampersands, quotes, apostrophes, and non-ASCII punctuation as required. Preserve the approved author order and ellipses.

- [ ] **Step 3: Cross-check rendered counts**

Compare total rendered articles and per-year counts against the approved inventory's `include` rows. Expected: exact equality, zero duplicate normalized titles, and no `needs-review` title present.

- [ ] **Step 4: Run focused tests**

Run the archive-only tests explicitly, excluding the homepage integration test that belongs to Task 6:

```powershell
python -m unittest `
  tests.test_publications_page.PublicationsPageTests.test_page_has_exact_metadata_and_no_redirect `
  tests.test_publications_page.PublicationsPageTests.test_publications_navigation_is_active `
  tests.test_publications_page.PublicationsPageTests.test_years_are_unique_and_reverse_chronological `
  tests.test_publications_page.PublicationsPageTests.test_entries_have_two_semantic_blocks `
  tests.test_publications_page.PublicationsPageTests.test_entry_years_match_their_enclosing_year_group `
  tests.test_publications_page.PublicationsPageTests.test_optional_title_links_use_https `
  tests.test_publications_page.PublicationsPageTests.test_display_titles_are_unique_after_normalization `
  tests.test_publications_page.PublicationsPageTests.test_rendered_titles_exactly_match_approved_inventory `
  tests.test_publications_page.PublicationsPageTests.test_visible_entry_content_matches_data_attributes `
  tests.test_publications_page.PublicationsPageTests.test_responsive_year_layout_contract `
  tests.test_publications_page.PublicationsPageTests.test_cloudflare_analytics_is_retained -v
```

Expected: all 11 archive-only tests PASS. The homepage integration test remains intentionally red until Task 6.

- [ ] **Step 5: Commit the archive content**

```powershell
git add publication/index.html
git commit -m "content: publish curated publication archive"
```

### Task 6: Integrate the homepage link and sitemap

**Files:**
- Modify: `index.html`
- Modify: `sitemap.xml`
- Modify: `tests/test_homepage_content.py`

- [ ] **Step 1: Change only the More Publications href**

Within `#publications`, replace:

```html
href="https://scholar.google.com/citations?user=R9iwlJcAAAAJ&amp;hl=en"
```

with:

```html
href="https://guolusjtu.github.io/guoluhomepage/publication/"
```

Leave the Scholar social icon and all publication entries unchanged.

- [ ] **Step 2: Add the publication route to the sitemap**

Add one `<url>` entry for `https://guolusjtu.github.io/guoluhomepage/publication/` in the same format as the existing retained routes.

- [ ] **Step 3: Update narrow legacy test expectations**

Retain the existing `PUBLICATIONS_URL`, which represents the homepage `#publications` anchor. Update only `PUBLICATION_ARCHIVE_URL` expectations, sitemap locations, standard-shell membership, and the homepage preservation hash after inspecting the intended one-link diff. Recompute the preservation hash using the existing test normalization logic; do not weaken or remove the preservation assertion.

- [ ] **Step 4: Run both test modules**

```powershell
python -m unittest tests.test_publications_inventory tests.test_publications_page tests.test_homepage_content -v
```

Expected: all tests PASS.

- [ ] **Step 5: Verify the homepage diff is narrow**

```powershell
git diff -- index.html
```

Expected: only the More Publications URL changes.

- [ ] **Step 6: Commit integration changes**

```powershell
git add index.html sitemap.xml tests/test_homepage_content.py
git commit -m "feat: link homepage to publication archive"
```

### Task 7: Perform final semantic and visual verification

**Files:**
- Verify: `publication/index.html`
- Verify: `index.html`
- Verify: `css/hugo-academic.css`
- Verify: `sitemap.xml`

- [ ] **Step 1: Run the complete test suite**

```powershell
python -m unittest discover -s tests -v
```

Expected: every test passes with zero failures and errors.

- [ ] **Step 2: Run static hygiene checks**

```powershell
git diff --check
rg -n "http-equiv=.refresh|Zongqing|supplementary material|arXiv preprint" publication/index.html
```

Expected: `git diff --check` has no errors; `rg` finds none of the excluded/legacy markers.

- [ ] **Step 3: Serve the site locally**

Start the server in a hidden managed process and keep the returned process object for cleanup:

```powershell
$publicationServer = Start-Process python -ArgumentList "-m","http.server","54321" -WorkingDirectory (Get-Location) -WindowStyle Hidden -PassThru
```

Open `http://localhost:54321/publication/` and `http://localhost:54321/`.

- [ ] **Step 4: Verify the 1280-pixel desktop layout**

Confirm the year is in a narrow left column, paper content is in the right column, long entries wrap within the content width, Publications is active, title links work, and there is no horizontal overflow.

- [ ] **Step 5: Verify the 375-pixel mobile layout**

Confirm each year becomes a compact label above its first paper, titles and author lists wrap naturally, navigation remains usable, and there is no horizontal overflow.

- [ ] **Step 6: Validate internal links and metadata**

Confirm the homepage More Publications link opens `/publication/`, the Scholar link remains available, the canonical URL and title are exact, and the Cloudflare beacon remains present once.

- [ ] **Step 7: Stop the local server**

```powershell
Stop-Process -Id $publicationServer.Id
```

Expected: the managed local server process exits and port 54321 is released.

If any visual-verification step aborts early, run this cleanup step before continuing so the server is not orphaned.

- [ ] **Step 8: Commit any verification-only corrections**

If verification required a correction, rerun the full suite, inspect the actual changed paths, and stage only those corrections. Run only the corresponding `git add -- ...` command or commands from this explicit scoped list:

```powershell
git status --short
git diff --name-only
git add -- publication/index.html
git add -- index.html
git add -- css/hugo-academic.css
git add -- sitemap.xml
git add -- tests/test_publications_page.py
git add -- tests/test_homepage_content.py
git commit -m "fix: polish publications archive"
```

Do not run a listed `git add` command for a path that was not corrected during verification. If no correction was required, create no empty commit.

- [ ] **Step 9: Request final code review before push**

Use `$requesting-code-review` for a spec-compliance and quality review. Resolve blocking findings, rerun the complete suite, and report the exact passing test count. Do not push until Guo Lu explicitly requests it.
