import pytest
from sqlalchemy import text

from app.db import db
from app.v1.auth.dto import RegisterRequest
from app.v1.auth.repository import AuthRepository

from tests.unit.data_auth_repository import (
    CREATE_USER,
    FAIL_GET_USER_BY_USERNAME,
    SIMILAR_USERNAME,
    SUCCESS_GET_USER_BY_USERNAME,
)


class TestAuthRepository:
    @pytest.fixture
    def gen_auth_repo(self):
        yield AuthRepository(db)

    @pytest.mark.parametrize("username, result", SIMILAR_USERNAME)
    def test_get_user_similar_username(self, gen_auth_repo, username, result):
        user = gen_auth_repo.get_user_with_similar_username(username)
        assert result == user

    @pytest.mark.parametrize(
        "username, email, hashed_pass, result", CREATE_USER
    )
    def test_create_user(
        self, gen_auth_repo, username, email, hashed_pass, result
    ):
        request = RegisterRequest(**{
            "username": username,
            "email": email,
            "password": hashed_pass,
        })
        new_user = gen_auth_repo.create_new_user(request)

        assert isinstance(new_user, result)
        assert new_user.username == username
        assert new_user.email == email

        query = text(
            """
            DELETE FROM platform_users
            WHERE id = :user_id
        """
        )
        with db.engine.connect() as db_conn:
            db_conn.execute(query, {"user_id": new_user.id})
            db_conn.commit()

    @pytest.mark.parametrize(
        "username, email, user_id, user_hash_id", SUCCESS_GET_USER_BY_USERNAME
    )
    def test_success_get_user_by_username(
        self, gen_auth_repo, username, email, user_id, user_hash_id
    ):
        user = gen_auth_repo.get_user_by_username(username)

        assert user.username == username
        assert user.email == email
        assert user.id == user_id
        assert user.hash_id == user_hash_id

    @pytest.mark.parametrize("username, result", FAIL_GET_USER_BY_USERNAME)
    def test_fail_get_user_by_username(self, gen_auth_repo, username, result):
        user = gen_auth_repo.get_user_by_username(username)

        assert user == result
