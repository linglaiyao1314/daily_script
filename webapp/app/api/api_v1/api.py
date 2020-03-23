from fastapi import APIRouter

from app.api.api_v1.endpoints import login, users, data_source
api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(data_source.router, prefix="/datasources", tags=["datasources"])
