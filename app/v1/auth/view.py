# responsible to handle HTTP request and produces correspond response
from fastapi import Depends, Request, status
from fastapi.responses import JSONResponse, Response

from app.db import db, Session
from app.helpers.logger import logger
from app.helpers.response import PostSuccessResponse
from app.v1.auth.dao import SessionDAO, UserDAO
from app.v1.auth.dto import LoginRequestDTO, RegisterRequestDTO
from app.v1.auth.service import AuthService, SessionService

session_service = SessionService(session_dao=SessionDAO())
auth_service = AuthService(session_service=session_service, user_dao=UserDAO())


class AuthViews:
    async def registration(
        self,
        user: RegisterRequestDTO,
        db_sess: Session = Depends(db.get_session),
    ) -> JSONResponse:
        """
        Register new user if related information haven't been in the db.
        """
        logger.debug(f"Registering new {user}...")
        new_user = auth_service.register_new_user(user, db_sess).model_dump()
        return JSONResponse(
            content=PostSuccessResponse(data=new_user).model_dump(),
            status_code=status.HTTP_201_CREATED,
        )

    async def login(
        self, user: LoginRequestDTO, db_sess: Session = Depends(db.get_session)
    ) -> JSONResponse:
        """
        Login user if the related information is correct.
        """
        logger.debug(f"Logging in {user}...")
        login_creds = auth_service.login_user(user, db_sess).model_dump()
        return JSONResponse(
            content=PostSuccessResponse(data=login_creds).model_dump(),
            status_code=status.HTTP_200_OK,
        )

    async def logout(
        self, request: Request, db_sess: Session = Depends(db.get_session)
    ) -> Response:
        """
        Logout user, blacklist session id.
        """
        username = request.state.username
        session_id = request.state.session_id
        logger.debug(f"Logging out {username} - {session_id}...")
        auth_service.logout_user(
            username=username, session=session_id, db_sess=db_sess
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
