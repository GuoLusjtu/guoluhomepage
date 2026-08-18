from pathlib import Path
import html
import hashlib
import re
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
HOMEPAGE = ROOT / "index.html"
NEWS_ARCHIVE = ROOT / "news" / "index.html"
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
    (
        "2026-07-publications",
        "ACM MM 2026 and ECCV 2026 papers accepted",
        NEWS_ITEMS[2],
    ),
    ("2026-06-challenge", "ECCV 2026 compression challenge", NEWS_ITEMS[3]),
    ("2026-03-jetcas", "IEEE JETCAS Special Issue Guest Editor", NEWS_ITEMS[4]),
    ("2026-02-cvpr", "Two CVPR 2026 papers accepted", NEWS_ITEMS[5]),
)
CLOUDFLARE_TOKEN = "7f0b11c30fc344bfb55c572509aea6d0"
CLOUDFLARE_SCRIPT_URL = "https://static.cloudflareinsights.com/beacon.min.js"
CLOUDFLARE_DATA_ATTRIBUTE = "data-cf-beacon="
CLOUDFLARE_BEACON = (
    "<!-- Cloudflare Web Analytics --><script type='module' "
    f"src='{CLOUDFLARE_SCRIPT_URL}' "
    f"data-cf-beacon='{{\"token\": \"{CLOUDFLARE_TOKEN}\"}}'></script>"
    "<!-- End Cloudflare Web Analytics -->"
)
LEGACY_ANALYTICS_MARKERS = (
    "UA-88925956-1",
    "GoogleAnalyticsObject",
    "www.google-analytics.com/analytics.js",
)
LEGACY_GA_CALL = re.compile(r"\bga\s*\(")
PUBLIC_COUNTER_MARKER = re.compile(
    r"busuanzi|hitwebcounter|visitor[-_ ]?(?:count|counter)|"
    r"pageview[-_ ]?counter|page[-_ ]?counter|"
    r"site[-_ ]?(?:pv|uv)|访问量|访客数|浏览量",
    re.IGNORECASE,
)


def read_text(path):
    return path.read_text(encoding="utf-8")


def publication_entry(homepage, title):
    title_position = homepage.index(title)
    entry_start = homepage.rfind('<div class="pub-list-item"', 0, title_position)
    entry_end = homepage.find('<div class="pub-list-item"', title_position)
    if entry_end == -1:
        entry_end = len(homepage)
    return homepage[entry_start:entry_end]


def section(html_text, section_id):
    start = html_text.index(f'<section id="{section_id}"')
    end = html_text.index("</section>", start) + len("</section>")
    return html_text[start:end]


def normalized_rendered_text(html_fragment):
    without_tags = re.sub(r"<[^>]+>", " ", html.unescape(html_fragment))
    return " ".join(without_tags.split())


class HomepageContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.homepage = read_text(HOMEPAGE)
        cls.html_files = tuple(
            path
            for path in ROOT.rglob("*.html")
            if ".worktrees" not in path.relative_to(ROOT).parts
        )

    def test_homepage_has_current_metadata_description(self):
        expected = (
            '<meta name="description" content="Associate Professor at Shanghai '
            'Jiao Tong University | Video Coding, Multimedia Processing, and '
            'Efficient Multimodal LLMs">'
        )
        self.assertIn(expected, self.homepage)
        self.assertNotIn('content="PhD-SJTU"', self.homepage)

    def test_graduate_course_heading_has_correct_text_and_id(self):
        self.assertIn(
            '<h3 id="graduate-courses">Graduate Course</h3>', self.homepage
        )
        self.assertNotIn("Gradudate Course", self.homepage)
        self.assertNotIn('id="gradudate-courses"', self.homepage)

    def test_aaai_2025_entry_has_official_venue(self):
        entry = publication_entry(
            self.homepage,
            "Controllable Distortion-Perception Tradeoff Through Latent Diffusion",
        )
        self.assertIn(
            "Proceedings of the AAAI Conference on Artificial Intelligence, "
            "39(10), 10725–10733, 2025.",
            entry,
        )
        self.assertNotIn("IEEE Transactions on Image Processing,2022", entry)

    def test_cvpr_2025_iqa_entry_is_highlight_but_not_oral(self):
        entry = publication_entry(
            self.homepage,
            "Image Quality Assessment: From Human to Machine Preference",
        )
        self.assertIn("(Highlight)", entry)
        self.assertNotIn("(Oral)", entry)

    def test_other_valid_oral_publication_labels_are_preserved(self):
        for title in (
            "Knowledge Distillation for Learned Image Compression",
            "Rate-aware Compression for NeRF-based Volumetric Video",
        ):
            with self.subTest(title=title):
                self.assertIn("(Oral)", publication_entry(self.homepage, title))

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
        publications = html.unescape(section(self.homepage, "publications"))
        for lookup_title, expected_title, url, authors, venue in expected:
            with self.subTest(title=expected_title):
                self.assertIn(lookup_title, self.homepage)
                entry = publication_entry(self.homepage, lookup_title)
                decoded_entry = html.unescape(entry)
                self.assertEqual(1, publications.count(expected_title))
                title_link = re.search(
                    r'<h3\b[^>]*>\s*<a\s+href="([^"]+)">\s*(.*?)\s*</a>\s*</h3>',
                    decoded_entry,
                    flags=re.DOTALL,
                )
                self.assertIsNotNone(title_link)
                self.assertEqual(url, title_link.group(1))
                self.assertEqual(expected_title, " ".join(title_link.group(2).split()))
                authors_block = re.search(
                    r'<div class="pub-authors"[^>]*>\s*(.*?)\s*</div>',
                    decoded_entry,
                    flags=re.DOTALL,
                )
                self.assertIsNotNone(authors_block)
                self.assertEqual(authors, " ".join(authors_block.group(1).split()))
                venue_block = re.search(
                    r'<div class="pub-publication">\s*<em>(.*?)</em>',
                    decoded_entry,
                    flags=re.DOTALL,
                )
                self.assertIsNotNone(venue_block)
                self.assertEqual(venue, " ".join(venue_block.group(1).split()))
                self.assertEqual(1, entry.count("<u>Guo Lu</u>"))
                self.assertEqual(1, entry.count("<u>"))
                self.assertEqual(1, entry.count("</u>"))
                self.assertNotRegex(decoded_entry.lower(), r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b")

    def test_2026_publications_have_confirmed_order(self):
        publications = html.unescape(section(self.homepage, "publications"))
        titles = (
            "Next-frame Decoding for Ultra-Low-Bitrate Image Compression with Video Diffusion Priors",
            "Every Packet Counts: Dispersing Information for Loss-Resilient Learned Image Compression",
            "Diff-VF: Training-free High-quality Long Video Generation via Diffusion Model",
            "Large Language Model for Lossless Image Compression with Visual Prompts",
            "Generative Video Communications: Concepts, Key Technologies, and Future Research Trends",
            "Unified Spatiotemporal Token Compression for Video-LLMs at Ultra-Low Retention",
            "Adaptive Learned Image Compression with Graph Neural Networks",
            "Content-Aware Mamba for Learned Image Compression",
        )
        missing_titles = tuple(title for title in titles if title not in publications)
        self.assertEqual((), missing_titles)
        positions = [publications.index(title) for title in titles]
        self.assertEqual(sorted(positions), positions)
        confirmed_order = tuple(sorted(titles, key=publications.index))
        self.assertEqual(
            "Diff-VF: Training-free High-quality Long Video Generation via Diffusion Model",
            confirmed_order[2],
        )
        self.assertEqual(
            "Large Language Model for Lossless Image Compression with Visual Prompts",
            confirmed_order[3],
        )
        self.assertEqual(1, publications.count("[ACMMM'26]"))

    def test_professional_services_have_confirmed_2026_roles(self):
        services = html.unescape(section(self.homepage, "services"))
        service_entries = tuple(
            normalized_rendered_text(item)
            for item in re.findall(r"<li\b[^>]*>(.*?)</li>", services, flags=re.DOTALL)
        )
        associate_editor = "Associate Editor, IEEE T-CSVT, 2025"
        confirmed_roles = (
            "Guest Editor, IEEE Journal on Emerging and Selected Topics in Circuits and Systems (JETCAS) Special Issue on “When Large Models Meet Video Coding: Synergies, Systems, and Hardware Challenges,” 2026.",
            "Challenge Organizer, The Challenge on Ultra-Low Bitrate Image Compression @ ECCV 2026.",
            "Area Chair, International Conference on Learning Representations (ICLR), 2025, 2026, 2027.",
            "Area Chair, Annual Conference on Neural Information Processing Systems (NeurIPS), 2025, 2026.",
            "Senior PC, AAAI, 2021, 2026, 2027.",
        )
        preserved_roles = (
            associate_editor,
            "IEEE VSPC-TC Member, 2025",
            "LAC-Technical Program Chairs, ICASSP Satellite Event Suzhou, China. 2025",
            "Challenge Organizer, Ultra-low Bitrate Video Compression at VCIP, 2025.",
            "Guest Editor, IJCV special issue on Video Understanding and Video Compression. 2021.",
            "Guest Editor, T-CSVT special issue on Learned Visual Data Compression for both Human and Machine. 2022.",
            "Tutorial Organizer, ACM MM Tutorial on Deep Learning for Visual Data Compression, 2021.",
            "Tutorial Organizer, CVPR Tutorial on Learning for Visual Data Compression, 2021.",
            "Tutorial Organizer, VCIP Tutorial on Learned Image and Video Compression with Deep Neural Networks, 2020.",
            "Tutorial Organizer, IEEE AVSS Tutorial on Deep Learning for Video Compression and Understanding, Taipei, 2019",
        )
        self.assertEqual(len(confirmed_roles) + len(preserved_roles), len(service_entries))
        for role in confirmed_roles:
            with self.subTest(role=role):
                self.assertEqual(1, service_entries.count(role))
                self.assertLess(
                    service_entries.index(associate_editor), service_entries.index(role)
                )
        for role in preserved_roles:
            with self.subTest(preserved_role=role):
                self.assertEqual(1, service_entries.count(role))
        preserved_positions = [service_entries.index(role) for role in preserved_roles]
        self.assertEqual(sorted(preserved_positions), preserved_positions)
        for stale_role in (
            "International Conference on Learning Representations(ICLR), 2025.",
            "Annual Conference on Neural Information Processing Systems(NeurIPS), 2025.",
            "Senior PC, AAAI 2021.",
        ):
            with self.subTest(stale_role=stale_role):
                self.assertNotIn(stale_role, services)
        self.assertNotIn("submission deadline", services.lower())
        self.assertNotIn("June 1, 2026", services)
        jetcas_entries = tuple(
            entry for entry in service_entries if entry.startswith("Guest Editor, IEEE")
        )
        challenge_entries = tuple(
            entry
            for entry in service_entries
            if entry.startswith("Challenge Organizer, The Challenge")
        )
        self.assertEqual(1, len(jetcas_entries))
        self.assertEqual(1, len(challenge_entries))
        for entry in (jetcas_entries[0], challenge_entries[0]):
            with self.subTest(no_month_or_deadline=entry):
                self.assertNotRegex(
                    entry.lower(),
                    r"submission deadline|\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b",
                )

    def test_contact_uses_obfuscated_plain_text_and_no_mailto(self):
        envelope_link = re.compile(
            r'<a\s+href="#contact"\s+aria-label="Contact">\s*'
            r'<i\s+class="fa fa-envelope big-icon"[^>]*></i>\s*</a>',
            re.DOTALL,
        )
        contact_section = self.homepage.split(
            '<section id="contact" class="home-section">', 1
        )[1]
        contact_section = contact_section.split("</section>", 1)[0]
        self.assertRegex(self.homepage, envelope_link)
        self.assertIn("luguo2014 AT sjtu.edu.cn", contact_section)
        self.assertNotIn("mailto:", self.homepage)

    def test_homepage_awards_navigation_and_section_use_awards_anchor(self):
        self.assertRegex(
            self.homepage,
            r'<a\s+href="[^"]*#awards">Awards</a>',
        )
        self.assertIn('<section id="awards" class="home-section">', self.homepage)
        self.assertNotRegex(
            self.homepage,
            r'<a\s+href="[^"]*#project">Awards</a>',
        )

    def test_homepage_footer_has_current_year_range(self):
        self.assertIn("&copy; 2020–2026 Guo Lu", self.homepage)
        self.assertNotIn("&copy; 2020 Guo Lu", self.homepage)

    def test_legacy_zongqing_lu_footers_are_preserved(self):
        legacy_footer_count = sum(
            read_text(path).count("&copy; 2018 Zongqing Lu")
            for path in self.html_files
        )
        self.assertEqual(18, legacy_footer_count)

    def test_html_file_discovery_excludes_nested_worktrees(self):
        for path in self.html_files:
            with self.subTest(path=path):
                self.assertNotIn(".worktrees", path.relative_to(ROOT).parts)

    def test_analytics_audit_classifies_all_repository_html_files(self):
        content_pages = tuple(
            path for path in self.html_files if "</body>" in read_text(path)
        )
        redirect_pages = tuple(
            path for path in self.html_files if "</body>" not in read_text(path)
        )
        self.assertEqual(31, len(self.html_files))
        self.assertEqual(19, len(content_pages))
        self.assertEqual(12, len(redirect_pages))
        self.assertEqual(set(self.html_files), set(content_pages) | set(redirect_pages))
        self.assertFalse(set(content_pages) & set(redirect_pages))

    def test_content_pages_have_one_cloudflare_beacon_before_body_end(self):
        content_pages = (
            path for path in self.html_files if "</body>" in read_text(path)
        )
        for path in content_pages:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                page = read_text(path)
                self.assertEqual(1, page.count(CLOUDFLARE_BEACON))
                self.assertEqual(1, page.count(CLOUDFLARE_TOKEN))
                self.assertEqual(1, page.count(CLOUDFLARE_SCRIPT_URL))
                self.assertEqual(1, page.count(CLOUDFLARE_DATA_ATTRIBUTE))
                body_end = page.rindex("</body>")
                self.assertTrue(
                    page[:body_end].rstrip().endswith(CLOUDFLARE_BEACON)
                )

    def test_redirect_stubs_are_unmodified_and_have_no_cloudflare_beacon(self):
        redirect_pages = sorted(
            (
                path
                for path in self.html_files
                if "</body>" not in read_text(path)
            ),
            key=lambda path: path.relative_to(ROOT).as_posix().encode("utf-8"),
        )
        snapshot = b"".join(
            path.relative_to(ROOT).as_posix().encode("utf-8")
            + b"\0"
            + path.read_bytes()
            + b"\0"
            for path in redirect_pages
        )
        for path in redirect_pages:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertNotIn(CLOUDFLARE_BEACON, read_text(path))
        self.assertEqual(
            "fb95fbe62cb3204583afd7b2cba254184babdff19b2e8add1208b973a894e162",
            hashlib.sha256(snapshot).hexdigest(),
        )

    def test_all_html_files_exclude_legacy_google_analytics(self):
        for path in self.html_files:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                page = read_text(path)
                legacy_matches = [
                    marker for marker in LEGACY_ANALYTICS_MARKERS if marker in page
                ]
                legacy_matches.extend(LEGACY_GA_CALL.findall(page))
                self.assertEqual([], legacy_matches)

    def test_all_html_files_exclude_visible_public_counters(self):
        for path in self.html_files:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertNotRegex(read_text(path), PUBLIC_COUNTER_MARKER)

    def test_all_body_pages_have_active_news_navigation(self):
        news_item = (
            r'<li class="nav-item"><a href="https://guolusjtu\.github\.io/'
            r'guoluhomepage/#news">News</a></li>'
        )
        commented_item = re.compile(r"<!--\s*" + news_item + r"\s*-->")
        active_item = re.compile(news_item)
        for path in self.html_files:
            page = read_text(path)
            page_without_comments = re.sub(r"<!--.*?-->", "", page, flags=re.DOTALL)
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                if "</body>" in page:
                    self.assertEqual(1, len(active_item.findall(page_without_comments)))
                    self.assertEqual(0, len(commented_item.findall(page)))
                else:
                    self.assertEqual(0, len(active_item.findall(page_without_comments)))
                    self.assertEqual(0, len(commented_item.findall(page)))

    def test_homepage_news_has_latest_six_and_archive_link(self):
        self.assertEqual(1, self.homepage.count('id="news"'))
        self.assertLess(self.homepage.index('id="bio"'), self.homepage.index('id="news"'))
        self.assertLess(
            self.homepage.index('id="news"'), self.homepage.index('id="publications"')
        )
        news = html.unescape(section(self.homepage, "news"))
        news_entries = tuple(
            normalized_rendered_text(item)
            for item in re.findall(r"<li\b[^>]*>(.*?)</li>", news, flags=re.DOTALL)
        )
        self.assertEqual(NEWS_ITEMS, news_entries)
        more_news_links = re.findall(
            r'<a\b[^>]*href="(?:https://guolusjtu\.github\.io)?/guoluhomepage/news/"[^>]*>\s*More News\s*</a>',
            news,
            flags=re.DOTALL,
        )
        self.assertEqual(1, len(more_news_links))

    def test_news_archive_has_exact_2026_items(self):
        archive = read_text(NEWS_ARCHIVE)
        decoded_archive = html.unescape(archive)
        ids = tuple(fragment for fragment, _, _ in NEWS_FEED_ITEMS)
        news_wrapper_ids = tuple(
            re.findall(r'<(?:article|div)\b[^>]*\bid="(2026-[^"]+)"[^>]*>', archive)
        )
        self.assertEqual(ids, news_wrapper_ids)
        self.assertNotIn('class="article-metadata"', archive)
        self.assertNotIn('class="article-style"', archive)
        self.assertNotRegex(
            archive,
            r'<h2>\s*<a\s+href="[^"]*/news/(?!#)[^"]+/',
        )
        self.assertNotRegex(
            archive,
            r'href="https://guolusjtu\.github\.io/guoluhomepage/news/(?!#|")([^"#]+/)+"',
        )
        positions = []
        for index, (fragment, _, expected_text) in enumerate(NEWS_FEED_ITEMS):
            with self.subTest(fragment=fragment):
                marker = f'id="{fragment}"'
                self.assertEqual(1, archive.count(marker))
                marker_position = archive.index(marker)
                positions.append(marker_position)
                block_start = archive.rfind("<", 0, marker_position)
                if index + 1 < len(ids):
                    next_position = archive.index(f'id="{ids[index + 1]}"')
                    block_end = archive.rfind("<", 0, next_position)
                else:
                    block_end = archive.index('<footer class="site-footer">', marker_position)
                block = html.unescape(archive[block_start:block_end])
                self.assertNotRegex(block, r"<a\b")
                self.assertEqual(1, block.count(expected_text))
                self.assertEqual(1, decoded_archive.count(expected_text))
                rendered = re.sub(r"<[^>]+>", " ", block)
                rendered = " ".join(rendered.split())
                self.assertEqual(expected_text, rendered)
        self.assertEqual(sorted(positions), positions)
        for marker in LEGACY_NEWS_MARKERS:
            with self.subTest(marker=marker):
                self.assertNotIn(html.unescape(marker), decoded_archive)

    def test_news_feed_has_exact_2026_items(self):
        feed_text = read_text(NEWS_FEED)
        root = ET.fromstring(feed_text)
        channel = root.find("channel")
        self.assertIsNotNone(channel)
        atom_link_tag = "{http://www.w3.org/2005/Atom}link"
        channel_children = list(channel)
        expected_metadata = (
            ("title", "News | Guo Lu's Homepage"),
            ("link", "https://guolusjtu.github.io/guoluhomepage/news/"),
            ("description", "News from Guo Lu's Homepage"),
            ("language", "en-us"),
            ("copyright", "© 2020–2026 Guo Lu"),
            ("lastBuildDate", "Tue, 18 Aug 2026 00:00:00 +0800"),
            (atom_link_tag, None),
        )
        self.assertEqual(
            tuple(tag for tag, _ in expected_metadata)
            + ("item",) * len(NEWS_FEED_ITEMS),
            tuple(child.tag for child in channel_children),
        )
        self.assertEqual(
            expected_metadata,
            tuple((child.tag, child.text) for child in channel_children[:7]),
        )
        atom_links = channel.findall(atom_link_tag)
        self.assertEqual(1, len(atom_links))
        self.assertEqual(
            {
                "href": "https://guolusjtu.github.io/guoluhomepage/news/index.xml",
                "rel": "self",
                "type": "application/rss+xml",
            },
            atom_links[0].attrib,
        )
        items = channel.findall("item")
        self.assertEqual(6, len(items))
        for item, (fragment, title, description) in zip(items, NEWS_FEED_ITEMS):
            with self.subTest(fragment=fragment):
                expected_url = (
                    "https://guolusjtu.github.io/guoluhomepage/news/#" + fragment
                )
                item_children = list(item)
                self.assertEqual(
                    (
                        ("title", title),
                        ("link", expected_url),
                        ("guid", expected_url),
                        ("description", description),
                    ),
                    tuple((child.tag, child.text) for child in item_children),
                )
                guid = item_children[2]
                self.assertEqual(expected_url, guid.text)
                self.assertEqual("true", guid.get("isPermaLink"))
                self.assertEqual({"isPermaLink": "true"}, guid.attrib)
        decoded_feed = html.unescape(feed_text)
        self.assertNotIn("Zongqing", decoded_feed)
        for marker in LEGACY_NEWS_MARKERS:
            with self.subTest(marker=marker):
                self.assertNotIn(html.unescape(marker), decoded_feed)
        self.assertNotRegex(decoded_feed, r"/news/(?!#|index\.xml)[^<#\s]+/")

    def test_news_directory_has_no_detail_pages(self):
        files = {
            path.relative_to(ROOT).as_posix()
            for path in NEWS_ARCHIVE.parent.rglob("*")
            if path.is_file()
        }
        directories = {
            path.relative_to(ROOT).as_posix()
            for path in NEWS_ARCHIVE.parent.rglob("*")
            if path.is_dir()
        }
        self.assertEqual({"news/index.html", "news/index.xml"}, files)
        self.assertEqual(set(), directories)

    def test_unrelated_projects_anchors_are_preserved(self):
        projects_count = sum(
            read_text(path).count("#projects") for path in self.html_files
        )
        self.assertEqual(18, projects_count)


if __name__ == "__main__":
    unittest.main()
