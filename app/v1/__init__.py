from fastapi import APIRouter

from app.v1.auth import auth_r

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(auth_r)
