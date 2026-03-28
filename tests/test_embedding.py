import unittest

from utils.embedding import VECTOR_SIZE, cosine_similarity, get_embedding, tokenize


class EmbeddingTests(unittest.TestCase):
    def test_tokenize_lowercases_words(self):
        self.assertEqual(tokenize("Hello, Libra!"), ["hello", "libra"])

    def test_embedding_has_stable_size(self):
        embedding = get_embedding("memory systems should stay deterministic")
        self.assertEqual(len(embedding), VECTOR_SIZE)

    def test_cosine_similarity_rewards_related_text(self):
        left = get_embedding("favorite color blue")
        right = get_embedding("my favorite color is blue")
        other = get_embedding("dark joke api")

        self.assertGreater(cosine_similarity(left, right), cosine_similarity(left, other))


if __name__ == "__main__":
    unittest.main()
