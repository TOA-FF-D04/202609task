import tempfile
import unittest
from pathlib import Path

import pandas as pd

from nikkei_prediction_dashboard import create_prediction_dashboard


class NikkeiPredictionDashboardTest(unittest.TestCase):
    def test_creates_separate_prediction_page(self) -> None:
        predictions = {
            "1日予測": pd.Series([38000.0, 38100.0], index=pd.date_range("2026-01-01", periods=2)),
            "1週間予測": pd.Series([37900.0, 38200.0], index=pd.date_range("2026-01-01", periods=2)),
            "1か月予測": pd.Series([37500.0, 38500.0], index=pd.date_range("2026-01-01", periods=2)),
        }
        with tempfile.TemporaryDirectory() as directory:
            path = create_prediction_dashboard(predictions, Path(directory) / "prediction.html")
            html = path.read_text(encoding="utf-8")

        self.assertEqual(path.name, "prediction.html")
        self.assertIn("日経平均 期間別予測", html)
        self.assertIn("実績グラフとは別の予測専用ページ", html)
        self.assertIn("plotly", html.lower())


if __name__ == "__main__":
    unittest.main()