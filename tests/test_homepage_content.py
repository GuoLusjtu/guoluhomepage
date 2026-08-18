from pathlib import Path
import html
import hashlib
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse


ROOT = Path(__file__).resolve().parents[1]
HOMEPAGE = ROOT / "index.html"
STYLESHEET = ROOT / "css" / "hugo-academic.css"
NEWS_ARCHIVE = ROOT / "news" / "index.html"
NEWS_FEED = ROOT / "news" / "index.xml"
NEWS_ITEMS = (
    "2026.8 Serving as an Area Chair for ICLR and as a Senior PC member for AAAI.",
    "2026.8 Two papers were accepted by ACM TOMM and IEEE T-CSVT.",
    "2026.7 Two papers were accepted by ACM MM 2026, and one paper was accepted by ECCV 2026.",
    "2026.6 Organizing the Challenge on Ultra-Low Bitrate Image Compression at ECCV 2026.",
    "2026.3 Serving as a Guest Editor for an IEEE JETCAS Special Issue.",
    "2026.2 Two papers were accepted by CVPR 2026.",
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
    ("2026-08-service", "ICLR and AAAI service roles", NEWS_ITEMS[0]),
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
SITE_BASE_URL = "https://guolusjtu.github.io/guoluhomepage/"
PUBLICATIONS_URL = SITE_BASE_URL + "#publications"
OWNER_SCHOLAR_URL = (
    "https://scholar.google.com/citations?user=R9iwlJcAAAAJ&hl=en"
)
RECRUITMENT_COPY = (
    "We are looking for self-motivated Ph.D./M.S. students, research interns, "
    "and postdoctoral fellows. Prospective applicants are welcome to send a CV "
    "and transcript by email."
)
CHINESE_HOMEPAGE_URL = "https://icisee.sjtu.edu.cn/jiaoshiml/luguo.html"
RETAINED_HTML_PATHS = (
    "404.html",
    "index.html",
    "news/index.html",
    "project/index.html",
    "publication/index.html",
)
STANDARD_SHELL_PATHS = (
    "404.html",
    "index.html",
    "news/index.html",
    "project/index.html",
)
REMOVED_PATHS = (
    "publication/index.xml",
    "index.xml",
    "home/index.xml",
    "project/index.xml",
    "categories/index.xml",
    "files/citations/infocom18.bib",
)
PUBLICATIONS_SECTION_CANONICAL_SHA256 = (
    "7535987340efe3c0c14e0b2bca12e9205aa452469b70b47637740f8d29adca91"
)
OLD_PUBLICATIONS_SCHOLAR_HREF = (
    b"https://scholar.google.com/citations?user=R9iwlJcAAAAJ&hl=en/"
)
CORRECTED_PUBLICATIONS_SCHOLAR_HREF = (
    b"https://scholar.google.com/citations?user=R9iwlJcAAAAJ&hl=en"
)
PROJECT_TITLES = (
    "Learning to Cooperate",
    "Distributed Video Processing Using Deep Learning on Networked Devices",
    "Building Smartphone Networks",
    "Health Sensing Using Mobile Devices",
    "Exploring Social Structure for Network Designs",
)
PROJECT_TAG_LABELS = (
    "Reinforcement Learning",
    "Multiagent Learning",
    "Deep Learning",
    "Edge Computing",
    "Smartphones",
    "Opportunistic Networking",
    "Data Offload",
    "Infectious Diseases",
    "Human Contact Networks",
    "Respiratory Symptoms",
    "Smartphones",
    "Social Networks",
    "Community",
    "Information Diffusion",
)
PROJECT_ASSET_SHA256 = {
    "atoc.png": "9d961c904cb14966c7298e709b48d4461eb4a6483e68ccaa612a55876c888c20",
    "crowdvision.png": "784a2c7267a3e5e083329368aa71927d490fbdfcc804b0a814d16147deda0aaa",
    "dgn.png": "44ffd593c90078d71e7dc9817ec0a12d6da628ea2db61487b780fd7ab6b74f90",
    "healthcare.jpg": "b0916fb9bb9aa257a8bb67e71ff8dc611d6dea26fbe311f17388bb34ead706f0",
    "learning-preview.png": "3a46ee5e3066e9967f07dc12e187935c2228b6e4f1f70e88b66ca547843dfd82",
    "netvision.png": "99e901387311b50b3daf1bd421416507fe3a4fa9d3a94c1c78239bdb47580f29",
    "teamphone.png": "968333aa69e3eb1ca404f1e484c0908ccd63d423ed6a45022e01b753bf2a3414",
}
PROJECT_SUMMARIES_SHA256 = (
    "3bf39900daf774c964e14583d9cd9ecc780087668885b3b59683fd7c7bbeaa9f"
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


def raw_section(document, section_id):
    start = document.index(f'<section id="{section_id}"'.encode("utf-8"))
    end = document.index(b"</section>", start) + len(b"</section>")
    return document[start:end]


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
    declarations = re.findall(
        r"(?:^|;)\s*([a-z-]+)\s*:\s*([^;]+?)\s*(?=;|$)",
        block,
        flags=re.IGNORECASE,
    )
    return {name.lower(): value.strip().lower() for name, value in declarations}


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

    def test_bio_has_exact_accessible_join_us_callout(self):
        bio = section(self.homepage, "bio")
        callout_matches = tuple(
            re.finditer(
                r'<aside\s+class="join-us-callout"\s+'
                r'aria-labelledby="join-us-heading">(.*?)</aside>',
                bio,
                flags=re.DOTALL,
            )
        )
        self.assertEqual(1, len(callout_matches))

        callout_match = callout_matches[0]
        callout = callout_match.group(1)
        before_callout = bio[: callout_match.start()]
        self.assertRegex(before_callout, r"</p>\s*$")
        self.assertEqual(
            len(re.findall(r"<p(?:\s|>)", before_callout)),
            before_callout.count("</p>"),
        )
        headings = re.findall(
            r'<h3\s+id="join-us-heading">(.*?)</h3>',
            callout,
            flags=re.DOTALL,
        )
        paragraphs = re.findall(r"<p>(.*?)</p>", callout, flags=re.DOTALL)
        links = re.findall(
            r'<a\s+href="([^"]+)">(.*?)</a>', callout, flags=re.DOTALL
        )
        self.assertEqual(["Join Us"], [normalized_rendered_text(x) for x in headings])
        self.assertEqual(
            [RECRUITMENT_COPY],
            [normalized_rendered_text(x) for x in paragraphs],
        )
        self.assertEqual(1, len(links))
        self.assertEqual(CHINESE_HOMEPAGE_URL, html.unescape(links[0][0]))
        self.assertEqual("中文主页 →", normalized_rendered_text(links[0][1]))
        decoded_bio = html.unescape(bio)
        self.assertEqual(1, decoded_bio.count(CHINESE_HOMEPAGE_URL))
        self.assertEqual(1, decoded_bio.count("中文主页 →"))

        self.assertNotRegex(bio, r'<span\b[^>]*style="[^"]*color\s*:\s*red')
        self.assertNotIn("CV/resume", bio)

    def test_homepage_source_and_stylesheet_are_strict_utf8(self):
        for path in (HOMEPAGE, STYLESHEET):
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                decoded = path.read_bytes().decode("utf-8", errors="strict")
                self.assertNotIn("\ufffd", decoded)

        self.assertEqual(1, self.homepage.count("2020&ndash;2022"))
        rendered_bio = normalized_rendered_text(section(self.homepage, "bio"))
        self.assertIn(
            "Beijing Institute of Technology (2020–2022).", rendered_bio
        )

    def test_owner_google_scholar_links_use_exact_corrected_url(self):
        owner_scholar_links = tuple(
            html.unescape(href)
            for href in re.findall(r'<a\b[^>]*\bhref="([^"]+)"', self.homepage)
            if "scholar.google.com/citations?user=R9iwlJcAAAAJ" in html.unescape(href)
        )
        self.assertEqual((OWNER_SCHOLAR_URL, OWNER_SCHOLAR_URL), owner_scholar_links)
        self.assertNotIn("hl=en/", self.homepage)

    def test_join_us_callout_has_exact_responsive_accessible_css(self):
        stylesheet = read_text(STYLESHEET)
        callout_blocks = css_rule_blocks(stylesheet, ".join-us-callout")
        self.assertEqual(1, len(callout_blocks))
        callout_declarations = css_declarations(callout_blocks[0])
        self.assertEqual("#f4f8fb", callout_declarations.get("background"))
        self.assertEqual(
            "4px solid #2f6f9f", callout_declarations.get("border-left")
        )
        self.assertEqual("15px 17px", callout_declarations.get("padding"))
        self.assertEqual("3px", callout_declarations.get("border-radius"))
        self.assertNotIn("width", callout_declarations)
        self.assertNotIn("height", callout_declarations)

        media = balanced_css_block_after(stylesheet, "@media (max-width: 767px)")
        mobile_blocks = css_rule_blocks(media, ".join-us-callout")
        self.assertEqual(1, len(mobile_blocks))
        self.assertEqual(
            "12px 14px", css_declarations(mobile_blocks[0]).get("padding")
        )

        link_blocks = css_rule_blocks(
            stylesheet, ".join-us-callout a,\n.join-us-callout a:visited"
        )
        self.assertEqual(1, len(link_blocks))
        self.assertEqual("#2f6f9f", css_declarations(link_blocks[0]).get("color"))

        interaction_blocks = css_rule_blocks(
            stylesheet, ".join-us-callout a:hover,\n.join-us-callout a:focus"
        )
        self.assertEqual(1, len(interaction_blocks))
        interaction_declarations = css_declarations(interaction_blocks[0])
        self.assertEqual("#254f70", interaction_declarations.get("color"))
        self.assertEqual(
            "underline", interaction_declarations.get("text-decoration")
        )

    def test_retained_archive_shells_have_current_metadata_description(self):
        expected = "Associate Professor at Shanghai Jiao Tong University"
        for relative_path in ("404.html", "news/index.html", "project/index.html"):
            page = read_text(ROOT / relative_path)
            descriptions = re.findall(
                r'<meta\s+name="description"\s+content="([^"]*)">', page
            )
            with self.subTest(path=relative_path):
                self.assertEqual([expected], descriptions)

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
            "Guest Editor, IEEE JETCAS Special Issue on “When Large Models Meet Video Coding: Synergies, Systems, and Hardware Challenges,” 2026.",
            "Challenge Organizer, The Challenge on Ultra-Low Bitrate Image Compression @ ECCV 2026.",
            "Area Chair, International Conference on Learning Representations (ICLR), 2025, 2026.",
            "Area Chair, Annual Conference on Neural Information Processing Systems (NeurIPS), 2025, 2026.",
            "Senior PC, AAAI, 2021, 2026.",
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
        self.assertNotIn("2027", services)
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

    def test_homepage_publications_section_is_byte_for_byte_unchanged(self):
        publications = raw_section(HOMEPAGE.read_bytes(), "publications")
        canonical_publications = publications.replace(
            OLD_PUBLICATIONS_SCHOLAR_HREF,
            CORRECTED_PUBLICATIONS_SCHOLAR_HREF,
        )
        self.assertEqual(
            PUBLICATIONS_SECTION_CANONICAL_SHA256,
            hashlib.sha256(canonical_publications).hexdigest(),
        )

    def test_project_body_and_image_assets_are_preserved(self):
        project = read_text(ROOT / "project" / "index.html")
        summaries = re.findall(
            r'<p\b[^>]*class="project-summary"[^>]*>(.*?)</p>',
            project,
            flags=re.DOTALL,
        )
        self.assertEqual(5, len(summaries))
        normalized_summaries = "\n".join(
            normalized_rendered_text(summary) for summary in summaries
        )
        self.assertEqual(
            PROJECT_SUMMARIES_SHA256,
            hashlib.sha256(normalized_summaries.encode("utf-8")).hexdigest(),
        )
        rendered_project = normalized_rendered_text(project)
        for title in PROJECT_TITLES:
            with self.subTest(title=title):
                self.assertEqual(1, rendered_project.count(title))
        rendered_tags = tuple(
            normalized_rendered_text(fragment)
            for fragment in re.findall(
                r'<span class="article-tags">(.*?)</span>',
                project,
                flags=re.DOTALL,
            )
        )
        actual_tag_labels = tuple(
            label.strip()
            for tag_group in rendered_tags
            for label in tag_group.split(",")
        )
        self.assertEqual(PROJECT_TAG_LABELS, actual_tag_labels)
        for image_reference in (
            "/img/sponsors/nsfc.jpg",
            "/img/sponsors/huawei.png",
            "/img/sponsors/hikvision.jpeg",
            "/img/sponsors/tencent.png",
        ):
            with self.subTest(image_reference=image_reference):
                self.assertEqual(1, project.count(f'src="{image_reference}"'))

        asset_directory = ROOT / "img" / "project"
        actual_assets = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in asset_directory.iterdir()
            if path.is_file()
        }
        self.assertEqual(PROJECT_ASSET_SHA256, actual_assets)

    def test_only_retained_html_pages_remain(self):
        actual = tuple(
            sorted(path.relative_to(ROOT).as_posix() for path in self.html_files)
        )
        self.assertEqual(RETAINED_HTML_PATHS, actual)

    def test_html_file_discovery_excludes_nested_worktrees(self):
        for path in self.html_files:
            with self.subTest(path=path):
                self.assertNotIn(".worktrees", path.relative_to(ROOT).parts)

    def test_analytics_audit_classifies_all_repository_html_files(self):
        expected = {ROOT / path for path in RETAINED_HTML_PATHS}
        self.assertEqual(expected, set(self.html_files))
        for path in self.html_files:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertIn("</body>", read_text(path))

    def test_content_pages_have_one_cloudflare_beacon_before_body_end(self):
        for relative_path in RETAINED_HTML_PATHS:
            path = ROOT / relative_path
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

    def test_publication_index_redirects_to_homepage_publications(self):
        redirect = read_text(ROOT / "publication" / "index.html")
        canonical = re.findall(
            r'<link\s+rel="canonical"\s+href="([^"]+)"\s*/?>', redirect
        )
        refresh = re.findall(
            r'<meta\s+http-equiv="refresh"\s+content="\s*0\s*;\s*url=([^"]+)"\s*/?>',
            redirect,
            flags=re.IGNORECASE,
        )
        fallback = tuple(
            (attributes, body)
            for attributes, body in re.findall(
                r"<a\b([^>]*)>(.*?)</a>", redirect, flags=re.DOTALL | re.IGNORECASE
            )
            if re.search(
                rf'href=["\']{re.escape(PUBLICATIONS_URL)}["\']',
                attributes,
                flags=re.IGNORECASE,
            )
        )
        self.assertEqual([PUBLICATIONS_URL], canonical)
        self.assertEqual([PUBLICATIONS_URL], refresh)
        self.assertEqual(1, len(fallback))
        fallback_attributes, fallback_body = fallback[0]
        self.assertTrue(normalized_rendered_text(fallback_body))
        self.assertNotRegex(
            fallback_attributes,
            re.compile(r"(?:^|\s)hidden(?:\s|=|$)", re.IGNORECASE),
        )
        self.assertNotRegex(
            fallback_attributes,
            re.compile(r"aria-hidden\s*=\s*[\"']?true", re.IGNORECASE),
        )
        self.assertNotRegex(
            fallback_attributes,
            re.compile(
                r"style\s*=\s*[\"'][^\"']*(?:display\s*:\s*none|visibility\s*:\s*hidden)",
                re.IGNORECASE,
            ),
        )
        self.assertEqual(1, redirect.count(CLOUDFLARE_BEACON))
        self.assertNotRegex(redirect, r"/publication/[^\"#]+/")

    def test_legacy_generated_archives_and_citation_are_absent(self):
        for relative_path in REMOVED_PATHS:
            with self.subTest(path=relative_path):
                self.assertFalse((ROOT / relative_path).exists())
        self.assertFalse((ROOT / "tags").exists())

    def test_retained_site_owner_identity_contains_no_zongqing(self):
        retained = tuple(ROOT / path for path in RETAINED_HTML_PATHS) + (
            NEWS_FEED,
            ROOT / "sitemap.xml",
        )
        for path in retained:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertNotRegex(read_text(path), re.compile("zongqing", re.I))

    def test_404_has_no_copied_publications_and_links_home(self):
        not_found = read_text(ROOT / "404.html")
        self.assertNotRegex(not_found, r'href="[^"]*/publication/[^"#]+/"')
        for copied_title in (
            "Learning Fairness in Multi-Agent Systems",
            "CrowdVision: A Computing Platform",
            "Cooperative Data Offload in Opportunistic Networks",
            "Community Detection in Weighted Networks",
        ):
            with self.subTest(title=copied_title):
                self.assertNotIn(copied_title, html.unescape(not_found))
        self.assertRegex(
            not_found,
            rf'<a\s+href="{re.escape(SITE_BASE_URL)}"[^>]*>[^<]+</a>',
        )

    def test_sitemap_contains_only_retained_indexable_routes(self):
        sitemap_root = ET.fromstring(read_text(ROOT / "sitemap.xml"))
        namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        locations = tuple(
            node.text for node in sitemap_root.findall(f"{namespace}url/{namespace}loc")
        )
        self.assertEqual(
            (
                SITE_BASE_URL,
                SITE_BASE_URL + "news/",
                SITE_BASE_URL + "project/",
            ),
            locations,
        )

    def test_retained_html_links_do_not_target_removed_local_routes(self):
        removed_route = re.compile(
            r"^(?:"
            r"tags(?:/|$)|"
            r"home(?:/|$)|"
            r"categories(?:/|$)|"
            r"publication/(?!$).+|"
            r"news/(?!$|index\.xml$).+|"
            r"project/(?!$).+|"
            r"(?:index|home/index|project/index|categories/index)\.xml$"
            r")"
        )
        failures = []
        for relative_path in RETAINED_HTML_PATHS:
            page = read_text(ROOT / relative_path)
            page_url = urljoin(SITE_BASE_URL, relative_path)
            for href in re.findall(r'href=["\']([^"\']+)', page, re.I):
                parsed = urlparse(urljoin(page_url, html.unescape(href)))
                if parsed.netloc and parsed.netloc.lower() != "guolusjtu.github.io":
                    continue
                path = parsed.path.lstrip("/")
                if path.startswith("guoluhomepage/"):
                    path = path[len("guoluhomepage/") :]
                if removed_route.match(path):
                    failures.append((relative_path, href))
        self.assertEqual([], failures)

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
        for relative_path in STANDARD_SHELL_PATHS:
            path = ROOT / relative_path
            page = read_text(path)
            page_without_comments = re.sub(r"<!--.*?-->", "", page, flags=re.DOTALL)
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertEqual(1, len(active_item.findall(page_without_comments)))
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
                self.assertNotRegex(block, re.compile(r"<a\b", re.IGNORECASE))
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

    def test_retained_standard_shells_preserve_projects_navigation(self):
        projects_count = sum(
            read_text(ROOT / path).count("#projects")
            for path in STANDARD_SHELL_PATHS
        )
        self.assertEqual(3, projects_count)


if __name__ == "__main__":
    unittest.main()
