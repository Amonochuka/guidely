from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.documents import router as documents_router
from routes.search import router as search_router

app = FastAPI(
    title="Guidely API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(search_router)


@app.get("/")
def root():
    return {"message": "Welcome to Guidely API"}


@app.get("/health")
def health():
    return {"status": "healthy"}