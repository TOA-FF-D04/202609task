import tempfile
import unittest
from pathlib import Path

import pandas as pd

from nikkei_dashboard import create_dashboard


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


if __name__ == "__main__":
    unittest.main()