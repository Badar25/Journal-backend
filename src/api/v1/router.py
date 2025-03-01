from fastapi import APIRouter
from .endpoints import journals

router = APIRouter(prefix="/api/v1")
router.include_router(journals.router, prefix="/journals", tags=["journals"])