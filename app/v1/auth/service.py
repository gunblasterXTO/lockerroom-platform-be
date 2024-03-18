from __future__ import annotations

import datetime as dt
from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from passlib.context import CryptContext
from sqlalchemy.engine.row import Row

from app.core.settings import Settings
from app.helpers.exceptions import (
    BadClientReqeust,
    ConflictClientRequest,
    InternalServerError,
    UnauthorizedClientRequest,
)
from app.helpers.logger import logger
from app.v1.auth.const import AuthRule, LoginErrorMsg, RegisterErrorMsg
from app.v1.auth.repository import AuthRepository
from app.v1.auth.dto import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    TokenData,
)
from app.v1.session import SessionService


class AuthService:
    def __init__(
        self, auth_repo: AuthRepository, sess_service: SessionService
    ) -> None:
        self.oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        self.auth_repo = auth_repo
        self.sess_service = sess_service

    def register(self, request: RegisterRequest) -> RegisterResponse:
        """Register new user"""
        self.__validate_username(request.username)
        if self.auth_repo.get_user_with_similar_username(request.username):
            logger.error(
                f"{RegisterErrorMsg.REGISTERED_USERNAME}: {request.username}"
            )
            raise ConflictClientRequest(RegisterErrorMsg.REGISTERED_USERNAME)

        hashed_pass = self.__create_hash_password(request.password)
        request.password = hashed_pass
        new_user = self.auth_repo.create_new_user(request)
        if not new_user:
            raise InternalServerError()

        return RegisterResponse(
            username=str(new_user.username), email=str(new_user.email)
        )

    def __validate_username(self, username: str) -> None:
        if not username:
            logger.error(f"{RegisterErrorMsg.EMPTY_USERNAME}: {username}")
            raise BadClientReqeust(RegisterErrorMsg.EMPTY_USERNAME)

        if not self.__is_containing_alphabet(username):
            logger.error(
                f"{RegisterErrorMsg.NO_ALPHABET_USERNAME}: {username}"
            )
            raise BadClientReqeust(RegisterErrorMsg.NO_ALPHABET_USERNAME)

        if len(username) > AuthRule.MAX_USERNAME_CHAR:
            logger.error(f"{RegisterErrorMsg.MAX_CHAR_USENAME}: {username}")
            raise BadClientReqeust(RegisterErrorMsg.MAX_CHAR_USENAME)

    def __is_containing_alphabet(self, username: str) -> bool:
        """Check username whether it contains alphabet or not"""
        is_contain = False
        for char in username:
            if char.isalpha():
                is_contain = True
                break

        return is_contain

    def __create_hash_password(self, password: str) -> str:
        """Create hash password"""
        return self.pwd_context.hash(password)

    def login(self, request: LoginRequest) -> LoginResponse:
        """Login user"""
        user = self.__validate_creds(request.username, request.password)
        session_id = self.sess_service.create_session(user.hash_id)
        token_data = TokenData(
            sub=str(user.username),
            sub_id=str(user.hash_id),
            session=session_id,
        )

        return LoginResponse(
            access_token=self.__create_access_token(token_data),
            token_type="bearer",
            expires_in=AuthRule.TOKEN_EXPIRES,
        )

    def __validate_creds(self, username: str, password: str) -> Row:
        """
        Validate whether username exist or password correct
        or session is occupied.
        Return user object if pass all validations.
        """
        user = self.auth_repo.get_user_by_username(username)
        if not user:
            raise UnauthorizedClientRequest(LoginErrorMsg.UNAUTHORIZED_USER)

        if not self.__verify_password(password, user.pass_hash):
            raise UnauthorizedClientRequest(LoginErrorMsg.UNAUTHORIZED_USER)

        if self.sess_service.get_user_session(user_id=user.hash_id):
            raise UnauthorizedClientRequest(LoginErrorMsg.OCCUPIED_SESSION)

        return user

    def __verify_password(self, plain_pass: str, hashed_pass: str) -> bool:
        """Verify whether given password and password in db is same"""
        return self.pwd_context.verify(plain_pass, hashed_pass)

    def __create_access_token(
        self,
        data: TokenData,
        exp_delta: timedelta = timedelta(minutes=AuthRule.TOKEN_EXPIRES),
    ) -> str:
        """Create JWT token"""
        expiry = datetime.now(dt.UTC) + exp_delta
        data.exp = expiry
        encoded_jwt = jwt.encode(
            claims=dict(data), key=Settings.SECRET_KEY, algorithm=Settings.ALGO
        )
        return encoded_jwt

    def logout(self, session_id: str) -> None:
        """Logout user with active session"""
        if not self.sess_service.get_user_session(sess_id=session_id):
            return

        self.sess_service.blacklist_session(session_id)
        return

    def verify_token(self, token: str) -> TokenData:
        """Parse access token detail"""
        try:
            payload = jwt.decode(
                token=token, key=Settings.SECRET_KEY, algorithms=Settings.ALGO
            )
        except ExpiredSignatureError as exc:
            # no need to manually check for expiry time
            # this exception means the token already expires
            logger.debug(f"JWT token ({token}) has expired: {exc}")
            raise UnauthorizedClientRequest(LoginErrorMsg.EXPIRED_SESSION)
        except JWTError:
            logger.debug(f"JWT token ({token}) is invalid")
            raise UnauthorizedClientRequest(LoginErrorMsg.INVALID_CREDS)
        except Exception as exc:
            logger.debug(f"Fail to decode JWT token ({token}): {exc}")
            raise InternalServerError()

        token_data = TokenData(**payload)
        return token_data

    def validate_session(self, token: TokenData) -> Row:
        """Check whether session is exist in db"""
        session = self.sess_service.get_user_session(sess_id=token.session)
        if not session:
            logger.debug(f"Session ({token.session} | {token.sub}) not exist")
            raise UnauthorizedClientRequest(LoginErrorMsg.INVALID_CREDS)

        return session

    def forgot_password(self) -> None: ...
