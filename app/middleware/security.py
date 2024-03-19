from typing import Tuple, Optional

from app.core.constants import ExcludeAuthMiddlewarePath
from app.db import db
from app.helpers.logger import logger
from app.helpers.exceptions import UnauthorizedClientRequest
from app.v1.auth import AuthRepository, AuthService
from app.v1.auth.const import LoginErrorMsg
from app.v1.auth.dto import TokenData
from app.v1.session import SessionRepository, SessionService


class SecurityMiddleware:
    def __init__(self) -> None:
        self.auth_service = AuthService(
            auth_repo=AuthRepository(db),
            sess_service=SessionService(SessionRepository(db)),
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
            ExcludeAuthMiddlewarePath.REGISTER.value in path
            or ExcludeAuthMiddlewarePath.LOGIN.value in path
            or ExcludeAuthMiddlewarePath.DOCS.value in path
            or ExcludeAuthMiddlewarePath.HEALTH_CHECK.value in path
            or ExcludeAuthMiddlewarePath.METRICS.value in path
        ):
            return sub_id, sub, session_id

        if not auth_header:
            logger.debug("No authorization header provided")
            raise UnauthorizedClientRequest(LoginErrorMsg.UNAUTHORIZED_USER)

        token = auth_header.replace("Bearer ", "")
        token_detail = self.check_jwt_token(token)
        self.check_session(token_detail)

        sub_id = token_detail.sub_id
        sub = token_detail.sub
        session_id = token_detail.session

        return sub_id, sub, session_id

    def check_jwt_token(self, token: str) -> TokenData:
        """
        Parse JWT token from client request.
        """
        return self.auth_service.verify_token(token=token)

    def check_session(self, token: TokenData) -> None:
        """
        Ensure session is exist and active.

        Args:
            - token
        """
        self.auth_service.validate_session(token)
