from pathlib import Path
import html
import re
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
TITLE = "Compressing 3D Gaussian Splatting via Cross-Representation Priors"
AUTHORS = "Yezheng Zhang, Huanxiong Liang, Chuqin Zhou, Guo Lu, Wenjun Zhang"
GRANT = "2026.9 Received an NSFC Young Scientists Fund-Type B grant (国家自然科学基金青年科学基金项目（B类）)."
CHINESE_BIO = "鲁国，上海交通大学电子工程系副教授，研究方向为视频编码与多媒体处理。"


class SeptemberUpdatesTests(unittest.TestCase):
    def test_short_chinese_identity_is_visible_once_in_about_me(self):
        homepage = (ROOT / "index.html").read_text(encoding="utf-8")
        about = homepage.split('id="about-me-heading"', 1)[1].split('<aside class="join-us-callout"', 1)[0]
        self.assertIn(f'<p lang="zh-CN">{CHINESE_BIO}</p>', about)
        self.assertEqual(1, homepage.count(CHINESE_BIO))

    def test_grant_is_latest_home_news_and_in_archive_feed(self):
        homepage = html.unescape((ROOT / "index.html").read_text(encoding="utf-8"))
        news = homepage.split('<section id="news"', 1)[1].split('</section>', 1)[0]
        items = re.findall(r'<li><p>(.*?)</p></li>', news)
        self.assertEqual(6, len(items))
        self.assertEqual(GRANT, items[0])
        archive = html.unescape((ROOT / "news" / "index.html").read_text(encoding="utf-8"))
        self.assertIn(f'<div id="2026-09-nsfc-grant">\n        <p>{GRANT}</p>', archive)
        feed = ET.parse(ROOT / "news" / "index.xml").getroot().find("channel")
        first = feed.findall("item")[0]
        self.assertEqual(GRANT, first.findtext("description"))
        self.assertTrue(first.findtext("guid").endswith("#2026-09-nsfc-grant"))

    def test_tip_paper_is_in_recent_and_full_publications_but_not_news(self):
        homepage = html.unescape((ROOT / "index.html").read_text(encoding="utf-8"))
        recent = homepage.split('<section id="publications"', 1)[1].split('</section>', 1)[0]
        self.assertIn(f"[TIP'26] {TITLE}", recent)
        self.assertIn("Yezheng Zhang, Huanxiong Liang, Chuqin Zhou, <u>Guo Lu</u>, Wenjun Zhang", recent)
        self.assertIn("IEEE Transactions on Image Processing, 2026.", recent)
        archive = html.unescape((ROOT / "publication" / "index.html").read_text(encoding="utf-8"))
        self.assertIn(f'data-title="{TITLE}" data-authors="{AUTHORS}" data-venue="IEEE TIP" data-year="2026" data-destination=""', archive)
        self.assertNotIn(TITLE, (ROOT / "news" / "index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
