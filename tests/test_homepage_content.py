from pathlib import Path
import hashlib
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOMEPAGE = ROOT / "index.html"
NEWS_ARCHIVE = ROOT / "news" / "index.html"


def read_text(path):
    return path.read_text(encoding="utf-8")


def publication_entry(homepage, title):
    title_position = homepage.index(title)
    entry_start = homepage.rfind('<div class="pub-list-item"', 0, title_position)
    entry_end = homepage.find('<div class="pub-list-item"', title_position)
    if entry_end == -1:
        entry_end = len(homepage)
    return homepage[entry_start:entry_end]


class HomepageContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.homepage = read_text(HOMEPAGE)
        cls.html_files = tuple(ROOT.rglob("*.html"))

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

    def test_all_news_navigation_items_are_commented_and_none_are_active(self):
        news_item = (
            r'<li class="nav-item"><a href="https://guolusjtu\.github\.io/'
            r'guoluhomepage/#news">News</a></li>'
        )
        commented_item = re.compile(r"<!--\s*" + news_item + r"\s*-->")
        active_item = re.compile(news_item)
        commented_count = 0
        active_count = 0
        for path in self.html_files:
            page = read_text(path)
            commented_count += len(commented_item.findall(page))
            page_without_comments = re.sub(r"<!--.*?-->", "", page, flags=re.DOTALL)
            active_count += len(active_item.findall(page_without_comments))
        self.assertEqual(19, commented_count)
        self.assertEqual(0, active_count)

    def test_news_archive_body_and_known_titles_are_preserved(self):
        archive_bytes = NEWS_ARCHIVE.read_bytes()
        separator = b"</nav>"
        self.assertIn(separator, archive_bytes)
        archive_body = archive_bytes.split(separator, 1)[1]
        self.assertEqual(
            "de25264193ea6089fd830c83d0d26f815dc5485fa82467fe77c8f51e7c77efee",
            hashlib.sha256(archive_body).hexdigest(),
        )
        archive_text = archive_body.decode("utf-8")
        for title in (
            "One paper accepted at ICLR&#39;20",
            "One paper accepted at TON",
            "One paper accepted at AAAI&#39;20",
            "One paper accepted at TMC",
            "One paper accepted at NIPS&#39;19",
            "GENE accepted at ERL&#39;19 as a Spotlight Talk",
            "One paper accepted at NIPS&#39;18",
            "One paper accepted at INFOCOM&#39;18",
        ):
            with self.subTest(title=title):
                self.assertIn(title, archive_text)

    def test_unrelated_projects_anchors_are_preserved(self):
        projects_count = sum(
            read_text(path).count("#projects") for path in self.html_files
        )
        self.assertEqual(18, projects_count)


if __name__ == "__main__":
    unittest.main()
