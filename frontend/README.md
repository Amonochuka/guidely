# Guidely Frontend

React + Vite client for the Guidely knowledge assistant.

## Pages

- `/` — Search page: ask a question, view the generated answer and its sources
- `/admin` — Admin page: upload documents, trigger re-indexing by re-uploading a changed file under the same filename, and review indexed documents

## Run

```bash
npm install
npm run dev
```

The app runs on http://localhost:5173 and expects the backend on http://127.0.0.1:8000.
Override the API location with `VITE_API_BASE_URL` in `.env` if needed.
