import tempfile
import unittest
from pathlib import Path
from unittest import mock

from nikkei_news_impact import NewsItem, classify_impact, create_news_page, summarize_with_gemini


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

    def test_gemini_failure_does_not_stop_news_page(self) -> None:
        items = [NewsItem("日経平均が反発", "https://example.com", "今日", "Example", "上昇要因", 25)]
        with mock.patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=True):
            with mock.patch("nikkei_news_impact.genai.Client", side_effect=RuntimeError("quota")):
                result = summarize_with_gemini(items)

        self.assertIn("キーワード分析は表示しています", result)


if __name__ == "__main__":
    unittest.main()