# Guidely

An internal knowledge assistant that enables users to upload documents, index them using vector embeddings, and ask natural language questions. Guidely combines semantic search with Retrieval-Augmented Generation (RAG) to provide concise answers together with the document sources used to generate them.

---

## Overview

Guidely is a Retrieval-Augmented Generation (RAG) application built with **FastAPI**, **React (Vite)**, **FAISS**, **Sentence Transformers**, and **Google Gemini**.

Instead of searching documents using keyword matching, Guidely converts documents into vector embeddings and retrieves the most semantically relevant chunks before generating an answer with an LLM.

The application follows the workflow:

```
Upload Documents
        ↓
Extract Text
        ↓
Chunk Documents
        ↓
Generate Embeddings
        ↓
Store in FAISS
        ↓
Ask Question
        ↓
Retrieve Top-k Chunks
        ↓
Generate AI Answer
        ↓
Return Answer + Sources
```

---

# Features

## Backend

- Upload TXT, PDF and DOCX documents
- Automatic document parsing
- Text chunking
- Sentence Transformer embeddings
- Persistent FAISS vector store
- Semantic similarity search
- AI answer generation using Gemini
- Source attribution
- Duplicate document detection using hashing
- Embedding cache for unchanged documents
- Logging
- Health endpoint
- Metrics endpoint

## Frontend *(In Progress)*

- Search page
- Admin upload page
- Source references
- Friendly error handling

---

# Tech Stack

## Backend

- FastAPI
- FAISS
- Sentence Transformers (all-MiniLM-L6-v2)
- Google Gemini API
- NumPy
- Pickle

## Frontend

- React
- Vite

---

# Project Structure

```text
guidely/
│
├── backend/
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── data/
│   └── main.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── README.md
└── .env
```

---

# System Architecture

```text
                +-------------------+
                |    React Client   |
                +---------+---------+
                          |
                          |
                    HTTP Requests
                          |
                          v
                +-------------------+
                |      FastAPI      |
                +---------+---------+
                          |
         +----------------+----------------+
         |                                 |
         v                                 v
 Document Processing                 Search Pipeline
         |                                 |
 Extract Text                     Embed Question
         |                                 |
 Chunk Text                       FAISS Search
         |                                 |
 Generate Embeddings              Retrieve Top-k Chunks
         |                                 |
 Store in FAISS                   Gemini
         |                                 |
         +---------------+-----------------+
                         |
                    JSON Response
```

---

# RAG Pipeline

## 1. Upload

Users upload supported documents.

Supported formats:

- TXT
- PDF
- DOCX

---

## 2. Document Processing

The uploaded document is:

- Parsed
- Converted to raw text
- Split into fixed-size chunks

---

## 3. Embedding Generation

Each chunk is converted into a vector embedding using Sentence Transformers.

---

## 4. Vector Storage

Embeddings are stored in a persistent FAISS vector index.

Chunk metadata is stored alongside each embedding.

---

## 5. Question Answering

When a question is submitted:

1. Generate an embedding for the question.
2. Retrieve the most relevant chunks using FAISS.
3. Build a context from the retrieved chunks.
4. Send the context and question to Gemini.
5. Return:

- Generated answer
- Source documents
- Chunk references

---

# API Endpoints

## Documents

### Upload Document

```
POST /documents/upload
```

Uploads and indexes a document.

---

## Search

### Ask Question

```
POST /search
```

Returns:

- answer
- referenced sources

---

## System

### Health

```
GET /system/health
```

Returns application health.

---

### Metrics

```
GET /system/metrics
```

Returns runtime metrics including:

- queries served
- cache hits
- median latency

---

# Dataset

The project uses sample internal knowledge documents including:

- Policies
- FAQs
- Guides
- Manuals
- Company documentation

At least five sample documents are included in:

```text
backend/data/sample-docs/
```

---

# Installation

## Clone Repository

```bash
git clone <repository-url>
cd guidely
```

---

## Backend

Create a virtual environment.

```bash
python -m venv venv
```

Activate it.

Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file.

```text
GEMINI_API_KEY=your_api_key
```

---

## Run Backend

```bash
uvicorn main:app --reload
```

Backend runs on

```
http://localhost:8000
```

---

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on

```
http://localhost:5173
```

---

# Error Handling

The API handles:

- Empty questions
- Unsupported file types
- Corrupted documents
- Missing AI configuration
- No relevant search results
- AI service failures

---

# Logging

The backend logs:

- Uploaded documents
- Cache hits
- Search requests
- Query latency
- AI failures
- Processing errors

---

# Testing & Metrics

> **To be completed after frontend testing.**

| Metric | Result | Status |
|---------|--------|--------|
| Retrieval@3 | TBD | ⏳ |
| Answer Reference Coverage | TBD | ⏳ |
| Source Precision | TBD | ⏳ |
| Median Latency | TBD | ⏳ |
| Embedding Cache Effectiveness | TBD | ⏳ |
| Failure Handling | TBD | ⏳ |

---

# Future Improvements

- Query-aware snippets
- Hybrid keyword + semantic search
- Conversation history
- Authentication
- Document tagging
- CSV query export
- Streaming responses

---

# Author

**Amon Mandela Ochuka**

Zone01 Kisumu