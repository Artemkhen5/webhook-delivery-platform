from fastapi import APIRouter
from wdp.api.v1.endpoints.endpoint_routes import router as endpoint_router

router = APIRouter(prefix="/api/v1")

router.include_router(
    endpoint_router,
    prefix="/endpoints",
    tags=["endpoints"]
)
