from fastapi import FastAPI, APIRouter
from app.routers.v1 import user
from app.routers.v1 import ai

api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(ai.openapi, prefix="/ai", tags=["ai"])

