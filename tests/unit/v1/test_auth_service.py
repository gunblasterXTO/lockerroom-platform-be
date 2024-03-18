import pytest
from sqlalchemy import text

from app.db import db
from app.helpers.exceptions import (
    BadClientReqeust,
    ConflictClientRequest,
    UnauthorizedClientRequest,
)
from app.v1.auth.dto import (
    LoginRequest,
    RegisterRequest,
)
from app.v1.auth import AuthRepository, AuthService
from app.v1.session import SessionRepository, SessionService
from tests.unit.data_auth_service import (
    TEST_LOGIN_FAIL_CREDS,
    TEST_LOGIN_FAIL_SESSION,
    TEST_LOGIN_SUCCESS,
    TEST_REGISTER_FAIL_USERNAME_DUPS,
    TEST_REGISTER_FAIL_USERNAME_REQ,
    TEST_REGISTER_SUCCESS,
)


class TestAuthService:
    @pytest.fixture
    def gen_auth_service(self):
        yield AuthService(
            auth_repo=AuthRepository(db),
            sess_service=SessionService(SessionRepository(db)),
        )

    @pytest.mark.parametrize(
        "username, email, password, result", TEST_REGISTER_SUCCESS
    )  # noqa
    def test_register_success(
        self, gen_auth_service, username, email, password, result
    ):  # noqa
        req = RegisterRequest(**{
            "username": username,
            "email": email,
            "password": password,
        })
        register_response = gen_auth_service.register(req)
        assert isinstance(register_response, result)
        assert register_response.username == username
        assert register_response.email == email

        with db.engine.connect() as db_conn:
            query = text(
                """
                DELETE FROM platform_users
                WHERE username = :username
            """
            )
            db_conn.execute(query, {"username": username})
            db_conn.commit()

    @pytest.mark.parametrize(
        "username, email, password, result", TEST_REGISTER_FAIL_USERNAME_REQ
    )  # noqa
    def test_register_fail_username_req(
        self, gen_auth_service, username, email, password, result
    ):  # noqa
        req = RegisterRequest(**{
            "username": username,
            "email": email,
            "password": password,
        })
        with pytest.raises(BadClientReqeust) as exc_info:
            gen_auth_service.register(req)
        assert str(exc_info.value) == result

    @pytest.mark.parametrize(
        "username, email, password, result", TEST_REGISTER_FAIL_USERNAME_DUPS
    )  # noqa
    def test_register_fail_username_dups(
        self, gen_auth_service, username, email, password, result
    ):  # noqa
        req = RegisterRequest(**{
            "username": username,
            "email": email,
            "password": password,
        })
        with pytest.raises(ConflictClientRequest) as exc_info:
            gen_auth_service.register(req)
        assert str(exc_info.value) == result

    # TODO: need to delete session after success login
    @pytest.mark.skip
    @pytest.mark.parametrize(
        "username, password, token_type, expires_in, obj_class",
        TEST_LOGIN_SUCCESS,
    )  # noqa
    def test_login_success(
        self,
        gen_auth_service,
        username,
        password,
        token_type,
        expires_in,
        obj_class,
    ):  # noqa
        request = LoginRequest(**{"username": username, "password": password})
        login_response = gen_auth_service.login(request)

        assert isinstance(login_response, obj_class)
        assert isinstance(login_response.access_token, str)
        assert isinstance(login_response.token_type, str)
        assert isinstance(login_response.expires_in, int)
        assert login_response.access_token != ""
        assert login_response.token_type == token_type
        assert login_response.expires_in == expires_in

    @pytest.mark.parametrize(
        "username, password, result", TEST_LOGIN_FAIL_CREDS
    )  # noqa
    def test_login_fail_credentials(
        self, gen_auth_service, username, password, result
    ):
        request = LoginRequest(**{"username": username, "password": password})
        with pytest.raises(UnauthorizedClientRequest) as exc_info:
            gen_auth_service.login(request)

        assert str(exc_info.value) == result

    @pytest.mark.parametrize(
        "username, password, result", TEST_LOGIN_FAIL_SESSION
    )  # noqa
    def test_login_fail_session(
        self, gen_auth_service, username, password, result
    ):
        request = LoginRequest(**{"username": username, "password": password})
        gen_auth_service.login(request)
        with pytest.raises(UnauthorizedClientRequest) as exc_info:
            gen_auth_service.login(request)

        assert str(exc_info.value) == result
