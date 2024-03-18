from fastapi import Request, status
from fastapi.responses import JSONResponse, Response

from app.db import db
from app.helpers.response import PostSuccessResponse
from app.v1.auth.repository import AuthRepository
from app.v1.auth.dto import LoginRequest, RegisterRequest
from app.v1.auth.service import AuthService
from app.v1.session import SessionRepository, SessionService

auth_service = AuthService(
    auth_repo=AuthRepository(db),
    sess_service=SessionService(SessionRepository(db)),
)


class AuthViews:
    async def registration(self, user: RegisterRequest) -> JSONResponse:
        """
        Register new user if related information haven't been in the db.
        """
        new_user = auth_service.register(user).model_dump()
        return JSONResponse(
            content=PostSuccessResponse(data=new_user).model_dump(),
            status_code=status.HTTP_201_CREATED,
        )

    async def login(self, user: LoginRequest) -> JSONResponse:
        """
        Login user if the related information is correct.
        """
        login_creds = auth_service.login(user).model_dump()
        return JSONResponse(
            content=PostSuccessResponse(data=login_creds).model_dump(),
            status_code=status.HTTP_200_OK,
        )

    async def logout(
        self,
        request: Request,
    ) -> Response:
        """
        Logout user, blacklist session id.
        """
        session_id = request.state.session_id
        auth_service.logout(session_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
