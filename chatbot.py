"""依存ライブラリなしで動く、学習用の小さなチャットボット。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
import random
import re


@dataclass
class SimpleAI:
    """入力文の特徴から返答を選ぶ簡単な AI。"""

    user_name: str | None = None
    random_source: random.Random = field(default_factory=random.Random)

    def respond(self, message: str) -> str:
        text = message.strip()
        if not text:
            return "何か話しかけてください。"

        name_match = re.search(r"(?:私の名前は|ぼくの名前は|僕の名前は)\s*([^。！!？?]+)", text)
        if name_match:
            self.user_name = name_match.group(1).strip()
            if self.user_name.endswith("です"):
                self.user_name = self.user_name[:-2].strip()
            return f"覚えました。{self.user_name}さんですね。"

        if self._matches(text, "さようなら", "またね", "終了", "ばいばい"):
            return "また話しましょう。"
        if self._matches(text, "こんにちは", "こんばんは", "おはよう"):
            greeting = self.random_source.choice(("こんにちは", "どうもこんにちは", "お話しできてうれしいです"))
            if self.user_name:
                return f"{greeting}、{self.user_name}さん。"
            return f"{greeting}。"
        if self._matches(text, "名前を覚えてる", "私の名前", "ぼくの名前", "僕の名前"):
            if self.user_name:
                return f"あなたの名前は{self.user_name}さんです。"
            return "まだ名前を聞いていません。"
        if self._matches(text, "何時", "時間"):
            return f"今は {datetime.now():%H:%M} です。"
        if self._matches(text, "ありがとう", "感謝"):
            return "どういたしまして。"
        if self._matches(text, "できること", "何ができる", "ヘルプ"):
            return "あいさつ、名前を覚えること、時刻の確認ができます。"

        return self._fallback(text)

    def _matches(self, text: str, *keywords: str) -> bool:
        return any(keyword in text for keyword in keywords)

    def _fallback(self, text: str) -> str:
        known_topics = ("天気", "勉強", "仕事", "趣味")
        closest_topic = max(
            known_topics,
            key=lambda topic: SequenceMatcher(None, text, topic).ratio(),
        )
        if SequenceMatcher(None, text, closest_topic).ratio() > 0.45:
            return f"{closest_topic}についてですね。もう少し詳しく教えてください。"
        return self.random_source.choice(
            (
                "なるほど。もう少し詳しく聞かせてください。",
                "その話は面白そうですね。",
                "まだ勉強中ですが、考えてみます。",
            )
        )


def main() -> None:
    bot = SimpleAI()
    print("SimpleAI を起動しました。終了するには「終了」と入力してください。")
    while True:
        try:
            message = input("あなた > ")
        except (EOFError, KeyboardInterrupt):
            print("\nまた話しましょう。")
            break

        response = bot.respond(message)
        print(f"AI   > {response}")
        if message.strip() in {"終了", "さようなら", "またね", "ばいばい"}:
            break


if __name__ == "__main__":
    main()