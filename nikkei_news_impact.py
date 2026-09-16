"""日経平均関連ニュースを集め、直近の影響方向を推測する学習用モデル。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import html
import os
from pathlib import Path
from urllib.parse import quote

import feedparser
from google import genai


NEWS_PAGE_PATH = Path("output/news-impact.html")
RSS_URL = "https://news.google.com/rss/search?q=" + quote("日経平均 OR 日本株") + "&hl=ja&gl=JP&ceid=JP:ja"


@dataclass(frozen=True)
class NewsItem:
    title: str
    link: str
    published: str
    source: str
    impact: str
    score: int


POSITIVE_WORDS = ("上昇", "反発", "続伸", "最高値", "買い", "好決算", "利下げ", "円安", "改善")
NEGATIVE_WORDS = ("下落", "反落", "続落", "急落", "売り", "低迷", "利上げ", "円高", "悪化", "懸念")


def classify_impact(title: str) -> tuple[str, int]:
    """見出しのキーワードから影響方向と簡易スコアを返す。"""
    positive = sum(title.count(word) for word in POSITIVE_WORDS)
    negative = sum(title.count(word) for word in NEGATIVE_WORDS)
    score = max(-100, min(100, (positive - negative) * 25))
    if score > 0:
        return "上昇要因", score
    if score < 0:
        return "下落要因", score
    return "中立", 0


def fetch_news(limit: int = 20) -> list[NewsItem]:
    """Google ニュース RSS から日経平均関連ニュースを取得する。"""
    feed = feedparser.parse(RSS_URL)
    items: list[NewsItem] = []
    for entry in feed.entries[:limit]:
        title = html.unescape(getattr(entry, "title", "")).strip()
        impact, score = classify_impact(title)
        source = getattr(getattr(entry, "source", None), "title", "Google News")
        items.append(
            NewsItem(
                title=title,
                link=getattr(entry, "link", ""),
                published=getattr(entry, "published", "不明"),
                source=source,
                impact=impact,
                score=score,
            )
        )
    if not items:
        raise RuntimeError("ニュースを取得できませんでした。時間を置いて再試行してください。")
    return items


def summarize_with_gemini(items: list[NewsItem]) -> str:
    """ニュース一覧を Gemini に短く要約させる。"""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return "GEMINI_API_KEY が未設定のため、キーワード分析のみ表示しています。"
    titles = "\n".join(f"- {item.title}" for item in items[:10])
    prompt = (
        "以下の日経平均関連ニュースを日本語で3文以内に要約してください。"
        "ニュースから推測できる影響方向だけを述べ、投資助言や断定は避けてください。\n" + titles
    )
    response = genai.Client(api_key=api_key).models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    return response.text or "要約を取得できませんでした。"


def create_news_page(items: list[NewsItem], output_path: Path = NEWS_PAGE_PATH) -> Path:
    """ニュース一覧と影響度を HTML として保存する。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    average_score = sum(item.score for item in items) / len(items)
    cards = "".join(
        f'<article class="{item.impact}"><strong>{item.impact} ({item.score:+d})</strong>'
        f'<a href="{html.escape(item.link)}" target="_blank">{html.escape(item.title)}</a>'
        f'<small>{html.escape(item.source)} / {html.escape(item.published)}</small></article>'
        for item in items
    )
    page = f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta http-equiv="refresh" content="300">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>日経平均ニュース影響分析</title>
<style>
body {{ margin:0; background:#f3f6f8; color:#18252f; font-family:sans-serif; }}
main {{ max-width:1000px; margin:auto; padding:24px; }}
h1 {{ color:#17324d; }} .score {{ font-size:32px; font-weight:bold; }}
article {{ display:grid; gap:8px; background:white; margin:12px 0; padding:16px; border-left:6px solid #8a9aa5; border-radius:6px; }}
article.上昇要因 {{ border-color:#168aad; }} article.下落要因 {{ border-color:#d1495b; }}
a {{ color:#145da0; font-size:18px; text-decoration:none; }} small {{ color:#667781; }}
</style></head><body><main><h1>日経平均ニュース影響分析</h1>
<p>Google ニュース RSS を約5分ごとに取得し、見出しのキーワードから影響方向を推測しています。</p>
<p>直近ニュース平均影響スコア: <span class="score">{average_score:+.1f}</span></p>
<p>取得時刻: {datetime.now():%Y-%m-%d %H:%M}</p><section>{cards}</section>
<h2>Gemini による補助要約</h2><p>{html.escape(summarize_with_gemini(items))}</p>
</main></body></html>"""
    output_path.write_text(page, encoding="utf-8")
    return output_path


def main() -> None:
    items = fetch_news()
    path = create_news_page(items)
    print(f"ニュース影響分析ページを保存しました: {path}")


if __name__ == "__main__":
    main()