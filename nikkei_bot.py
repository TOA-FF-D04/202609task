"""日経平均株価を取得し、グラフと Gemini による要約を作成するボット。"""

from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import yfinance as yf

from google import genai


TICKER = "^N225"
DEFAULT_PERIOD = "1y"
CHART_PATH = Path("output/nikkei225.png")


def fetch_nikkei(period: str = DEFAULT_PERIOD, interval: str = "1d"):
    """Yahoo Finance から日経平均の終値データを取得する。"""
    data = yf.download(
        TICKER,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
    )
    if data.empty or "Close" not in data:
        raise RuntimeError("日経平均のデータを取得できませんでした。時間を置いて再試行してください。")

    close = data["Close"]
    if hasattr(close, "columns"):
        close = close[TICKER]
    close = close.dropna()
    if close.empty:
        raise RuntimeError("日経平均の終値データが空です。")
    if getattr(close.index, "tz", None) is not None:
        close.index = close.index.tz_localize(None)
    return close


def create_chart(close, output_path: Path = CHART_PATH) -> Path:
    """終値データから日経平均の折れ線グラフを保存する。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    japanese_fonts = ("Yu Gothic", "Meiryo", "Noto Sans CJK JP")
    for font_name in japanese_fonts:
        try:
            font_manager.findfont(font_name, fallback_to_default=False)
        except ValueError:
            continue
        else:
            plt.rcParams["font.family"] = font_name
            break
    figure, axis = plt.subplots(figsize=(12, 6))
    axis.plot(close.index, close.values, color="#d1495b", linewidth=2)
    axis.set_title("日経平均株価（終値）")
    axis.set_xlabel("日付")
    axis.set_ylabel("円")
    axis.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)
    return output_path


def summarize_with_gemini(close) -> str:
    """日経平均の推移を Gemini に短く要約させる。"""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return "GEMINI_API_KEY が未設定のため、AI 解説はスキップしました。"

    first = float(close.iloc[0])
    latest = float(close.iloc[-1])
    change = latest - first
    change_rate = change / first * 100
    prompt = (
        "以下は日経平均株価の1年間の終値データの要約です。"
        "投資助言ではなく、観測できる値だけを使って日本語で3文以内に説明してください。\n"
        f"開始値: {first:.2f}円\n最新値: {latest:.2f}円\n"
        f"変化額: {change:+.2f}円\n変化率: {change_rate:+.2f}%"
    )
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
    return response.text or "Gemini から解説を取得できませんでした。"


def main() -> None:
    print("日経平均データを取得しています...")
    close = fetch_nikkei()
    chart_path = create_chart(close)
    latest = float(close.iloc[-1])
    previous = float(close.iloc[-2]) if len(close) > 1 else latest
    print(f"基準日: {close.index[-1]:%Y-%m-%d}")
    print(f"最新終値: {latest:,.2f}円 ({latest - previous:+,.2f}円)")
    print(f"グラフを保存しました: {chart_path}")
    print(f"取得日時: {datetime.now():%Y-%m-%d %H:%M}")
    print("\nGemini による要約:")
    print(summarize_with_gemini(close))


if __name__ == "__main__":
    main()