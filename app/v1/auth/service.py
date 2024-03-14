# responsible for cover business logic, core functionality of the application.
# reusable, abstract from interface and focus on underlying business logic.
# might be dependent to controller according to use cases.
from __future__ import annotations

import datetime as dt
from datetime import datetime, timedelta
from typing import List, Optional, Union

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from passlib.context import CryptContext

from app.core.settings import Settings
from app.db import Session
from app.db.models.user_mgmt import Sessions, Users
from app.helpers.exceptions import (
    credentials_exception,
    internal_exception,
    registration_exception,
    session_expired_exception,
    uname_pwd_exception,
)
from app.helpers.logger import logger
from app.v1.auth.dao import SessionDAO, UserDAO
from app.v1.auth.dto import (
    LoginRequestDTO,
    LoginResponseDTO,
    RegisterRequestDTO,
    RegisterResponseDTO,
    TokenDataDTO,
)


class AuthService:
    def __init__(self, session_service: SessionService, user_dao: UserDAO):
        self.oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        self.session_service = session_service
        self.user_dao = user_dao

    def register_new_user(
        self, new_user: RegisterRequestDTO, db_sess: Session
    ) -> RegisterResponseDTO:
        """
        Register new user.

        Args:
            - new_user: user object coming from client.
            - db_sess: database session.

        Return:
            - user_obj: user object created from new_user param.
        """
        existing_user = self.user_dao.get_user_by_username(
            new_user.username, db_sess
        )
        if existing_user:
            raise registration_exception

        hash_pass = self.create_hash_password(new_user.password)
        new_user.password = hash_pass

        user_db = self.user_dao.create_new_user(new_user, db_sess)
        if not user_db:
            raise internal_exception

        return RegisterResponseDTO(username=str(user_db.username))

    def login_user(
        self, user: LoginRequestDTO, db_sess: Session
    ) -> LoginResponseDTO:
        """
        Ensure user credentials are valid and return bearer token.

        Args:
            - user
            - db_sess

        Return:
            - LoginResponseDTO
        """
        user_db = self.authenticate_user(user, db_sess)
        if not user_db:
            raise uname_pwd_exception

        session_id = self.session_service.create_session(
            user.username, db_sess
        )
        if session_id is None:
            raise internal_exception

        token_data = TokenDataDTO(
            sub=str(user_db.username),
            sub_id=str(user_db.id_hash),
            session=session_id,
        )
        access_token = self.create_access_token(data=token_data)
        return LoginResponseDTO(access_token=access_token)

    def logout_user(
        self, username: str, session: str, db_sess: Session
    ) -> None:
        """
        Close session for passed username and session.

        Args:
            - username
            - session: session id
            - db_sess
        """
        user_session = self.session_service.get_user_session(
            session=session, username=username, db_sess=db_sess
        )
        if not user_session:
            return

        if self.session_service.blacklist_session(
            sessions=user_session, db_sess=db_sess
        ):
            return

        raise internal_exception

    def create_access_token(
        self,
        data: TokenDataDTO,
        exp_delta: timedelta = timedelta(minutes=Settings.TOKEN_EXP_MINUTES),
    ) -> str:
        """
        Create JWT token.

        Args:
            - data: jwt information details
            - exp_delta: jwt expiry time limit

        Return:
            - encoded_jwt
        """
        expiry = datetime.now(dt.UTC) + exp_delta
        data.exp = expiry
        encoded_jwt = jwt.encode(
            claims=dict(data), key=Settings.SECRET_KEY, algorithm=Settings.ALGO
        )
        return encoded_jwt

    def verify_token(self, token: str) -> TokenDataDTO:
        """
        Parse access token detail.

        Args:
            - token: token from client

        Return:
            - token_data
        """
        try:
            payload = jwt.decode(
                token=token, key=Settings.SECRET_KEY, algorithms=Settings.ALGO
            )
        except ExpiredSignatureError as exc:
            # no need to manually check for expiry time
            # this exception means the token already expires
            logger.debug(f"JWT token ({token}) has expired: {exc}")
            raise session_expired_exception
        except JWTError:
            logger.debug(f"JWT token ({token}) is invalid")
            raise credentials_exception
        except Exception as exc:
            logger.debug(f"Fail to decode JWT token ({token}): {exc}")
            raise internal_exception

        token_data = TokenDataDTO(**payload)
        return token_data

    def validate_session(
        self, token: TokenDataDTO, db_sess: Session
    ) -> Sessions:
        """
        Check whether session is exist in db or not.

        Args:
            - token
            - by: check session either by "id" or "username"
            - db_sess

        Return:
            - session_obj
        """
        session_obj = self.session_service.get_user_session(
            session=token.session, username=token.sub, db_sess=db_sess
        )
        if not session_obj:
            logger.debug(f"Session ({token.session} | {token.sub}) not exist")
            raise credentials_exception

        if not session_obj.is_active:
            logger.debug(f"Session ({token.session} | {token.sub}) logged out")
            raise credentials_exception

        return session_obj

    def create_hash_password(self, password: str) -> str:
        """
        Create hash password.

        Args:
            - password: plain text password

        Return:
            - hash_password
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_pass: str, hashed_pass: str) -> bool:
        """
        Verify inputted password is as similar with hashed password.

        Args:
            - plain_pass: password coming from client request
            - hashed_pass: password coming from database

        Return:
            - True or False
        """
        return self.pwd_context.verify(plain_pass, hashed_pass)

    def authenticate_user(
        self, user: LoginRequestDTO, db_sess: Session
    ) -> Optional[Users]:
        """
        Authenticate user by its credentials.

        What we authenticate:

            1. ensure username is registered
            2. ensure password is valid

        Args:
            - username: username coming from client.
            - password: hashed password coming from client.
            - db_sess: database session.

        Return:
            - user: user object that fits to given username and password.
        """
        user_db = self.user_dao.get_user_by_username(user.username, db_sess)
        if not user_db:
            logger.debug(f"Wrong username ({user})")
            return None

        if not self.verify_password(user.password, str(user_db.pass_hash)):
            logger.debug(f"Wrong password ({user})")
            return None

        return user_db


class SessionService:
    def __init__(self, session_dao: SessionDAO):
        self.session_dao = session_dao

    def create_session(self, username: str, db_sess: Session) -> str | None:
        """
        Create new session after login.

        Args:
            - user_id
            - token: containing session_token and expiry time,
                data is coming from AuthService

        Return:
            - session_id
        """
        user_sessions = self.session_dao.get_session_by_username(
            username=username, db_sess=db_sess
        )
        if user_sessions:
            # set all as inactive to maintain only one session per user
            logger.debug(f"{username} has an active session")
            if not self.blacklist_session(user_sessions, db_sess):
                raise internal_exception

        session = self.session_dao.create_new_session(username, db_sess)
        session_id = str(session.id) if session else None
        return session_id

    def blacklist_session(
        self, sessions: Union[List[Sessions], Sessions], db_sess: Session
    ) -> bool:
        """
        Set sessions to inactive.

        Args:
            - sessions
            - db_sess

        Return:
            boolean
        """
        return self.session_dao.set_as_inactive(
            session_objs=sessions, db_sess=db_sess
        )

    def get_user_session(
        self, session: str, username: str, db_sess: Session
    ) -> Optional[Sessions]:
        """
        Get session from passed session id and username.

        Args:
            - session
            - username
            - db_sess

        Return:
            - session_obj
        """
        session_obj = self.session_dao.get_session(
            id=session, username=username, db_sess=db_sess
        )
        if not session_obj:
            logger.debug(f"Session {session} not found")

        return session_obj
