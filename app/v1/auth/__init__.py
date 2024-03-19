from fastapi import APIRouter

from .repository import AuthRepository  # noqa
from .service import AuthService  # noqa
from .view import AuthViews

auth_views = AuthViews()
auth_r = APIRouter(prefix="/auth", tags=["Auth"])

auth_r.add_api_route("/login", endpoint=auth_views.login, methods=["POST"])
auth_r.add_api_route(
    "/register", endpoint=auth_views.registration, methods=["POST"]
)  # noqa
auth_r.add_api_route("/logout", endpoint=auth_views.logout, methods=["POST"])
