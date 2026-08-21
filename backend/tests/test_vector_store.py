import unittest

import faiss
import numpy as np

from models.chunk import Chunk
from services import vector_store


class VectorStoreTests(unittest.TestCase):
    def setUp(self):
        self.original_index = vector_store.index
        self.original_chunks = vector_store.chunks
        vector_store.index = faiss.IndexFlatIP(vector_store.DIMENSION)
        vector_store.chunks = [
            Chunk(
                chunk_id=0,
                filename="relevant.txt",
                chunk_index=0,
                text="Relevant content",
            ),
            Chunk(
                chunk_id=1,
                filename="irrelevant.txt",
                chunk_index=1,
                text="Irrelevant content",
            ),
        ]

        vectors = np.zeros((2, vector_store.DIMENSION), dtype="float32")
        vectors[0, 0] = 1.0
        vectors[1, 1] = 1.0
        vector_store.index.add(vectors)

    def tearDown(self):
        vector_store.index = self.original_index
        vector_store.chunks = self.original_chunks

    def test_returns_only_chunks_above_minimum_similarity(self):
        query = np.zeros(vector_store.DIMENSION, dtype="float32")
        query[0] = 1.0

        results = vector_store.search(query, min_similarity=0.35)

        self.assertEqual([chunk.filename for chunk in results], ["relevant.txt"])

    def test_returns_no_results_when_index_is_empty(self):
        vector_store.index = faiss.IndexFlatIP(vector_store.DIMENSION)

        self.assertEqual(vector_store.search(np.zeros(vector_store.DIMENSION)), [])

    def test_returns_ranked_results_without_a_similarity_cutoff(self):
        query = np.zeros(vector_store.DIMENSION, dtype="float32")
        query[0] = 1.0

        results = vector_store.search_ranked(query)

        self.assertEqual(results[0][0].filename, "relevant.txt")
        self.assertEqual(results[0][1], 1.0)
        self.assertEqual(results[1][0].filename, "irrelevant.txt")
