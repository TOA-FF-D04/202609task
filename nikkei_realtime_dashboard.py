"""日経平均の当日5分足を表示する準リアルタイム Web ページ。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import plotly.graph_objects as go
from plotly.offline import plot

from nikkei_bot import fetch_nikkei


REALTIME_PATH = Path("output/realtime.html")


def create_realtime_dashboard(close, output_path: Path = REALTIME_PATH) -> Path:
    """当日の5分足からリアルタイム表示用 HTML を作る。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    latest = float(close.iloc[-1])
    previous = float(close.iloc[-2]) if len(close) > 1 else latest
    figure = go.Figure(
        go.Scatter(
            x=close.index,
            y=close.values,
            mode="lines+markers",
            name="日経平均",
            line={"color": "#d1495b", "width": 2},
            customdata=close.values,
            hovertemplate="時刻: %{x|%Y-%m-%d %H:%M}<br>価格: %{customdata:,.2f} 円<extra></extra>",
        )
    )
    figure.update_layout(
        title="日経平均 当日値動き",
        template="plotly_white",
        hovermode="x",
        xaxis={"title": "時刻", "rangeslider": {"visible": True}},
        yaxis={"title": "円", "tickformat": ",.0f"},
        margin={"l": 80, "r": 30, "t": 80, "b": 70},
    )
    chart = plot(
        figure,
        output_type="div",
        include_plotlyjs=True,
        config={"responsive": True, "displaylogo": False},
    )
    page = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="300">
  <title>日経平均 当日値動き</title>
  <style>
    body {{ margin: 0; background: #fff8f0; font-family: sans-serif; }}
    main {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
    h1 {{ color: #252422; font-size: 28px; }}
    .summary {{ display: flex; gap: 32px; flex-wrap: wrap; margin: 20px 0; }}
    .value {{ font-size: 28px; font-weight: bold; color: #d1495b; }}
    .chart {{ background: #fff; padding: 12px; border-radius: 8px; }}
    .note {{ color: #5c554d; }}
  </style>
</head>
<body><main><h1>日経平均 当日値動き</h1>
<p class="note">Yahoo Finance の5分足を使った準リアルタイム表示です。ページは約5分ごとに更新されます。</p>
<div class="summary"><div>最新値<br><span class="value">{latest:,.2f} 円</span></div>
<div>前回比<br><span class="value">{latest - previous:+,.2f} 円</span></div>
<div>取得時刻<br><span>{datetime.now():%Y-%m-%d %H:%M}</span></div></div>
<div class="chart">{chart}</div></main></body>
</html>"""
    output_path.write_text(page, encoding="utf-8")
    return output_path


def main() -> None:
    print("日経平均の当日データを取得しています...")
    close = fetch_nikkei(period="1d", interval="5m")
    path = create_realtime_dashboard(close)
    print(f"準リアルタイムページを保存しました: {path}")


if __name__ == "__main__":
    main()