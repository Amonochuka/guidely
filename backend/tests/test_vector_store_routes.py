import unittest

import faiss
import numpy as np
from fastapi import FastAPI
from fastapi.testclient import TestClient

from models.chunk import Chunk
from routes import vector_store as vector_store_routes
from services import vector_store


class VectorStoreRoutesTests(unittest.TestCase):
    def setUp(self):
        self.original_index = vector_store.index
        self.original_chunks = vector_store.chunks

        vector_store.index = faiss.IndexFlatIP(vector_store.DIMENSION)
        vector_store.chunks = [
            Chunk(
                chunk_id=0,
                filename="guide.txt",
                chunk_index=0,
                text="Guide content",
            ),
        ]

        vectors = np.zeros((1, vector_store.DIMENSION), dtype="float32")
        vectors[0, 0] = 1.0
        vector_store.index.add(vectors)

        app = FastAPI()
        app.include_router(vector_store_routes.router)
        self.client = TestClient(app)

    def tearDown(self):
        vector_store.index = self.original_index
        vector_store.chunks = self.original_chunks

    def test_returns_stored_embeddings(self):
        response = self.client.get("/vector-store/")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["total_vectors"], 1)
        self.assertEqual(body["dimension"], vector_store.DIMENSION)
        self.assertEqual(body["embeddings"][0]["filename"], "guide.txt")
        self.assertEqual(body["embeddings"][0]["embedding"][0], 1.0)

    def test_filters_embeddings_by_filename(self):
        response = self.client.get("/vector-store/", params={"filename": "other.txt"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["embeddings"], [])

    def test_persists_vectors_to_disk(self):
        saved = []

        original_save_index = vector_store.save_index
        original_save_chunks = vector_store.save_chunks
        vector_store.save_index = lambda: saved.append("index")
        vector_store.save_chunks = lambda: saved.append("chunks")

        try:
            response = self.client.post("/vector-store/persist")
        finally:
            vector_store.save_index = original_save_index
            vector_store.save_chunks = original_save_chunks

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(saved, ["index", "chunks"])
        self.assertEqual(body["vectors_in_index"], 1)
        self.assertEqual(body["chunks_stored"], 1)


if __name__ == "__main__":
    unittest.main()
