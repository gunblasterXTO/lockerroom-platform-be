from typing import Tuple, Optional

from app.core.constants import ExcludeAuthMiddlewarePath
from app.db import db
from app.helpers.logger import logger
from app.helpers.exceptions import credentials_exception
from app.v1.auth.service import AuthService, SessionService
from app.v1.auth.dao import SessionDAO, UserDAO
from app.v1.auth.dto import TokenDataDTO


class SecurityMiddleware:
    def __init__(self) -> None:
        self.auth_service = AuthService(
            session_service=SessionService(SessionDAO()), user_dao=UserDAO()
        )

    def authenticate_user(
        self, auth_header: Optional[str], path: str
    ) -> Tuple[str, str, str]:
        """
        Ensure user is a valid user that has access to other backend services.

        Args:
            - auth_header: Auhtorization header from client request
            - path: full url path

        Return:
            - is_authenticated: True if allow to proceed
            - creds: contains user id, username, and session id
        """
        sub_id, sub, session_id = "", "", ""
        if (
            path == "/"
            or ExcludeAuthMiddlewarePath.REGISTER.value in path
            or ExcludeAuthMiddlewarePath.LOGIN.value in path
            or ExcludeAuthMiddlewarePath.DOCS.value in path
        ):
            return sub_id, sub, session_id

        if not auth_header:
            logger.debug("No authorization header provided")
            raise credentials_exception

        token = auth_header.replace("Bearer ", "")
        token_detail = self.check_jwt_token(token)
        self.check_session(token_detail)

        sub_id = token_detail.sub_id
        sub = token_detail.sub
        session_id = token_detail.session

        return sub_id, sub, session_id

    def check_jwt_token(self, token: str) -> TokenDataDTO:
        """
        Parse JWT token from client request.

        Args:
            - token

        Return:
            - token_detail
        """
        return self.auth_service.verify_token(token=token)

    def check_session(self, token: TokenDataDTO) -> None:
        """
        Ensure session is exist and active.

        Args:
            - token
        """
        with db.session() as db_sess:
            self.auth_service.validate_session(token=token, db_sess=db_sess)
