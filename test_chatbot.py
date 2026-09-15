import unittest

from chatbot import SimpleAI


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


if __name__ == "__main__":
    unittest.main()