"""
API v1 router configuration
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users
from app.api.v1 import vehicles, predictions, maintenance, reports

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/api/v1")
api_router.include_router(users.router, prefix="/api/v1")
api_router.include_router(vehicles.router, prefix="/api/v1")
api_router.include_router(predictions.router, prefix="/api/v1")
api_router.include_router(maintenance.router, prefix="/api/v1")
api_router.include_router(reports.router, prefix="/api/v1")