"""ローカル fallback と Gemini API に対応した学習用チャットボット。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
import random
import re
import os

from google import genai


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


class GeminiChatbot:
    """Gemini API に会話履歴を渡して自然な返答を生成するチャットボット。"""

    def __init__(
        self,
        model: str = "gemini-3.6-flash",
        system_prompt: str = "あなたは親切で簡潔な日本語アシスタントです。",
        client: object | None = None,
        api_key: str | None = None,
    ) -> None:
        self.model = model
        self.system_prompt = system_prompt
        normalized_api_key = (api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "")).strip()
        self.client = client or genai.Client(api_key=normalized_api_key)
        self.chat = self.client.chats.create(
            model=self.model,
            config={"system_instruction": self.system_prompt},
        )

    def respond(self, message: str) -> str:
        text = message.strip()
        if not text:
            return "何か話しかけてください。"

        try:
            response = self.chat.send_message(message=text)
        except Exception as error:
            if "quota" in str(error).lower() or "resource exhausted" in str(error).lower():
                return "Gemini API の利用上限に達しました。時間を置くか、Google AI Studio の利用状況を確認してください。"
            raise

        return response.text or "すみません、うまく返答できませんでした。"


def create_bot() -> SimpleAI | GeminiChatbot:
    """Gemini API キーがあれば高性能版、なければローカル版を返す。"""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if api_key:
        return GeminiChatbot(api_key=api_key)
    return SimpleAI()


def main() -> None:
    bot = create_bot()
    mode = "Gemini API" if isinstance(bot, GeminiChatbot) else "ローカル fallback"
    print(f"SimpleAI ({mode}) を起動しました。終了するには「終了」と入力してください。")
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