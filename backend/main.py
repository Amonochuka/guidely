from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Guidely API",
    version="1.0.0",
    description="Internal Knowledge Assistant API"
)

# Allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to Guidely API"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }