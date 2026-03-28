import unittest

from utils.emotion import detect_emotion, detect_intensity


class EmotionTests(unittest.TestCase):
    def test_detects_sadness(self):
        self.assertEqual(detect_emotion("I feel sad and lonely today"), "sad")

    def test_detects_confusion(self):
        self.assertEqual(detect_emotion("I am confused about why this broke"), "confused")

    def test_detects_high_intensity(self):
        self.assertEqual(detect_intensity("I am very frustrated!!"), "high")

    def test_detects_low_intensity(self):
        self.assertEqual(detect_intensity("I am a bit tired"), "low")


if __name__ == "__main__":
    unittest.main()
