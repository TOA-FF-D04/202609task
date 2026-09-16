"""日経平均の期間別予測だけを表示する Web ページを生成する。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot

from nikkei_bot import fetch_nikkei
from nikkei_dashboard import build_prediction_series


PREDICTION_DASHBOARD_PATH = Path("output/prediction.html")


def create_prediction_dashboard(
    predictions: dict[str, pd.Series],
    output_path: Path = PREDICTION_DASHBOARD_PATH,
) -> Path:
    """期間別予測系列から予測専用 HTML を作成する。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure = go.Figure()
    colors = ("#277da1", "#7b2cbf", "#f77f00")
    for (label, series), color in zip(predictions.items(), colors):
        figure.add_trace(
            go.Scatter(
                x=series.index,
                y=series.values,
                mode="lines+markers",
                name=label,
                line={"color": color, "width": 2, "dash": "dash"},
                customdata=series.values,
                hovertemplate="予測日: %{x|%Y-%m-%d}<br>予測値: %{customdata:,.2f} 円<extra></extra>",
            )
        )
    figure.update_layout(
        title="日経平均 期間別予測",
        template="plotly_white",
        hovermode="x unified",
        xaxis={
            "title": "予測日",
            "rangeselector": {
                "buttons": [
                    {"count": 1, "label": "1か月", "step": "month", "stepmode": "backward"},
                    {"count": 1, "label": "1年", "step": "year", "stepmode": "backward"},
                    {"step": "all", "label": "全期間"},
                ]
            },
            "rangeslider": {"visible": True},
        },
        yaxis={"title": "予測値（円）", "tickformat": ",.0f"},
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
  <title>日経平均 期間別予測</title>
  <style>
    body {{ margin: 0; background: #eef4f7; font-family: sans-serif; }}
    main {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
    h1 {{ color: #17324d; font-size: 28px; }}
    .chart {{ background: #fff; padding: 12px; border-radius: 8px; }}
    .note {{ color: #40566b; }}
  </style>
</head>
<body><main><h1>日経平均 期間別予測</h1>
<p class="note">このページは実績グラフとは別の予測専用ページです。破線は過去の予測推移、各線の右端は最新時点からの予測です。</p>
<div class="chart">{chart}</div></main></body>
</html>"""
    output_path.write_text(page, encoding="utf-8")
    return output_path


def main() -> None:
    print("日経平均の予測データを計算しています...")
    daily = fetch_nikkei(period="5y", interval="1d")
    predictions = build_prediction_series(daily)
    path = create_prediction_dashboard(predictions)
    print(f"予測専用ページを保存しました: {path}")


if __name__ == "__main__":
    main()