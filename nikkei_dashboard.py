"""日経平均を見やすいインタラクティブな Web ページとして出力する。"""

from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
from plotly.offline import plot
import pandas as pd

from nikkei_bot import CHART_PATH, fetch_nikkei


DASHBOARD_PATH = Path("output/nikkei_dashboard.html")


def fetch_dashboard_data():
    """日足と5分足を結合し、期間ボタン用のデータを用意する。"""
    daily = fetch_nikkei(period="1y", interval="1d")
    intraday = fetch_nikkei(period="2d", interval="5m")
    return pd.concat([daily, intraday]).sort_index()


def create_dashboard(close, output_path: Path = DASHBOARD_PATH) -> Path:
    """価格データから期間切り替えとホバーに対応した HTML を作成する。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=close.index,
            y=close.values,
            mode="lines",
            name="日経平均",
            line={"color": "#d1495b", "width": 2},
            customdata=close.values,
            hovertemplate="日付: %{x|%Y-%m-%d}<br>終値: %{customdata:,.2f} 円<extra></extra>",
        )
    )
    figure.update_layout(
        title="日経平均株価（終値）",
        template="plotly_white",
        hovermode="x",
        xaxis={
            "title": "日付",
            "rangeselector": {
                "buttons": [
                    {"count": 1, "label": "1日", "step": "day", "stepmode": "backward"},
                    {"count": 1, "label": "1か月", "step": "month", "stepmode": "backward"},
                    {"count": 1, "label": "1年", "step": "year", "stepmode": "backward"},
                    {"step": "all", "label": "全期間"},
                ]
            },
            "rangeslider": {"visible": True},
        },
        yaxis={"title": "円", "tickformat": ",.0f"},
        margin={"l": 70, "r": 30, "t": 80, "b": 70},
    )
    html = plot(
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
  <title>日経平均ダッシュボード</title>
  <style>
    body {{ margin: 0; background: #f5f1eb; font-family: sans-serif; }}
    main {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
    h1 {{ color: #252422; font-size: 28px; }}
    .chart {{ background: #fff; padding: 12px; border-radius: 8px; }}
  </style>
</head>
<body><main><h1>日経平均ダッシュボード</h1>
<p>期間: 1日 / 1か月 / 1年 / 全期間。グラフにマウスを合わせると、その日の終値が表示されます。</p>
<div class="chart">{html}</div></main></body>
</html>"""
    output_path.write_text(page, encoding="utf-8")
    return output_path


def main() -> None:
    print("日経平均データを取得しています...")
    close = fetch_dashboard_data()
    path = create_dashboard(close)
    print(f"Web ページを保存しました: {path}")
    print("ブラウザでこのファイルを開くと、期間切り替えと価格ホバーを使えます。")


if __name__ == "__main__":
    main()