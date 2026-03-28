import shutil
import unittest
from pathlib import Path

from services.conversation_store import LocalConversationStore


class LocalStoreTests(unittest.TestCase):
    def test_preferences_behavior_and_memory_roundtrip(self):
        temp_dir = Path.cwd() / ".tmp_local_store_test"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()

        try:
            store = LocalConversationStore(str(temp_dir / "libra.json"))
            user_id = "user-123"

            store.save_preference(user_id, "favorite_color", "blue")
            store.update_behavior(user_id, "short_style", True)
            store.save_memory(user_id, "My favorite color is blue", "Nice, I will remember that.")
            store.save_memory(user_id, "Tell me a joke", "Here is one.")

            self.assertEqual(store.get_preferences(user_id)["favorite_color"], "blue")
            self.assertTrue(store.get_behavior(user_id)["short_style"])

            memory = store.get_memory(user_id, "favorite color", limit=1)
            self.assertEqual(memory[0][0], "My favorite color is blue")
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
