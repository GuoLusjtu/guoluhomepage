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
        expected = "Summary: " + "; ".join(
            f"{key}={counts[key]}" for key in ("include", "exclude", "needs-review")
        )
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
