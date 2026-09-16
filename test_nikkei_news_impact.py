import tempfile
import unittest
from pathlib import Path

from nikkei_news_impact import NewsItem, classify_impact, create_news_page


class NikkeiNewsImpactTest(unittest.TestCase):
    def test_classifies_headline_direction(self) -> None:
        self.assertEqual(classify_impact("日経平均が続伸、円安で買い優勢")[0], "上昇要因")
        self.assertEqual(classify_impact("日経平均が急落、円高懸念")[0], "下落要因")
        self.assertEqual(classify_impact("日経平均は小動き")[0], "中立")

    def test_creates_news_page(self) -> None:
        items = [NewsItem("日経平均が反発", "https://example.com", "今日", "Example", "上昇要因", 25)]
        with tempfile.TemporaryDirectory() as directory:
            path = create_news_page(items, Path(directory) / "news-impact.html")
            page = path.read_text(encoding="utf-8")
        self.assertIn("日経平均ニュース影響分析", page)
        self.assertIn("上昇要因", page)
        self.assertIn('content="300"', page)


if __name__ == "__main__":
    unittest.main()