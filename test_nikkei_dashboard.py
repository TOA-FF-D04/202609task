import tempfile
import unittest
from pathlib import Path

import pandas as pd

from nikkei_dashboard import build_prediction_series, create_dashboard


class NikkeiDashboardTest(unittest.TestCase):
    def test_create_dashboard_contains_interactive_controls(self) -> None:
        close = pd.Series(
            [38000.0, 38200.0, 38100.0],
            index=pd.date_range("2026-01-01", periods=3),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = create_dashboard(close, Path(directory) / "dashboard.html")
            html = path.read_text(encoding="utf-8")

        self.assertIn("日経平均ダッシュボード", html)
        self.assertIn("1か月", html)
        self.assertIn("hovertemplate", html)
        self.assertIn("rangeselector", html)
        self.assertIn("plotly", html.lower())

    def test_create_dashboard_can_show_predictions(self) -> None:
        close = pd.Series(
            [38000.0, 38200.0, 38100.0],
            index=pd.date_range("2026-01-01", periods=3),
        )
        predictions = pd.Series([38150.0], index=pd.DatetimeIndex(["2026-01-02"]))
        with tempfile.TemporaryDirectory() as directory:
            path = create_dashboard(close, Path(directory) / "dashboard.html", predictions)
            html = path.read_text(encoding="utf-8")

        self.assertIn("破線は1日・1週間・1か月先の予測", html)

    def test_prediction_series_includes_future_point(self) -> None:
        close = pd.Series(
            [100 * (1.001**index) for index in range(150)],
            index=pd.date_range("2025-01-01", periods=150, freq="B"),
        )

        predictions = build_prediction_series(close)

        self.assertEqual(set(predictions), {"1日予測", "1週間予測", "1か月予測"})
        for series in predictions.values():
            self.assertGreater(series.index[-1], close.index[-1])
            self.assertGreater(series.iloc[-1], 0)


if __name__ == "__main__":
    unittest.main()