from pathlib import Path
import html
import json
import re
import unittest
from urllib.parse import urlparse

from tests.test_publications_inventory import load_inventory, normalized_title


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "publication" / "index.html"
HOME = ROOT / "index.html"
CSS = ROOT / "css" / "hugo-academic.css"
ORDER_BASELINE = ROOT / "docs" / "publications-order-baseline.json"
PUBLICATIONS_URL = "https://guolusjtu.github.io/guoluhomepage/publication/"
SCHOLAR_HREF = (
    "https://scholar.google.com/citations?user=R9iwlJcAAAAJ&amp;hl=en"
)
EXPECTED_TITLE = "Publications | Guo Lu (鲁国) | SJTU"
CLOUDFLARE_SCRIPT_URL = "https://static.cloudflareinsights.com/beacon.min.js"
CLOUDFLARE_TOKEN = "7f0b11c30fc344bfb55c572509aea6d0"
TYPE_LABELS = {
    "journal": "Journal Articles",
    "conference-main": "Conference Papers",
}


def included_inventory_by_title():
    _, rows = load_inventory()
    return {
        normalized_title(row["Canonical title"]): row
        for row in rows
        if row["Status"] == "include"
    }


def expected_titles_by_year_and_type():
    baseline = json.loads(ORDER_BASELINE.read_text(encoding="utf-8"))
    inventory = included_inventory_by_title()
    expected = {}
    for year, titles in baseline.items():
        expected[year] = {record_type: [] for record_type in TYPE_LABELS}
        for title in titles:
            row = inventory[normalized_title(title)]
            expected[year][row["Type"]].append(title)
    return expected


def balanced_section_bodies(fragment, opening_pattern):
    """Return capture groups and bodies for matching, properly nested sections."""
    opening = re.compile(opening_pattern)
    section_tag = re.compile(r"</?section\b[^>]*>")
    results = []
    cursor = 0
    while match := opening.search(fragment, cursor):
        depth = 0
        for tag in section_tag.finditer(fragment, match.start()):
            depth += -1 if tag.group(0).startswith("</") else 1
            if depth == 0:
                results.append((*match.groups(), fragment[match.end():tag.start()]))
                cursor = tag.end()
                break
        else:
            raise AssertionError(f"Unclosed section beginning at offset {match.start()}")
    return results


def visible_text(fragment):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def inline_visible_text(fragment):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", fragment)).split())


def css_rule_blocks(stylesheet, selector):
    selector_pattern = r"\s+".join(
        re.escape(component) for component in selector.split()
    )
    return re.findall(
        rf"(?:^|\}})\s*{selector_pattern}\s*\{{([^{{}}]*)\}}",
        stylesheet,
        flags=re.MULTILINE,
    )


def css_declarations(block):
    return {
        name.lower(): value.strip().lower()
        for name, value in re.findall(
            r"(?:^|;)\s*([a-z-]+)\s*:\s*([^;]+?)\s*(?=;|$)",
            block,
            flags=re.IGNORECASE,
        )
    }


def balanced_css_block_after(stylesheet, marker):
    marker_position = stylesheet.index(marker)
    opening_brace = stylesheet.index("{", marker_position + len(marker))
    depth = 0
    for position in range(opening_brace, len(stylesheet)):
        if stylesheet[position] == "{":
            depth += 1
        elif stylesheet[position] == "}":
            depth -= 1
            if depth == 0:
                return stylesheet[opening_brace + 1 : position]
    raise AssertionError(f"Unclosed CSS block after {marker!r}")


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

    def publication_years(self):
        return balanced_section_bodies(
            self.page,
            r'<section class="publication-year" data-year="(\d{4})" '
            r'aria-labelledby="publication-year-\d{4}">',
        )

    @staticmethod
    def publication_type_groups(year_body):
        return balanced_section_bodies(
            year_body,
            r'<section class="publication-type-group" data-publication-type="([^"]+)" '
            r'aria-labelledby="([^"]+)">',
        )

    def test_order_baseline_exactly_matches_included_inventory(self):
        baseline = json.loads(ORDER_BASELINE.read_text(encoding="utf-8"))
        baseline_titles = [title for titles in baseline.values() for title in titles]
        baseline_keys = [normalized_title(title) for title in baseline_titles]
        inventory = included_inventory_by_title()
        inventory_keys = list(inventory)
        self.assertEqual(72, len(baseline_titles))
        self.assertEqual(len(baseline_keys), len(set(baseline_keys)))
        self.assertEqual(set(inventory_keys), set(baseline_keys))
        for year, titles in baseline.items():
            for title in titles:
                self.assertEqual(year, inventory[normalized_title(title)]["Year"], title)

    def test_subgroup_parser_stops_at_each_balanced_section_boundary(self):
        fragment = (
            '<section class="publication-type-group" data-publication-type="journal" '
            'aria-labelledby="journals"><article data-title="Journal"></article></section>'
            '<section class="publication-type-group" data-publication-type="conference-main" '
            'aria-labelledby="conferences"><article data-title="Conference"></article></section>'
        )
        groups = self.publication_type_groups(fragment)
        self.assertEqual(["journal", "conference-main"], [group[0] for group in groups])
        self.assertIn('data-title="Journal"', groups[0][2])
        self.assertNotIn('data-title="Conference"', groups[0][2])
        self.assertIn('data-title="Conference"', groups[1][2])

    def test_each_year_has_only_nonempty_inventory_authorized_subgroups(self):
        expected = expected_titles_by_year_and_type()
        years = dict(self.publication_years())
        self.assertEqual(set(expected), set(years))
        for year, expected_types in expected.items():
            groups = self.publication_type_groups(years[year])
            actual_types = [record_type for record_type, _, _ in groups]
            wanted_types = [
                record_type for record_type in TYPE_LABELS
                if expected_types[record_type]
            ]
            self.assertEqual(wanted_types, actual_types, year)
            for record_type, label_id, body in groups:
                expected_id = f"publication-year-{year}-{record_type}"
                labels = re.findall(
                    r'<h3 id="([^"]+)" class="publication-type-label">(.*?)</h3>',
                    body,
                    flags=re.DOTALL,
                )
                self.assertEqual(
                    [(expected_id, TYPE_LABELS[record_type])],
                    [(item_id, visible_text(label)) for item_id, label in labels],
                )
                self.assertEqual(expected_id, label_id)

    def test_subgroups_preserve_baseline_relative_order_and_classification(self):
        expected = expected_titles_by_year_and_type()
        rendered_titles = []
        for year, year_body in self.publication_years():
            for record_type, _, body in self.publication_type_groups(year_body):
                titles = [
                    html.unescape(title) for title in re.findall(
                        r'<article class="publication-entry" data-title="([^"]+)"',
                        body,
                    )
                ]
                self.assertEqual(expected[year][record_type], titles)
                rendered_titles.extend(titles)
        self.assertEqual(72, len(rendered_titles))
        self.assertEqual(72, len({normalized_title(title) for title in rendered_titles}))

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
            r'<a\b[^>]*href="([^"]+)"[^>]*>\s*More Publications\s*'
            r'<i class="fa fa-angle-double-right"></i>\s*</a>',
            publications,
            flags=re.DOTALL,
        )
        self.assertEqual([PUBLICATIONS_URL], [html.unescape(link) for link in links])

    def test_publication_entries_use_compact_spacing(self):
        blocks = css_rule_blocks(self.css, ".publications-page .publication-entry")
        self.assertEqual(1, len(blocks))
        self.assertEqual("8px", css_declarations(blocks[0]).get("margin-bottom"))

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

    def test_publications_navigation_uses_awards_and_omits_ai_edge(self):
        navigation = self.page.split(
            '<ul class="nav navbar-nav navbar-right">', 1
        )[1].split("</ul>", 1)[0]
        self.assertIn(
            '<a href="https://guolusjtu.github.io/guoluhomepage/#awards">Awards</a>',
            navigation,
        )
        self.assertNotIn("AI@edge", navigation)
        self.assertNotIn("#projects", navigation)

    def test_footer_back_to_top_targets_current_page(self):
        back_to_top = re.findall(
            r'<a\s+href="([^"]+)"\s+id="back_to_top">', self.page
        )
        self.assertEqual(
            ["https://guolusjtu.github.io/guoluhomepage/publication/#top"],
            back_to_top,
        )

    def test_years_are_unique_and_reverse_chronological(self):
        groups = re.findall(
            r'<section class="publication-year" data-year="(\d{4})" '
            r'aria-labelledby="(publication-year-\d{4})">',
            self.page,
        )
        years = [int(year) for year, _ in groups]
        self.assertTrue(years)
        self.assertEqual(sorted(set(years), reverse=True), years)
        ids = [label_id for _, label_id in groups]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual([f"publication-year-{year}" for year in years], ids)

    def test_tutorial_is_absent_and_archive_counts_are_updated(self):
        self.assertNotIn(
            "Learned image and video compression with deep neural networks",
            self.page,
        )
        self.assertEqual(72, len(self.publication_entries()))
        self.assertEqual(
            4,
            len(re.findall(r'<article class="publication-entry"[^>]*data-year="2020"', self.page)),
        )

    def test_compact_venue_names_are_rendered_once_with_year(self):
        expected = {
            "Neural Hamiltonian Deformation Fields for Dynamic Scene Rendering": "SIGGRAPH Asia",
            "Efficient Video Semantic Transmission Needs Generative Latent Priors": "WCSP",
            "TVM: A Tile-based Video Management Framework": "PVLDB",
        }
        for title, venue in expected.items():
            article = re.search(
                rf'<article class="publication-entry" data-title="{re.escape(title)}".*?</article>',
                self.page,
                flags=re.DOTALL,
            )
            self.assertIsNotNone(article)
            fragment = article.group(0)
            self.assertIn(f'data-venue="{venue}"', fragment)
            year = "2023" if venue == "PVLDB" else "2025"
            self.assertEqual(1, fragment.count(f'<em>{venue}, {year}</em>'))
            meta = re.search(
                r'<div class="publication-meta">(.*?)</div>',
                fragment,
                flags=re.DOTALL,
            ).group(1)
            self.assertEqual(1, visible_text(meta).count(year))

    def test_entries_have_exact_semantic_blocks_and_owner(self):
        entries = self.publication_entries()
        self.assertTrue(entries)
        for entry in entries:
            self.assertEqual(1, entry.count('class="publication-title"'))
            self.assertEqual(
                1,
                len(re.findall(r'<h4\s+class="publication-title">.*?</h4>', entry, re.DOTALL)),
            )
            self.assertEqual(1, entry.count('class="publication-meta"'))
            owners = re.findall(
                r'<span\s+class="publication-owner">(.*?)</span>',
                entry,
                flags=re.DOTALL,
            )
            self.assertEqual(["Guo Lu"], [visible_text(owner) for owner in owners])

    def test_year_group_labels_wrappers_and_entry_metadata_match(self):
        groups = re.findall(
            r'<section class="publication-year" data-year="(\d{4})" '
            r'aria-labelledby="(publication-year-\d{4})">'
            r'(.*?)</section>',
            self.page,
            flags=re.DOTALL,
        )
        self.assertTrue(groups)
        for year, label_id, body in groups:
            labels = re.findall(
                r'<h2 id="([^"]+)" class="publication-year-label">(.*?)</h2>',
                body,
                flags=re.DOTALL,
            )
            self.assertEqual([(label_id, year)], [(value_id, visible_text(label)) for value_id, label in labels])
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
            r'<h4\s+class="publication-title">\s*<a\s+href="([^"]+)"',
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
        records = re.findall(pattern, self.page)
        literal_article_count = self.page.count('<article class="publication-entry"')
        self.assertEqual(len(approved), literal_article_count)
        self.assertEqual(literal_article_count, len(self.publication_entries()))
        self.assertEqual(literal_article_count, len(records))
        for title, authors, venue, year, destination in records:
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
                r'<h4\s+class="publication-title">(.*?)</h4>',
                body,
                flags=re.DOTALL,
            )
            self.assertEqual(1, len(title_block))
            self.assertEqual(html.unescape(title), inline_visible_text(title_block[0]))
            links = re.findall(
                r'<h4\s+class="publication-title">\s*<a\s+href="([^"]+)">',
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
        year_blocks = css_rule_blocks(self.css, ".publications-page .publication-year")
        desktop_year_blocks = [
            block
            for block in year_blocks
            if css_declarations(block).get("display") == "grid"
        ]
        self.assertEqual(1, len(desktop_year_blocks))
        year_declarations = css_declarations(desktop_year_blocks[0])
        self.assertEqual("grid", year_declarations.get("display"))
        self.assertEqual(
            "72px minmax(0, 1fr)",
            year_declarations.get("grid-template-columns"),
        )

        desktop_label_blocks = [
            block
            for block in css_rule_blocks(
                self.css, ".publications-page .publication-year-label"
            )
            if css_declarations(block).get("font-size") == "18px"
        ]
        self.assertEqual(1, len(desktop_label_blocks))
        self.assertEqual(
            "0", css_declarations(desktop_label_blocks[0]).get("margin")
        )

        items_blocks = css_rule_blocks(
            self.css, ".publications-page .publication-year-items"
        )
        self.assertEqual(1, len(items_blocks))
        self.assertEqual("0", css_declarations(items_blocks[0]).get("min-width"))

        owner_blocks = css_rule_blocks(
            self.css, ".publications-page .publication-owner"
        )
        self.assertEqual(1, len(owner_blocks))
        self.assertEqual(
            "underline", css_declarations(owner_blocks[0]).get("text-decoration")
        )

        for selector in (
            ".publications-page .publication-title",
            ".publications-page .publication-meta",
        ):
            with self.subTest(selector=selector):
                blocks = [
                    block
                    for block in css_rule_blocks(self.css, selector)
                    if css_declarations(block).get("overflow-wrap") == "anywhere"
                ]
                self.assertEqual(1, len(blocks))
                self.assertEqual(
                    "anywhere", css_declarations(blocks[0]).get("overflow-wrap")
                )

        media_marker = "@media (max-width: 767px)"
        self.assertIn(media_marker, self.css)
        mobile_candidates = [
            balanced_css_block_after(self.css[position:], media_marker)
            for position in (
                match.start()
                for match in re.finditer(re.escape(media_marker), self.css)
            )
        ]
        mobile_candidates = [
            block
            for block in mobile_candidates
            if ".publications-page .publication-year" in block
        ]
        self.assertEqual(1, len(mobile_candidates))
        mobile = mobile_candidates[0]
        mobile_year_blocks = css_rule_blocks(
            mobile, ".publications-page .publication-year"
        )
        self.assertEqual(1, len(mobile_year_blocks))
        self.assertEqual(
            "block", css_declarations(mobile_year_blocks[0]).get("display")
        )
        mobile_label_blocks = css_rule_blocks(
            mobile, ".publications-page .publication-year-label"
        )
        self.assertEqual(1, len(mobile_label_blocks))
        margin_bottom = css_declarations(mobile_label_blocks[0]).get(
            "margin-bottom"
        )
        self.assertIsNotNone(margin_bottom)
        self.assertNotEqual("0", margin_bottom)

    def test_cloudflare_analytics_is_retained(self):
        self.assertEqual(1, self.page.count(CLOUDFLARE_SCRIPT_URL))
        self.assertEqual(1, self.page.count(CLOUDFLARE_TOKEN))


if __name__ == "__main__":
    unittest.main()
