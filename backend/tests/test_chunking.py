import unittest

from services.chunking import chunk_text


class ChunkTextTests(unittest.TestCase):
    def test_splits_text_with_overlap(self):
        chunks = chunk_text(
            "abcdefghij",
            "guide.txt",
            chunk_size=6,
            overlap=2,
        )

        self.assertEqual([chunk.text for chunk in chunks], ["abcdef", "efghij"])
        self.assertEqual([chunk.chunk_index for chunk in chunks], [0, 1])
        self.assertTrue(all(chunk.filename == "guide.txt" for chunk in chunks))

    def test_ignores_blank_text(self):
        self.assertEqual(chunk_text("   ", "blank.txt"), [])
