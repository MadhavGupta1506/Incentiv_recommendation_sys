from fastapi import APIRouter

from app.api.companies import router as companies_router
from app.api.demands import router as demands_router
from app.api.preferences import router as preferences_router
from app.api.recommendations import router as recommendations_router
from app.api.supplies import router as supplies_router


router = APIRouter()
router.include_router(companies_router)
router.include_router(supplies_router)
router.include_router(demands_router)
router.include_router(preferences_router)
router.include_router(recommendations_router)
