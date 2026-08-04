from fastapi import APIRouter
from services.metrics import get_metrics

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/health")
def health():
    return{
        "status": "healthy"
    }

@router.get("/metrics")
def metrics():
    return get_metrics()