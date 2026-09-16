import tempfile
import unittest
from pathlib import Path

import pandas as pd

from nikkei_realtime_dashboard import create_realtime_dashboard


class NikkeiRealtimeDashboardTest(unittest.TestCase):
    def test_creates_realtime_page_with_latest_value(self) -> None:
        close = pd.Series(
            [38000.0, 38100.0, 38050.0],
            index=pd.date_range("2026-01-01 09:00", periods=3, freq="5min"),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = create_realtime_dashboard(close, Path(directory) / "realtime.html")
            html = path.read_text(encoding="utf-8")

        self.assertIn("日経平均 当日値動き", html)
        self.assertIn('http-equiv="refresh" content="300"', html)
        self.assertIn("5分足", html)
        self.assertIn("plotly", html.lower())


if __name__ == "__main__":
    unittest.main()