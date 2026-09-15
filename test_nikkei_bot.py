import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pandas as pd

from nikkei_bot import create_chart, summarize_with_gemini


class NikkeiBotTest(unittest.TestCase):
    def test_create_chart_saves_png(self) -> None:
        close = pd.Series(
            [38000.0, 38200.0, 38100.0],
            index=pd.date_range("2026-01-01", periods=3),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = create_chart(close, Path(directory) / "chart.png")
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 0)

    def test_skips_gemini_without_api_key(self) -> None:
        close = pd.Series([38000.0, 38200.0])
        with mock.patch.dict("os.environ", {}, clear=True):
            result = summarize_with_gemini(close)
        self.assertIn("AI 解説はスキップ", result)


if __name__ == "__main__":
    unittest.main()