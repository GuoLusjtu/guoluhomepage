# Homepage Content Cleanup Implementation Plan

> **For agentic workers:** REQUIRED: Use $subagent-driven-development (if subagents available) or $executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct the confirmed homepage content, contact, publication, navigation, anchor, and footer defects while preserving the legacy News archive and unrelated generated pages.

**Architecture:** Treat the repository as deployed static output. Add a standard-library Python regression test that inspects rendered HTML source, then make narrowly scoped HTML edits: homepage-specific corrections in `index.html` and one mechanical News-navigation comment across the 19 files that currently expose it.

**Tech Stack:** Static HTML, Python 3 standard library (`unittest`, `pathlib`, `re`), Git, Python HTTP server.

---

## Chunk 1: Regression coverage and homepage corrections

### Task 1: Add source-level regression tests and establish RED

**Files:**
- Create: `tests/test_homepage_content.py`
- Test: `index.html`
- Test: `news/index.html`
- Test: all repository `*.html` files containing the News navigation item

- [ ] **Step 1: Create the regression test**

Create `tests/test_homepage_content.py` with the following complete implementation:

```python
import hashlib
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
HTML_FILES = sorted(ROOT.rglob("*.html"))
NEWS_ARCHIVE_BYTES = (ROOT / "news" / "index.html").read_bytes()
NEWS_ARCHIVE = NEWS_ARCHIVE_BYTES.decode("utf-8")

NEWS_ITEM = re.compile(
    r'<li class="nav-item">\s*<a href="https://guolusjtu\.github\.io/'
    r'guoluhomepage/#news">News</a>\s*</li>',
    re.DOTALL,
)
COMMENTED_NEWS_ITEM = re.compile(
    r'<!--\s*<li class="nav-item">\s*<a href="https://guolusjtu\.github\.io/'
    r'guoluhomepage/#news">News</a>\s*</li>\s*-->',
    re.DOTALL,
)


def publication_block(marker: str) -> str:
    start = INDEX.index(marker)
    end = INDEX.find('<div class="pub-list-item"', start + len(marker))
    return INDEX[start:] if end == -1 else INDEX[start:end]


def without_comments(source: str) -> str:
    return re.sub(r"<!--.*?-->", "", source, flags=re.DOTALL)


class HomepageContentTests(unittest.TestCase):
    def test_metadata_description_is_current(self):
        self.assertIn(
            'meta name="description" content="Associate Professor at Shanghai Jiao '
            'Tong University | Video Coding, Multimedia Processing, and Efficient '
            'Multimodal LLMs"',
            INDEX,
        )
        self.assertNotIn('content="PhD-SJTU"', INDEX)

    def test_graduate_course_heading_is_spelled_and_anchored_correctly(self):
        self.assertIn('<h3 id="graduate-courses">Graduate Course</h3>', INDEX)
        self.assertNotIn("Gradudate", INDEX)

    def test_aaai_2025_entry_has_official_venue(self):
        block = publication_block("Controllable Distortion-Perception Tradeoff")
        self.assertIn(
            "Proceedings of the AAAI Conference on Artificial Intelligence, "
            "39(10), 10725–10733, 2025.",
            block,
        )
        self.assertNotIn("IEEE Transactions on Image Processing,2022", block)

    def test_cvpr_2025_iqa_entry_is_highlight_not_oral(self):
        block = publication_block("Image Quality Assessment: From Human to Machine Preference")
        self.assertIn("(Highlight)", block)
        self.assertNotIn("(Oral)", block)

    def test_other_valid_oral_labels_are_preserved(self):
        iccv = publication_block("Knowledge Distillation for Learned Image Compression")
        acmmm = publication_block("Rate-aware Compression for NeRF-based Volumetric Video")
        self.assertIn("(Oral)", iccv)
        self.assertIn("(Oral)", acmmm)

    def test_obfuscated_email_is_visible_without_invalid_mailto(self):
        self.assertRegex(
            INDEX,
            re.compile(
                r'<a href="#contact">\s*<i class="fa fa-envelope big-icon"',
                re.DOTALL,
            ),
        )
        contact = INDEX[INDEX.index('<section id="contact"'):]
        self.assertIn("luguo2014 AT sjtu.edu.cn", contact)
        self.assertNotIn("mailto:", INDEX)

    def test_awards_navigation_and_section_use_awards_anchor(self):
        self.assertIn('guoluhomepage/#awards">Awards</a>', INDEX)
        self.assertIn('<section id="awards" class="home-section">', INDEX)
        self.assertNotIn('guoluhomepage/#project">Awards</a>', INDEX)

    def test_homepage_footer_has_current_year_range(self):
        self.assertIn("&copy; 2020–2026 Guo Lu", INDEX)
        self.assertNotIn("&copy; 2020 Guo Lu", INDEX)

    def test_legacy_footer_attributions_are_preserved(self):
        count = sum(
            path.read_text(encoding="utf-8").count("&copy; 2018 Zongqing Lu")
            for path in HTML_FILES
        )
        self.assertEqual(18, count)

    def test_news_navigation_is_commented_in_all_19_existing_locations(self):
        active = []
        commented = []
        for path in HTML_FILES:
            source = path.read_text(encoding="utf-8")
            if NEWS_ITEM.search(without_comments(source)):
                active.append(path.relative_to(ROOT).as_posix())
            if COMMENTED_NEWS_ITEM.search(source):
                commented.append(path.relative_to(ROOT).as_posix())
        self.assertEqual([], active)
        self.assertEqual(19, len(commented))

    def test_news_archive_body_remains_available(self):
        archive_body = NEWS_ARCHIVE_BYTES.split(b"</nav>", 1)[1]
        digest = hashlib.sha256(archive_body).hexdigest()
        self.assertEqual(
            "de25264193ea6089fd830c83d0d26f815dc5485fa82467fe77c8f51e7c77efee",
            digest,
        )
        self.assertIn("<h1>News</h1>", NEWS_ARCHIVE)
        self.assertIn("One paper accepted at ICLR&#39;20", NEWS_ARCHIVE)
        self.assertIn("One paper accepted at TON", NEWS_ARCHIVE)
        self.assertIn("One paper accepted at AAAI&#39;20", NEWS_ARCHIVE)

    def test_unrelated_projects_anchors_are_preserved(self):
        count = sum(
            path.read_text(encoding="utf-8").count("#projects")
            for path in HTML_FILES
        )
        self.assertEqual(18, count)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify RED**

Run: `& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tests/test_homepage_content.py -v`

Expected: 12 tests run; the News archive, unrelated `#projects`, legacy footer, and valid `(Oral)` preservation tests pass, while the eight tests for the unfixed defects fail for their intended assertions.

### Task 2: Apply the homepage-only corrections and verify partial GREEN

**Files:**
- Modify: `index.html:87` metadata description
- Modify: `index.html:131` News navigation comment (completed with Task 3)
- Modify: `index.html:136` Awards navigation anchor
- Modify: `index.html:180` email icon link
- Modify: `index.html:391-400` AAAI'25 venue
- Modify: `index.html:430-440` CVPR'25 status
- Modify: `index.html:600` Awards section ID
- Modify: `index.html:642` Graduate Course heading and ID
- Modify: `index.html:715-730` Contact email text
- Modify: `index.html:743` footer year range

- [ ] **Step 1: Replace the metadata description**

Change `PhD-SJTU` to `Associate Professor at Shanghai Jiao Tong University | Video Coding, Multimedia Processing, and Efficient Multimodal LLMs`.

- [ ] **Step 2: Correct the course heading and anchor**

Replace `<h3 id="gradudate-courses">Gradudate Course</h3>` with `<h3 id="graduate-courses">Graduate Course</h3>`.

- [ ] **Step 3: Correct the AAAI'25 venue**

Within only the `Controllable Distortion-Perception Tradeoff` entry, replace the stale TIP venue with `Proceedings of the AAAI Conference on Artificial Intelligence, 39(10), 10725–10733, 2025.`

- [ ] **Step 4: Resolve the CVPR'25 status conflict**

Within only the `Image Quality Assessment` entry, preserve the title's red `(Highlight)` label and remove the red `(Oral)` span from the venue, leaving `IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2025.`

- [ ] **Step 5: Replace the invalid email interaction**

Change the profile email icon link from `mailto:sdluguo AT gmail.com` to `#contact`. Add a Contact list item containing an envelope icon and the plain text `luguo2014 AT sjtu.edu.cn`; do not create a `mailto:` link.

- [ ] **Step 6: Correct the Awards anchor**

On the homepage only, change the Awards navigation URL suffix from `#project` to `#awards` and change `<section id="project"` to `<section id="awards"`. Do not change `#projects` anywhere.

- [ ] **Step 7: Update the homepage footer**

Change `&copy; 2020 Guo Lu` to `&copy; 2020–2026 Guo Lu` only in `index.html`.

- [ ] **Step 8: Run the regression test and inspect the expected remaining failure**

Run: `& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tests/test_homepage_content.py -v`

Expected: all homepage correction tests pass; only `test_news_navigation_is_commented_in_all_19_existing_locations` remains failing because News is not yet commented everywhere.

## Chunk 2: News navigation, smoke tests, and implementation commit

### Task 3: Comment the existing News navigation items

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

- [ ] **Step 1: Wrap each complete News navigation item in an HTML comment**

Transform only this existing element in each listed file:

```html
<li class="nav-item"><a href="https://guolusjtu.github.io/guoluhomepage/#news">News</a></li>
```

to:

```html
<!-- <li class="nav-item"><a href="https://guolusjtu.github.io/guoluhomepage/#news">News</a></li> -->
```

Preserve all News archive body markup and all other navigation items.

- [ ] **Step 2: Run the full regression test for GREEN**

Run: `& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tests/test_homepage_content.py -v`

Expected: `Ran 12 tests` followed by `OK`.

- [ ] **Step 3: Include the untracked test in diff inspection**

Run: `git add -N -- tests/test_homepage_content.py`

Expected: the test remains unstaged but now appears in `git diff` output.

- [ ] **Step 4: Check patch integrity**

Run: `git diff --check`

Expected: exit code 0, with no whitespace errors.

Run: `git diff --stat`

Expected: one test file plus the homepage and exactly 18 additional HTML files modified; no News archive body, PDFs, slides, images, CSS, or JavaScript changed.

### Task 4: Serve and smoke-test the affected pages

**Files:**
- Test: `index.html`
- Test: `news/index.html`

- [ ] **Step 1: Start a temporary local server**

Run: `& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m http.server --bind 127.0.0.1 8000`

Expected: server listens on `127.0.0.1:8000`; keep the process running only for the smoke test.

- [ ] **Step 2: Request the homepage and News archive**

Run: `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/ | Select-Object StatusCode`

Expected: `StatusCode 200`.

Run: `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/news/ | Select-Object StatusCode`

Expected: `StatusCode 200`.

- [ ] **Step 3: Stop the temporary server**

Send Ctrl-C to the server process and verify it exits.

### Task 5: Final verification and local implementation commit

**Files:**
- Verify: all modified files

- [ ] **Step 1: Run fresh final verification**

Run: `& 'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tests/test_homepage_content.py -v`

Expected: `Ran 12 tests` and `OK`.

Run: `git diff --check`

Expected: exit code 0.

Run: `git status --short`

Expected: only the planned test and HTML files are modified/untracked.

- [ ] **Step 2: Review the exact diff**

Run: `git diff -- index.html` and `git diff -- '*.html'`.

Expected: only approved homepage corrections and News navigation comments; specifically no unrelated `(Oral)`, `#projects`, News archive body, or legacy footer attribution changes.

- [ ] **Step 3: Commit the implementation locally**

Run:

```powershell
git add -- tests/test_homepage_content.py index.html 404.html news/index.html project/index.html publication/index.html tags
git commit -m "fix: correct homepage content and navigation"
```

Expected: one local implementation commit. Do not push until the user reviews the result and explicitly approves publication.
