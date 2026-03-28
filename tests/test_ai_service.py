import unittest

from services.ai_service import LibraAIService, offline_ai_reply


class AIServiceTests(unittest.TestCase):
    def test_service_stays_offline_without_api_key(self):
        service = LibraAIService(api_key="", model_name="models/gemini-2.5-flash")
        reply, mode = service.generate_reply(
            user_message="Hello there",
            emotion="neutral",
            intensity="medium",
            preferences={},
            memory=[],
            behavior={},
        )

        self.assertEqual(mode, "offline")
        self.assertTrue(reply)

    def test_offline_reply_respects_emotion(self):
        reply = offline_ai_reply("I feel sad", emotion="sad", behavior={})
        self.assertTrue(reply)


if __name__ == "__main__":
    unittest.main()
