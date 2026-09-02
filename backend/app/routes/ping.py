from fastapi import APIRouter

router = APIRouter(prefix="/ping", tags=["ping"])

@router.get("/", include_in_schema=False)
def ping():
    return {"status": "ok"}
