import unittest
from unittest import mock

from chatbot import GeminiChatbot, SimpleAI, create_bot


class FakeChat:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.received_messages: list[str] = []

    def send_message(self, *, message: str) -> object:
        if self.error:
            raise self.error
        self.received_messages.append(message)
        return type("FakeResponse", (), {"text": "テスト回答"})()


class FakeClient:
    def __init__(self, error: Exception | None = None) -> None:
        self.chat = FakeChat(error)

    def chats(self) -> object:
        return self.chat


class FakeChats:
    def __init__(self, chat: FakeChat) -> None:
        self.chat = chat

    def create(self, *, model: str, config: object) -> FakeChat:
        return self.chat


class FakeGeminiClient:
    def __init__(self, error: Exception | None = None) -> None:
        self.chat = FakeChat(error)
        self.chats = FakeChats(self.chat)


class SimpleAITest(unittest.TestCase):
    def test_remembers_name(self) -> None:
        bot = SimpleAI()

        self.assertEqual(bot.respond("私の名前はさくらです"), "覚えました。さくらさんですね。")
        self.assertEqual(bot.respond("名前を覚えてる？"), "あなたの名前はさくらさんです。")

    def test_greeting_uses_name(self) -> None:
        bot = SimpleAI(user_name="太郎")

        self.assertIn("太郎さん", bot.respond("こんにちは"))

    def test_empty_message(self) -> None:
        self.assertEqual(SimpleAI().respond("  "), "何か話しかけてください。")

    def test_gemini_chatbot_keeps_conversation_history(self) -> None:
        client = FakeGeminiClient()
        bot = GeminiChatbot(client=client)  # type: ignore[arg-type]

        self.assertEqual(bot.respond("こんにちは"), "テスト回答")
        bot.respond("昨日の話を覚えていますか")

        self.assertEqual(client.chat.received_messages, ["こんにちは", "昨日の話を覚えていますか"])

    def test_uses_local_bot_without_api_key(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            self.assertIsInstance(create_bot(), SimpleAI)

    def test_uses_local_bot_for_whitespace_only_api_key(self) -> None:
        with mock.patch.dict("os.environ", {"GEMINI_API_KEY": " "}, clear=True):
            self.assertIsInstance(create_bot(), SimpleAI)

    def test_handles_gemini_quota_error(self) -> None:
        bot = GeminiChatbot(client=FakeGeminiClient(error=RuntimeError("RESOURCE_EXHAUSTED: quota")))  # type: ignore[arg-type]

        self.assertIn("利用上限", bot.respond("こんにちは"))


if __name__ == "__main__":
    unittest.main()