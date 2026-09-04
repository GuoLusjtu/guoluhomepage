import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT_PATH = ROOT / "docs" / "cv-content.md"
INVENTORY_PATH = ROOT / "docs" / "publications-inventory.md"

EXPECTED_TITLES = [
    "Next-frame decoding for ultra-low-bitrate image compression with video diffusion priors",
    "Every Packet Counts: Dispersing Information for Loss-Resilient Learned Image Compression",
    "Diff-VF: Training-free High-quality Long Video Generation via Diffusion Model",
    "Large language model for lossless image compression with visual prompts",
    "Generative Video Communications: Concepts, Key Technologies, and Future Research Trends",
    "Unified spatiotemporal token compression for video-llms at ultra-low retention",
    "Adaptive Learned Image Compression with Graph Neural Networks",
    "Content-aware mamba for learned image compression",
    "Knowledge Distillation for Learned Image Compression",
    "Controllable Distortion-Perception Tradeoff Through Latent Diffusion for Neural Image Compression",
    "SMC++: Masked Learning of Unsupervised Video Semantic Compression",
    "Image Quality Assessment: From Human to Machine Preference",
    "Towards Trustworthy Multimodal Moderation via Policy-Aligned Reasoning and Hierarchical Labeling",
    "Implicit-Explicit Integrated Representations for Multi-View Video Compression",
    "VARFVV: View-Adaptive Real-Time Interactive Free-View Video Streaming With Edge Computing",
    "A Coding Framework and Benchmark Towards Low-Bitrate Video Understanding",
    "Neural rate control for learned video compression",
    "Preprocessing Enhanced Image Compression for Machine Vision",
    "Rate-aware Compression for NeRF-based Volumetric Video",
    "FVC: A New Framework towards Deep Video Compression in Feature Space",
    "DVC: An End-To-End Deep Video Compression Framework",
]


def parse_markdown_table(text, heading):
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        return []
    rows = []
    for line in match.group(1).splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and not all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            rows.append(cells)
    return rows[1:]


def parse_inventory():
    lines = INVENTORY_PATH.read_text(encoding="utf-8").splitlines()
    header_index = next(i for i, line in enumerate(lines) if line.startswith("| Scholar title |"))
    headers = [cell.strip() for cell in lines[header_index].strip("|").split("|")]
    records = []
    for line in lines[header_index + 2 :]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        records.append(dict(zip(headers, cells)))
    return records


class CvContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = CONTENT_PATH.read_text(encoding="utf-8")
        cls.publication_rows = parse_markdown_table(cls.content, "Selected Publications")
        cls.evidence_rows = parse_markdown_table(cls.content, "Evidence")
        cls.inventory = parse_inventory()

    def test_exact_21_selected_publications_resolve_once_to_included_inventory(self):
        self.assertEqual(21, len(self.publication_rows))
        actual_titles = [row[0] for row in self.publication_rows]
        self.assertEqual(EXPECTED_TITLES, actual_titles)
        included = [row for row in self.inventory if row["Status"] == "include"]
        for title in actual_titles:
            matches = [row for row in included if row["Canonical title"] == title]
            self.assertEqual(1, len(matches), title)

    def test_selected_publication_metadata_exactly_matches_inventory(self):
        self.assertTrue(self.publication_rows)
        self.assertTrue(all(len(row) == 6 for row in self.publication_rows))
        included = {
            row["Canonical title"]: row
            for row in self.inventory
            if row["Status"] == "include"
        }
        for title, authors, venue, year, link, publication_type in self.publication_rows:
            source = included[title]
            self.assertEqual(source["Display authors"], authors, title)
            self.assertEqual(source["Venue"], venue, title)
            self.assertEqual(source["Year"], year, title)
            self.assertEqual(source["Destination"], link, title)
            self.assertEqual(source["Type"], publication_type, title)

    def test_non_publication_facts_have_compact_provenance(self):
        fact_ids = set(re.findall(r"\[\^(F\d+)\]", self.content))
        self.assertGreaterEqual(len(fact_ids), 1)
        evidence_ids = {row[0] for row in self.evidence_rows}
        self.assertEqual(fact_ids, evidence_ids)
        for row in self.evidence_rows:
            self.assertEqual(4, len(row))
            self.assertRegex(row[0], r"^F\d+$")
            self.assertTrue(row[1] and row[2])
            self.assertRegex(row[3], r"^(index\.html|https://icisee\.sjtu\.edu\.cn/jiaoshiml/luguo\.html|https://guolusjtu\.github\.io/guoluhomepage/paper/GuoLu\.pdf)(?: \(.+\))?$")

    def test_content_has_no_placeholders_or_unsupported_claim_markers(self):
        forbidden = [
            "TODO", "TBD", "PLACEHOLDER", "grant no.", "grant number",
            "CNY", "RMB", "¥", "$", "corresponding author", "* Guo Lu",
            "†", "‡",
        ]
        lowered = self.content.lower()
        for token in forbidden:
            self.assertNotIn(token.lower(), lowered)


if __name__ == "__main__":
    unittest.main()
