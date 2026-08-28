from pathlib import Path
import html
import re
import unittest
from urllib.parse import urlparse

from tests.test_publications_inventory import load_inventory, normalized_title


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "publication" / "index.html"
HOME = ROOT / "index.html"
CSS = ROOT / "css" / "hugo-academic.css"
PUBLICATIONS_URL = "https://guolusjtu.github.io/guoluhomepage/publication/"
SCHOLAR_HREF = (
    "https://scholar.google.com/citations?user=R9iwlJcAAAAJ&amp;hl=en"
)
EXPECTED_TITLE = "Publications | Guo Lu (鲁国) | SJTU"
CLOUDFLARE_SCRIPT_URL = "https://static.cloudflareinsights.com/beacon.min.js"
CLOUDFLARE_TOKEN = "7f0b11c30fc344bfb55c572509aea6d0"


def visible_text(fragment):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def inline_visible_text(fragment):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", fragment)).split())


class PublicationsPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.home = HOME.read_text(encoding="utf-8")
        cls.css = CSS.read_text(encoding="utf-8")

    def publication_entries(self):
        return re.findall(
            r'<article\b(?=[^>]*\bclass="publication-entry"(?:\s|"))[^>]*>'
            r'(.*?)</article>',
            self.page,
            flags=re.DOTALL,
        )

    def test_page_has_exact_metadata_and_no_redirect(self):
        self.assertEqual(
            [EXPECTED_TITLE],
            re.findall(r"<title>(.*?)</title>", self.page, flags=re.DOTALL),
        )
        self.assertEqual(
            [PUBLICATIONS_URL],
            re.findall(
                r'<link\s+rel="canonical"\s+href="([^"]+)"\s*/?>', self.page
            ),
        )
        self.assertNotRegex(
            self.page, r'<meta\s+[^>]*http-equiv=["\']refresh["\']'
        )
        self.assertEqual(
            1,
            len(re.findall(r'<main\s+class="publications-page">', self.page)),
        )
        self.assertEqual(1, self.page.count(f'href="{SCHOLAR_HREF}"'))

    def test_homepage_more_publications_targets_archive(self):
        publications = self.home.split('<section id="publications"', 1)[1].split(
            "</section>", 1
        )[0]
        links = re.findall(
            r'<a\b[^>]*href="([^"]+)"[^>]*>\s*More Publications\s*</a>',
            publications,
            flags=re.DOTALL,
        )
        self.assertEqual([PUBLICATIONS_URL], [html.unescape(link) for link in links])

    def test_publications_navigation_is_exactly_active(self):
        active_items = re.findall(
            r'<li\s+class="nav-item active">(.*?)</li>',
            self.page,
            flags=re.DOTALL,
        )
        self.assertEqual(1, len(active_items))
        self.assertEqual(
            [(PUBLICATIONS_URL, "Publications")],
            [
                (html.unescape(href), visible_text(label))
                for href, label in re.findall(
                    r'<a\s+href="([^"]+)">(.*?)</a>',
                    active_items[0],
                    flags=re.DOTALL,
                )
            ],
        )

    def test_years_are_unique_and_reverse_chronological(self):
        years = [
            int(value)
            for value in re.findall(
                r'<section\b[^>]*\bclass="publication-year"[^>]*'
                r'\bdata-year="(\d{4})"[^>]*>',
                self.page,
            )
        ]
        self.assertTrue(years)
        self.assertEqual(sorted(set(years), reverse=True), years)

    def test_entries_have_exact_semantic_blocks_and_owner(self):
        entries = self.publication_entries()
        self.assertTrue(entries)
        for entry in entries:
            self.assertEqual(1, entry.count('class="publication-title"'))
            self.assertEqual(1, entry.count('class="publication-meta"'))
            owners = re.findall(
                r'<span\s+class="publication-owner">(.*?)</span>',
                entry,
                flags=re.DOTALL,
            )
            self.assertEqual(["Guo Lu"], [visible_text(owner) for owner in owners])

    def test_year_group_labels_wrappers_and_entry_metadata_match(self):
        groups = re.findall(
            r'<section\s+class="publication-year"\s+data-year="(\d{4})">'
            r'(.*?)</section>',
            self.page,
            flags=re.DOTALL,
        )
        self.assertTrue(groups)
        for year, body in groups:
            labels = re.findall(
                r'<div\s+class="publication-year-label">(.*?)</div>',
                body,
                flags=re.DOTALL,
            )
            self.assertEqual([year], [visible_text(label) for label in labels])
            self.assertEqual(1, body.count('class="publication-year-items"'))
            metas = re.findall(
                r'<div\s+class="publication-meta">(.*?)</div>',
                body,
                flags=re.DOTALL,
            )
            self.assertTrue(metas)
            for meta in metas:
                self.assertRegex(meta, rf'<em>[^<]+, {year}</em>')

    def test_optional_title_links_use_absolute_https(self):
        links = re.findall(
            r'<h2\s+class="publication-title">\s*<a\s+href="([^"]+)"',
            self.page,
        )
        for href in links:
            parsed = urlparse(html.unescape(href))
            self.assertEqual("https", parsed.scheme)
            self.assertTrue(parsed.netloc)

    def test_display_titles_are_unique_after_normalization(self):
        titles = re.findall(
            r'<article\s+class="publication-entry"\s+data-title="([^"]+)"',
            self.page,
        )
        self.assertTrue(titles)
        keys = [normalized_title(html.unescape(title)) for title in titles]
        self.assertEqual(len(keys), len(set(keys)))

    def test_rendered_records_exactly_match_approved_inventory(self):
        _, rows = load_inventory()
        approved = {
            normalized_title(row["Canonical title"]): {
                "title": row["Canonical title"],
                "authors": row["Display authors"],
                "venue": row["Venue"],
                "year": row["Year"],
                "destination": "" if row["Destination"] == "—" else row["Destination"],
            }
            for row in rows
            if row["Status"] == "include"
        }
        pattern = (
            r'<article class="publication-entry" data-title="([^"]+)" '
            r'data-authors="([^"]+)" data-venue="([^"]+)" '
            r'data-year="(\d{4})" data-destination="([^"]*)">'
        )
        rendered = {}
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
            r'data-year="(\d{4})" data-destination="([^"]*)">'
            r'(.*?)</article>'
        )
        records = re.findall(pattern, self.page, flags=re.DOTALL)
        self.assertTrue(records)
        for title, authors, venue, year, destination, body in records:
            title_block = re.findall(
                r'<h2\s+class="publication-title">(.*?)</h2>',
                body,
                flags=re.DOTALL,
            )
            self.assertEqual(1, len(title_block))
            self.assertEqual(html.unescape(title), inline_visible_text(title_block[0]))
            links = re.findall(
                r'<h2\s+class="publication-title">\s*<a\s+href="([^"]+)">',
                body,
            )
            self.assertEqual(
                [] if not destination else [html.unescape(destination)],
                [html.unescape(value) for value in links],
            )
            metas = re.findall(
                r'<div\s+class="publication-meta">(.*?)</div>',
                body,
                flags=re.DOTALL,
            )
            self.assertEqual(1, len(metas))
            self.assertEqual(
                f'{html.unescape(authors)} · {html.unescape(venue)}, {year}',
                inline_visible_text(metas[0]),
            )

    def test_responsive_year_layout_contract(self):
        self.assertIn(".publications-page .publication-year", self.css)
        self.assertIn(".publications-page .publication-year-label", self.css)
        self.assertRegex(self.css, r'@media\s*\(max-width:\s*767px\)')

    def test_cloudflare_analytics_is_retained(self):
        self.assertEqual(1, self.page.count(CLOUDFLARE_SCRIPT_URL))
        self.assertEqual(1, self.page.count(CLOUDFLARE_TOKEN))


if __name__ == "__main__":
    unittest.main()
