from fastapi import APIRouter
from services.metrics import get_metrics

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
)

@router.get("/")
def metrics():
    return get_metrics()