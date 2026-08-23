from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.documents import router as documents_router
from routes.search import router as search_router
from routes.system import router as system_router
from routes.metrics import router as metrics_router
from routes.vector_store import router as vector_store_router
from services.settings import CORS_ORIGINS

app = FastAPI(
    title="Guidely API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(search_router)
app.include_router(system_router)
app.include_router(metrics_router)
app.include_router(vector_store_router)


@app.get("/")
def root():
    return {"message": "Welcome to Guidely API"}


@app.get("/health")
def health():
    return {"status": "healthy"}
