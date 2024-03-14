from fastapi import APIRouter

from .view import AuthViews

auth_views = AuthViews()
auth_r = APIRouter(prefix="/auth", tags=["Auth"])

auth_r.add_api_route(
    path="/login", endpoint=auth_views.login, methods=["POST"]
)
auth_r.add_api_route(
    path="/register", endpoint=auth_views.registration, methods=["POST"]
)
auth_r.add_api_route(
    path="/logout", endpoint=auth_views.logout, methods=["POST"]
)
