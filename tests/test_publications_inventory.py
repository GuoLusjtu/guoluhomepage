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
CURATION_EXCLUSIONS = {
    "DiFace: Cross-Modal Face Recognition through Controlled Diffusion",
    "Multi-Style Facial Sketch Synthesis through Masked Generative Modeling",
    "FreeFlow: A Unified Viewpoint on Diffusion Probabilistic Models via Optimal Transport and Fluid Mechanics",
    "Frame-Level Complexity Control for Practical Encoder x265",
    "An Efficient and Flexible Complexity Control Method for Versatile Video Coding",
    "A unified efficient deep image compression framework and its application on human-centric Task",
    "Video Encoding Enhancement via Content-Aware Spatial and Temporal Super-Resolution",
    "基于 Transformer 的深度条件视频压缩",
    "A Transformer based deep conditional video compression",
    "A novel frame rate up conversion using iterative non-local means interpolation",
}


def normalized_title(value):
    value = unicodedata.normalize("NFKC", value).lower()
    value = re.sub(r"\s*supplementary materials?\s*$", "", value)
    return "".join(character for character in value if character.isalnum())


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
        scholar_records = re.search(r"^Scholar records: (\d+)$", self.text, re.M)
        self.assertIsNotNone(scholar_records)
        declared = int(scholar_records.group(1))
        discovered = sum(row["Scholar title"] not in {"", "—"} for row in self.rows)
        self.assertEqual(declared, discovered)
        counts = {status: sum(row["Status"] == status for row in self.rows) for status in STATUSES}
        expected = "Summary: " + "; ".join(
            f"{key}={counts[key]}" for key in ("include", "exclude", "needs-review")
        )
        self.assertIn(expected, self.text)

    def test_learned_compression_tutorial_is_excluded(self):
        matches = [
            row for row in self.rows
            if row["Canonical title"] == "Learned image and video compression with deep neural networks"
        ]
        self.assertEqual(1, len(matches))
        self.assertEqual("excluded", matches[0]["Type"])
        self.assertEqual("exclude", matches[0]["Status"])
        self.assertIn("tutorial", matches[0]["Reason"].lower())

    def test_compact_venue_names_are_normalized(self):
        expected = {
            "Neural Hamiltonian Deformation Fields for Dynamic Scene Rendering": "SIGGRAPH Asia",
            "Efficient Video Semantic Transmission Needs Generative Latent Priors": "WCSP",
            "TVM: A Tile-based Video Management Framework": "PVLDB",
        }
        included = {
            row["Canonical title"]: row["Venue"]
            for row in self.rows
            if row["Status"] == "include"
        }
        for title, venue in expected.items():
            self.assertEqual(venue, included[title])

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
                    self.assertNotIn(row[field], {"", "—"})
                authors = [author.strip() for author in row["Display authors"].split(",")]
                self.assertEqual(1, authors.count("Guo Lu"))
                if int(row["Original author count"]) > 10:
                    self.assertIn("…", authors)
                else:
                    self.assertNotIn("…", authors)
            if row["Status"] != "include":
                self.assertNotIn(row["Reason"], {"", "—"})
            if row["Provenance"] == "user-confirmed":
                self.assertNotIn(row["Reason"], {"", "—"})
            elif row["Status"] != "exclude":
                self.assertNotIn(row["Authority"], {"", "—"})
            for field in ("Destination", "Authority"):
                if row[field] != "—":
                    parsed = urlparse(row[field])
                    self.assertEqual("https", parsed.scheme)
                    self.assertTrue(parsed.netloc)
            if row["Year authority"] not in {"—", "user-confirmed"}:
                parsed = urlparse(row["Year authority"])
                self.assertEqual("https", parsed.scheme)
                self.assertTrue(parsed.netloc)
            elif row["Year authority"] == "—":
                self.assertEqual("exclude", row["Status"])

    def test_inventory_contains_no_bare_root_evidence_urls(self):
        for row in self.rows:
            for field in ("Destination", "Authority", "Year authority"):
                value = row[field]
                if value in {"—", "user-confirmed"}:
                    continue
                parsed = urlparse(value)
                self.assertNotIn(parsed.path, {"", "/"}, f"{row['Scholar title']}: {field}")

    def test_normalized_title_preserves_unicode_alphanumerics(self):
        self.assertEqual("café视频压缩2026", normalized_title("Café：视频压缩 2026"))

    def test_normalized_title_removes_punctuation_and_terminal_supplementary_suffix(self):
        self.assertEqual(
            "diffvftrainingfree",
            normalized_title("Diff-VF: Training-Free — Supplementary Materials"),
        )
        self.assertEqual(
            "supplementarymaterialanalysis",
            normalized_title("Supplementary Material Analysis"),
        )

    def test_included_titles_are_unique_after_normalization(self):
        keys = [
            normalized_title(row["Canonical title"])
            for row in self.rows
            if row["Status"] == "include"
        ]
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

    def test_guo_lu_curation_exclusions_are_applied(self):
        for title in CURATION_EXCLUSIONS:
            matches = [
                row for row in self.rows
                if normalized_title(row["Canonical title"]) == normalized_title(title)
            ]
            self.assertEqual(1, len(matches), title)
            self.assertEqual("exclude", matches[0]["Status"], title)
            self.assertIn("Guo Lu's curation decision", matches[0]["Reason"], title)

    def test_content_adaptive_latents_has_verified_eccv_metadata(self):
        title = "Content adaptive latents and decoder for neural image compression"
        matches = [
            row for row in self.rows
            if normalized_title(row["Canonical title"]) == normalized_title(title)
        ]
        self.assertEqual(1, len(matches))
        row = matches[0]
        self.assertEqual("Guanbo Pan, Guo Lu, Zhihao Hu, Dong Xu", row["Display authors"])
        self.assertEqual("ECCV", row["Venue"])
        self.assertEqual("2022", row["Year"])
        self.assertEqual("include", row["Status"])

    def test_aaai_2025_papers_are_conference_publications(self):
        titles = {
            "L3TC: Leveraging RWKV for Learned Lossless Low-Complexity Text Compression",
            "Controllable Distortion-Perception Tradeoff Through Latent Diffusion for Neural Image Compression",
        }
        for title in titles:
            matches = [
                row for row in self.rows
                if normalized_title(row["Canonical title"]) == normalized_title(title)
            ]
            self.assertEqual(1, len(matches), title)
            row = matches[0]
            self.assertEqual("include", row["Status"], title)
            self.assertEqual("AAAI", row["Venue"], title)
            self.assertEqual("2025", row["Year"], title)
            self.assertEqual("conference-main", row["Type"], title)
